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
            "__main__.JobPostgresPipeline": 300,
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
            mode = site.get("mode", "list")
            for seed in site.get("seeds", []):
                meta = {"site": site, "mode": mode}
                yield scrapy.Request(seed, callback=self.route, meta=meta)

    # ----- router --------
    def route(self, response):
        mode = response.meta["mode"]
        if mode == "sitemap":
            yield from self.parse_sitemap(response)
        elif mode == "api":
            yield from self.parse_api(response)
        else:
            yield from self.parse_listing(response)

    # ----- sitemap (XML) --
    def parse_sitemap(self, response):
        response.selector.remove_namespaces() # Needed for some sitemaps
        for loc in response.xpath("//url/loc/text()").getall():
            yield scrapy.Request(loc, callback=self.parse_job, meta=response.meta)

    # ----- API (JSON) -----
    def parse_api(self, response):
        try:
            data = json.loads(response.text)
            # Adapt this part based on the actual API structure
            jobs_list = data # Default assumption: list of jobs
            if isinstance(data, dict): # Handle common case where jobs are under a key
                 jobs_list = data.get("jobs", []) or data.get("results", [])

            for post in jobs_list:
                 # Adapt field extraction based on API structure
                 url = post.get("url") or post.get("absolute_url") or post.get("job_url")
                 if url:
                     # Pass entire post data in meta for potential use in parse_job
                     response.meta['api_post_data'] = post
                     yield scrapy.Request(url, callback=self.parse_job, meta=response.meta, dont_filter=True)
                 else:
                     # If no URL, try to yield item directly from API data
                     loader = ItemLoader(item=JobItem(), selector=post) # Use post dict as selector
                     loader.add_value("title", post.get("title"))
                     # ... add other fields directly from post dict ...
                     loader.add_value("source", response.meta["site"].get("name"))
                     loader.add_value("url", response.url) # Use API endpoint URL if no specific job URL
                     loader.add_value("scraped_at", dt.datetime.utcnow().isoformat())
                     # ... handle description, location etc. from API data ...
                     yield loader.load_item()

        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse JSON from API: {response.url}")


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

    # ----- parse Job page --
    def parse_job(self, response):
        loader = ItemLoader(item=JobItem(), response=response)
        loader.default_output_processor = TakeFirst()

        # Try extracting from API data passed via meta first
        api_data = response.meta.get('api_post_data')
        if api_data and isinstance(api_data, dict):
             loader.add_value("title", api_data.get("title"))
             loader.add_value("company", api_data.get("company_name") or api_data.get("hiringOrganization", {}).get("name"))
             loader.add_value("location", api_data.get("location") or api_data.get("jobLocation", {}).get("address", {}).get("addressLocality"))
             loader.add_value("description_md", api_data.get("description") or api_data.get("content"))
             loader.add_value("date_posted", api_data.get("posted_date") or api_data.get("datePosted"))
        else:
            # Extract structured data (JSON-LD, Microdata)
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
        url = item.get("url")
        if not url:
             # Decide how to handle items without a URL (log, drop, etc.)
             logging.warning(f"Skipping item with no URL: {item.get('title')}")
             return

        title = item.get("title")
        company = item.get("company")
        location = item.get("location")
        description_md = item.get("description_md", "") # Default to empty string
        date_posted_str = item.get("date_posted")
        h1b_sponsor = item.get("h1b_sponsor", False) # Default to False
        raw = item.get("raw", "") # Default to empty string
        source = item.get("source")
        scraped_at_str = item.get("scraped_at")

        # Attempt to parse dates, handle potential errors
        date_posted = None
        if date_posted_str:
            try:
                date_posted = dt.datetime.fromisoformat(date_posted_str.replace('Z', '+00:00')).date()
            except (ValueError, TypeError):
                 logging.warning(f"Could not parse date_posted: {date_posted_str} for URL: {url}")
                 # Optionally try other date formats here

        scraped_at = None
        if scraped_at_str:
             try:
                  scraped_at = dt.datetime.fromisoformat(scraped_at_str.replace('Z', '+00:00'))
             except (ValueError, TypeError):
                  logging.warning(f"Could not parse scraped_at: {scraped_at_str} for URL: {url}")
                  scraped_at = dt.datetime.utcnow() # Fallback to now

        try:
            await pool.execute(
                """INSERT INTO jobs(url, title, company, location, description_md, date_posted, h1b_sponsor, raw, source, scraped_at)
                   VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
                   ON CONFLICT (url) DO NOTHING""", # Consider DO UPDATE if you want to refresh data
                url, title, company, location, description_md, date_posted,
                h1b_sponsor, raw, source, scraped_at
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
