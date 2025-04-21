# job_crawler.py – High‑throughput Job Posting Crawler
"""
Run with:
    scrapy runspider job_crawler.py -a sites_file=sites.yml

Design goals
------------
* **Pluggable site catalogue** – pass YAML/TOML defining seed URLs & crawl mode (sitemap, listings, api)
* **Schema.org JobPosting first**  – parse <script type="application/ld+json"> OR microdata via `extruct`
* **Distributed‑ready** – leverages scrapy‑redis when REDIS_URL env var is set, enabling horizontal scale
* **ATS‑friendly normalisation** – maps arbitrary fields to internal canonical schema (see JobItem below)
* **H1B filter** – naïve Boolean from keyword list; replace with ML classifier later
* **Rotating proxies / UA pool** – optional; auto‑enabled when env vars provided
* **Output** – streams NDJSON to STDOUT **and** async‑inserts to Postgres (see `JobPostgresPipeline`)
"""

import json, logging, os, re, textwrap, yaml, datetime as dt
import asyncio
from urllib.parse import urljoin

import scrapy
from w3lib.html import remove_tags
import extruct
from itemloaders.processors import TakeFirst, MapCompose
from scrapy.loader import ItemLoader
from scrapy.exceptions import DropItem

# ---------------------------
# Canonical Job item
# ---------------------------
class JobItem(scrapy.Item):
    source          = scrapy.Field()
    url             = scrapy.Field()
    scraped_at      = scrapy.Field()
    title           = scrapy.Field()
    company         = scrapy.Field()
    location        = scrapy.Field()
    description_md  = scrapy.Field()
    date_posted     = scrapy.Field()
    h1b_sponsor     = scrapy.Field()
    raw             = scrapy.Field()

# ---------------------------
# Utility helpers
# ---------------------------
_H1B_KWS = ["h-1b", "h1b", "visa sponsorship", "will sponsor"]

def detect_h1b(text: str) -> bool:
    tex = text.lower()
    return any(kw in tex for kw in _H1B_KWS)

# ---------------------------
# Spider
# ---------------------------
class JobSpider(scrapy.Spider):
    name = "job_universal"
    custom_settings = {
        "ITEM_PIPELINES": {
            # Use the full Python path to the class within the project structure
            "app.crawler.job_crawler.JobPostgresPipeline": 300,
        },
        # Auto‑throttle keeps you polite
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 4.0,
        "DOWNLOAD_TIMEOUT": 30,
    }

    def __init__(self, sites_file="sites.yml", *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Look for sites.yml relative to the crawler script
        script_dir = os.path.dirname(__file__)
        sites_path = os.path.join(script_dir, sites_file)
        if not os.path.exists(sites_path):
             # Fallback to CWD if not found next to script
             sites_path = sites_file
        try:
            with open(sites_path, "r", encoding="utf-8") as fh:
                self.sites = yaml.safe_load(fh)
            logging.info("Loaded %d site definitions from %s", len(self.sites), sites_path)
        except FileNotFoundError:
             logging.error("Could not find sites file: %s", sites_path)
             self.sites = [] # Start with no sites if file not found
        except yaml.YAMLError as e:
             logging.error("Error parsing sites file %s: %s", sites_path, e)
             self.sites = []


    # ----- seeds ---------
    def start_requests(self):
        for site in self.sites:
            mode = site.get("mode", "listing").lower() # Default to listing
            source = site.get("source", "").lower()
            seeds = site.get("seeds", [])
            name = site.get("name", "Unknown Site")

            if not seeds:
                 self.logger.warning(f"No seeds found for site: {name}")
                 continue

            meta = {"site": site, "mode": mode, "source": source} # Pass source in meta

            for seed in seeds:
                request_url = seed # Default for listing/sitemap
                callback_func = self.route

                if mode == "api":
                    callback_func = self.parse_api # Go directly to API parser
                    if source == "greenhouse":
                        # Seed is the board token
                        request_url = f"https://boards-api.greenhouse.io/v1/boards/{seed}/jobs?content=true"
                    elif source == "lever":
                        # Seed is the site tag
                        request_url = f"https://api.lever.co/v0/postings/{seed}?mode=json"
                    else:
                        self.logger.warning(f"Unsupported API source '{source}' for site: {name}. Skipping seed: {seed}")
                        continue
                elif mode == "sitemap":
                     callback_func = self.parse_sitemap # Go directly to sitemap parser
                # else mode == "listing", use default seed URL and self.route

                self.logger.info(f"Yielding request for {name} ({source}/{mode}): {request_url}")
                yield scrapy.Request(request_url, callback=callback_func, meta=meta)


    # ----- router --------
    # This route function is now only needed if start_requests yields with callback=self.route (e.g., for listing mode)
    def route(self, response):
        mode = response.meta["mode"]
        # We should only arrive here for 'listing' mode now.
        # Sitemap and API modes have direct callbacks from start_requests.
        if mode == "listing":
             yield from self.parse_listing(response)
        else:
             self.logger.warning(f"Unexpected arrival at route() for mode: {mode}. URL: {response.url}")


    # ----- sitemap (XML) --
    def parse_sitemap(self, response):
        response.selector.remove_namespaces() # Needed for some sitemaps
        for loc in response.xpath("//url/loc/text()").getall():
            yield scrapy.Request(loc, callback=self.parse_job, meta=response.meta)

    # ----- API (JSON) -----
    # This method now directly parses the API response and yields JobItems
    def parse_api(self, response):
        source = response.meta.get("source")
        site_name = response.meta.get("site", {}).get("name", "Unknown Site")
        self.logger.info(f"Parsing API response for {site_name} ({source}) from {response.url}")

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse JSON from API response: {response.url}")
            return

        jobs_list = []
        if source == "greenhouse":
            if isinstance(data, dict) and 'jobs' in data:
                jobs_list = data['jobs']
            else:
                 self.logger.warning(f"Unexpected JSON structure for Greenhouse API: {response.url}")
                 return
        elif source == "lever":
            if isinstance(data, list):
                jobs_list = data
            else:
                self.logger.warning(f"Unexpected JSON structure for Lever API: {response.url}")
                return
        else:
            self.logger.warning(f"parse_api called for unhandled source: {source}")
            return

        self.logger.info(f"Found {len(jobs_list)} potential job items in API response for {site_name}")

        for job_item in jobs_list:
            if not isinstance(job_item, dict):
                 self.logger.warning(f"Skipping non-dict item in API response for {site_name}")
                 continue

            loader = ItemLoader(item=JobItem()) # No response needed for loader when using add_value

            # --- Field Extraction (adapt based on source) ---
            title = None
            url = None
            location = None
            description = None
            date_posted_str = None
            job_id = job_item.get('id', 'N/A') # For logging

            if source == "greenhouse":
                title = job_item.get('title')
                url = job_item.get('absolute_url')
                location = job_item.get('location', {}).get('name', 'N/A') if job_item.get('location') else 'N/A'
                description_html = job_item.get('content', '')
                description = remove_tags(description_html) # Use w3lib helper
                date_posted_str = job_item.get('updated_at')
            elif source == "lever":
                title = job_item.get('text')
                url = job_item.get('hostedUrl')
                location = job_item.get('categories', {}).get('location', 'N/A')
                description_html = job_item.get('description')
                description_plain = job_item.get('descriptionPlain', '')
                description = description_plain if description_plain else remove_tags(description_html)
                created_at_ms = job_item.get('createdAt')
                if created_at_ms:
                    try:
                        # Convert ms timestamp to ISO string for consistency
                        date_posted_dt = dt.datetime.fromtimestamp(created_at_ms / 1000, tz=dt.timezone.utc)
                        date_posted_str = date_posted_dt.isoformat()
                    except Exception as e:
                        self.logger.warning(f"Could not parse Lever createdAt timestamp {created_at_ms}: {e}")

            # --- Loading Item ---
            if not title or not url:
                 self.logger.warning(f"Skipping job item from {site_name} due to missing title or URL. ID: {job_id}")
                 continue

            loader.add_value("title", title)
            loader.add_value("url", url)
            loader.add_value("company", site_name) # Use the name from sites.yml
            loader.add_value("location", location)
            loader.add_value("description_md", description) # Store plain text description
            loader.add_value("date_posted", date_posted_str) # Store as string, pipeline handles parsing
            loader.add_value("source", site_name) # Or use source variable ('greenhouse'/'lever')? Using site name for now.
            loader.add_value("scraped_at", dt.datetime.utcnow().isoformat())
            loader.add_value("raw", json.dumps(job_item)[:5000]) # Store snippet of raw JSON

            # H1B detection
            loader.add_value("h1b_sponsor", detect_h1b(description or ""))

            yield loader.load_item()


    # ----- HTML listing ---
    # More robust link selectors
    LINK_SEL = [
        'a[href*="/jobs/"]::attr(href)',
        'a[href*="/careers/"]::attr(href)',
        'a[href*="/job/"]::attr(href)',
        'a[href*="/position/"]::attr(href)',
        'a[itemprop="url"]::attr(href)' # Schema.org microdata
    ]
    def parse_listing(self, response):
        found_links = set()
        for pattern in self.LINK_SEL:
            for href in response.css(pattern).getall():
                url = urljoin(response.url, href.strip())
                if url not in found_links:
                     found_links.add(url)
                     yield scrapy.Request(url, callback=self.parse_job, meta=response.meta)

        # follow pagination heuristically
        nexts = response.css("a[rel~=next]::attr(href), a:contains('Next')::attr(href), a[aria-label*='Next']::attr(href)").getall()
        for n in nexts[:3]: # Limit pagination depth per page
            yield response.follow(n, callback=self.parse_listing, meta=response.meta)

    # ----- parse Job page -- (Now only for HTML pages from listing/sitemap modes)
    def parse_job(self, response):
        loader = ItemLoader(item=JobItem(), response=response)
        loader.default_output_processor = TakeFirst()

        # Extract structured data (JSON-LD, Microdata)
        # No longer check response.meta['api_post_data'] here
        ld = extruct.extract(response.text, syntaxes=["json-ld", "microdata"])
        job = None
        for syntax in (ld.get("json-ld") or []) + (ld.get("microdata") or []):
            if isinstance(syntax, dict) and syntax.get("@type") == "JobPosting":
                job = syntax
                break
        if job:
            loader.add_value("title", job.get("title"))
            loader.add_value("company", job.get("hiringOrganization", {}).get("name"))
            loader.add_value("location", job.get("jobLocation", {}).get("address", {}).get("addressLocality"))
            loader.add_value("description_md", job.get("description"))
            loader.add_value("date_posted", job.get("datePosted"))
        else:  # fallback naive selectors if no structured data
            loader.add_css("title", "h1::text, .job-title::text") # Add common class selectors
            loader.add_css("company", "[class*='company']::text, .company-name::text")
            loader.add_css("location", "[class*='location']::text, .job-location::text")
            desc_html = response.css("article, .description, #job-description, .job-details").get() # Add common class selectors
            loader.add_value("description_md", remove_tags(desc_html or ""))

        raw_text = response.text[:15000]  # store small slice for audit
        loader.add_value("raw", raw_text)
        loader.add_value("source", response.meta["site"].get("name"))
        loader.add_value("url", response.url)
        loader.add_value("scraped_at", dt.datetime.utcnow().isoformat())

        # visa filter
        # Ensure description_md has a value before joining
        desc_values = loader.get_collected_values("description_md")
        joined_desc = " ".join(desc_values) if desc_values else ""
        loader.add_value("h1b_sponsor", detect_h1b(joined_desc))

        yield loader.load_item()

# ---------------------------
# Pipelines
# ---------------------------
class JobPostgresPipeline:
    """Async inserts; set PG_DSN env var like postgres://user:pass@host:5432/db"""
    def __init__(self):
        self.pool = None
        self.loop = None
        self.insert_tasks = []

    def open_spider(self, spider):
        import asyncio, asyncpg
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

        dsn = os.getenv("PG_DSN")
        if not dsn:
            spider.logger.warning("PG_DSN not set – skipping DB writes")
            return

        async def create_pool():
            try:
                self.pool = await asyncpg.create_pool(dsn, min_size=1, max_size=10) # Add pool size limits
                spider.logger.info("Asyncpg connection pool created.")
            except Exception as e:
                spider.logger.error(f"Failed to create asyncpg pool: {e}")
                self.pool = None # Ensure pool is None if creation fails

        self.loop.run_until_complete(create_pool())


    async def _insert(self, pool, item):
        # Ensure required fields exist, provide defaults if necessary
        url_val = item.get("url")
        url = url_val[0] if isinstance(url_val, list) and url_val else url_val # Handle potential list
        if not url or not isinstance(url, str):
            logging.warning(f"Skipping item due to missing or invalid URL: {item.get('title')}")
            return

        # Extract and handle potential lists for other fields
        title_val = item.get("title")
        title = title_val[0] if isinstance(title_val, list) and title_val else title_val

        company_val = item.get("company")
        company = company_val[0] if isinstance(company_val, list) and company_val else company_val

        location_val = item.get("location")
        location = location_val[0] if isinstance(location_val, list) and location_val else location_val

        # Correctly get description from 'description_md' item field
        description_val = item.get("description_md")
        description = (description_val[0] if isinstance(description_val, list) and description_val else description_val) or ""

        date_posted_val = item.get("date_posted")
        date_posted_str = date_posted_val[0] if isinstance(date_posted_val, list) and date_posted_val else date_posted_val

        h1b_sponsor_val = item.get("h1b_sponsor") # Corresponds to visa_sponsorship_available
        h1b_sponsor = (h1b_sponsor_val[0] if isinstance(h1b_sponsor_val, list) and h1b_sponsor_val else h1b_sponsor_val) or False

        raw_val = item.get("raw")
        raw = (raw_val[0] if isinstance(raw_val, list) and raw_val else raw_val) or ""

        source_val = item.get("source")
        source = source_val[0] if isinstance(source_val, list) and source_val else source_val

        scraped_at_val = item.get("scraped_at")
        scraped_at_str = scraped_at_val[0] if isinstance(scraped_at_val, list) and scraped_at_val else scraped_at_val

        # --- Date Parsing (Improved) ---
        date_posted = None
        if date_posted_str and isinstance(date_posted_str, str):
            try:
                if date_posted_str.endswith('Z'):
                     date_posted_str = date_posted_str[:-1] + '+00:00'
                # Attempt ISO format first
                date_posted = dt.datetime.fromisoformat(date_posted_str).date()
            except ValueError:
                 # Add fallback parsing attempts if needed (e.g., different formats)
                 logging.warning(f"Could not parse date_posted ISO string: '{date_posted_str}' for URL: {url}. Trying other formats...")
                 # Example fallback: try: date_posted = dt.datetime.strptime(date_posted_str, '%Y-%m-%d').date() etc.
                 pass # Keep date_posted = None if all parsing fails
        elif date_posted_str:
             logging.warning(f"date_posted value is not a string: {date_posted_str} for URL: {url}")

        scraped_at = None
        if scraped_at_str and isinstance(scraped_at_str, str):
             try:
                  if scraped_at_str.endswith('Z'):
                       scraped_at_str = scraped_at_str[:-1] + '+00:00'
                  scraped_at = dt.datetime.fromisoformat(scraped_at_str)
             except ValueError:
                  logging.warning(f"Could not parse scraped_at ISO string: '{scraped_at_str}' for URL: {url}")
                  scraped_at = dt.datetime.now(dt.timezone.utc) # Fallback to now UTC
        else:
             # Always set scraped_at, fallback to now if missing/invalid
             if scraped_at_str:
                  logging.warning(f"scraped_at value is not a string: {scraped_at_str} for URL: {url}")
             scraped_at = dt.datetime.now(dt.timezone.utc)

        # --- Database Insertion ---
        try:
            # Ensure column names in INSERT match models/job.py exactly
            # Correct columns: url, title, company, location, description, date_posted, visa_sponsorship_available, source, created_at, updated_at
            await pool.execute(
                 # Removed 'raw' column from INSERT statement
                """INSERT INTO jobs(url, title, company, location, description, date_posted, visa_sponsorship_available, source, created_at, updated_at)
                   VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                   ON CONFLICT (url) DO NOTHING""",
                 # Removed 'raw' parameter from the list
                url,                          # $1
                title,                        # $2
                company,                      # $3
                location,                     # $4
                description,                  # $5
                date_posted,                  # $6
                h1b_sponsor,                  # $7
                source,                       # $8
                scraped_at,                   # $9
                scraped_at                    # $10
            )
            logging.debug(f"Inserted/Skipped job: {url}")
        except Exception as e:
            logging.error(f"Error inserting job {url}: {e}")


    def process_item(self, item, spider):
        if self.pool:
            # Schedule the insertion task
            task = self.loop.create_task(self._insert(self.pool, item))
            self.insert_tasks.append(task)
        else:
             spider.logger.warning("No DB pool - skipping DB write for item.")

        # Optionally print JSON to stdout (can be disabled for production)
        # print(json.dumps(dict(item)))
        return item # Must return item for subsequent pipelines

    async def _close_pool(self):
         if self.pool:
              await self.pool.close()
              self.pool = None
              logging.info("Asyncpg connection pool closed.")

    def close_spider(self, spider):
         # Wait for all pending insertion tasks to complete
         if self.insert_tasks:
              self.loop.run_until_complete(asyncio.gather(*self.insert_tasks))
              self.insert_tasks = [] # Clear the list

         # Close the connection pool
         if self.pool:
              self.loop.run_until_complete(self._close_pool())
         # Close the event loop if it was created by this pipeline
         # Note: Be careful if the loop is shared with other parts of the application
         # if hasattr(self, 'loop') and self.loop.is_running():
         #      self.loop.close()


# ---------------------------
# Settings overrides when used as a stand‑alone file
# ---------------------------
if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    # Use Scrapy settings if available, otherwise provide defaults
    settings = get_project_settings()
    settings.set("LOG_LEVEL", "INFO")
    settings.set("USER_AGENT", "JobCrawlerBot/1.0 (+https://yourdomain.com/bot)") # Replace with actual domain
    # Add pipeline to settings if running standalone
    settings.set("ITEM_PIPELINES", {
        '__main__.JobPostgresPipeline': 1,
    })

    process = CrawlerProcess(settings)

    # Allow passing sites_file via command line when run directly
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--sites_file", default="sites.yml", help="Path to the sites configuration file")
    args = parser.parse_args()

    process.crawl(JobSpider, sites_file=args.sites_file)
    process.start()
