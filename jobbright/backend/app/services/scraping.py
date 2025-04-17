import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin
from datetime import datetime, timedelta
# from playwright.sync_api import sync_playwright # If needed for JS-heavy sites
from typing import List

from .. import schemas

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Constants ---
INDEED_BASE_URL = "https://www.indeed.com"

# --- Helper Functions ---
def parse_relative_date(date_str: str) -> datetime | None:
    """Rudimentary parser for relative dates like 'today', 'X days ago'."""
    date_str = date_str.lower().strip()
    try:
        if "today" in date_str or "just posted" in date_str:
            return datetime.now()
        elif "days ago" in date_str:
            days = int(date_str.split()[0])
            return datetime.now() - timedelta(days=days)
        # Add more cases as needed (e.g., hours ago, yesterday)
    except Exception as e:
        logger.warning(f"Could not parse relative date '{date_str}': {e}")
    return None

# --- Scraper Functions ---

# Placeholder function - replace with actual scraping logic per site
def scrape_indeed(query: str, location: str, pages: int = 1) -> List[schemas.JobCreate]:
    logger.info(f"Starting Indeed scrape for query='{query}', location='{location}', pages={pages}")
    jobs: List[schemas.JobCreate] = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for page in range(pages):
        start_index = page * 10 # Indeed pagination often uses 'start=' parameter
        search_url = f"{INDEED_BASE_URL}/jobs?q={query}&l={location}&start={start_index}"
        logger.info(f"Scraping URL: {search_url}")

        try:
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {search_url}: {e}")
            continue # Skip this page if request fails

        soup = BeautifulSoup(response.text, 'html.parser')

        # --- Selector Logic (Highly dependent on Indeed's current HTML structure) ---
        # This targets the main job results container found via browser inspection
        # Often a 'div' with an id like 'mosaic-provider-jobcards' or similar
        job_results_container = soup.find('div', id='mosaic-provider-jobcards')
        if not job_results_container:
             # Fallback: Sometimes results are within <ul> or other structures
            job_results_container = soup.find('ul', class_='jobsearch-ResultsList') # Example fallback class

        if not job_results_container:
            logger.warning(f"Could not find job results container on page {page+1}. Structure might have changed.")
            continue

        # Find individual job cards within the container. This often involves 'a' tags with specific classes or attributes.
        # We look for 'a' tags that seem to be direct links to job details.
        job_cards = job_results_container.find_all('a', class_=lambda x: x and 'tapItem' in x, recursive=True) # Example based on observed classes

        if not job_cards:
             logger.warning(f"Could not find individual job card links on page {page+1}. Selectors might need update.")
             continue


        logger.info(f"Found {len(job_cards)} potential job card links on page {page+1}.")

        for card in job_cards:
            # Extract information relative to the card link ('a' tag)
            # Titles are often in spans or headings within the card
            title_element = card.find('span', attrs={'title': True})
            title = title_element.text.strip() if title_element else "N/A"

            # Company name is often nearby, maybe in a sibling or parent div
            company_element = card.find('span', class_='companyName')
            company = company_element.text.strip() if company_element else "N/A"

            # Location is also often nearby
            location_element = card.find('div', class_='companyLocation')
            location_text = location_element.text.strip() if location_element else "N/A"

            # Get the job link
            job_url_relative = card.get('href')
            if not job_url_relative:
                continue
            job_url = urljoin(INDEED_BASE_URL, job_url_relative)

            # Date posted might be in a 'date' span
            date_element = card.find('span', class_='date')
            date_posted = parse_relative_date(date_element.text.strip()) if date_element else None

            # Description snippet (optional, often limited on search results)
            # description_snippet_element = card.find('div', class_='job-snippet')
            # description = description_snippet_element.text.strip() if description_snippet_element else None
            description = None # Keep it simple for now

            if title != "N/A" and company != "N/A":
                 try:
                     job_data = schemas.JobCreate(
                         title=title,
                         company=company,
                         location=location_text,
                         url=job_url,
                         source="Indeed",
                         date_posted=date_posted,
                         description=description
                     )
                     jobs.append(job_data)
                 except Exception as e: # Catch validation errors etc.
                     logger.warning(f"Failed to create JobCreate schema for {title} at {company}: {e}")


    logger.info(f"Finished Indeed scrape. Found {len(jobs)} jobs.")
    return jobs

def scrape_greenhouse(company_board_token: str) -> List[schemas.JobCreate]:
    """Scrapes jobs from a Greenhouse board using its API endpoint.

    Args:
        company_board_token: The unique token for the company's board 
                             (e.g., 'airbnb' from boards.greenhouse.io/airbnb).
    """
    logger.info(f"Starting Greenhouse scrape for board token: {company_board_token}")
    jobs: List[schemas.JobCreate] = []
    # Greenhouse often provides a JSON API endpoint
    api_url = f"https://boards-api.greenhouse.io/v1/boards/{company_board_token}/jobs?content=true"
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; JobBrightBot/1.0; +http://jobbright.ai/botinfo)' # Be a good bot
    }

    try:
        response = requests.get(api_url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for Greenhouse board {company_board_token}: {e}")
        return []
    except requests.exceptions.JSONDecodeError as e:
         logger.error(f"Failed to decode JSON from Greenhouse board {company_board_token}: {e}")
         return []

    if not data or 'jobs' not in data:
        logger.warning(f"No 'jobs' key found in Greenhouse API response for {company_board_token}")
        return []

    logger.info(f"Found {len(data['jobs'])} jobs on Greenhouse board: {company_board_token}")

    for job_item in data['jobs']:
        try:
            # Extract relevant fields - check Greenhouse API docs/response for exact fields
            title = job_item.get('title')
            url = job_item.get('absolute_url')
            location_name = job_item.get('location', {}).get('name', 'N/A') if job_item.get('location') else 'N/A'
            description_html = job_item.get('content', '') # Contains HTML
            # Basic HTML to text conversion (consider a library like html2text for better results)
            soup = BeautifulSoup(description_html, 'html.parser')
            description_text = soup.get_text(separator='\n', strip=True)
            date_posted_str = job_item.get('updated_at') # Often 'updated_at' is more reliable than 'posted_at'
            date_posted = None
            if date_posted_str:
                try:
                    # Format is often like '2023-10-27T10:30:00-07:00' or '2023-10-27T17:30:00Z'
                    date_posted = datetime.fromisoformat(date_posted_str.replace('Z', '+00:00'))
                except ValueError:
                     logger.warning(f"Could not parse Greenhouse date format: {date_posted_str}")

            if title and url:
                 job_data = schemas.JobCreate(
                     title=title,
                     company=company_board_token, # Use token as placeholder company name
                     location=location_name,
                     url=url,
                     description=description_text,
                     source="Greenhouse",
                     date_posted=date_posted
                 )
                 jobs.append(job_data)
            else:
                logger.warning(f"Skipping job from {company_board_token} due to missing title or URL: ID {job_item.get('id')}")

        except Exception as e:
            logger.warning(f"Failed to process job item from Greenhouse board {company_board_token}: {e} - Item: {job_item.get('id')}")

    logger.info(f"Finished Greenhouse scrape for {company_board_token}. Found {len(jobs)} valid jobs.")
    return jobs

def scrape_lever(company_site_tag: str) -> List[schemas.JobCreate]:
    """Scrapes jobs from a Lever board using its API endpoint.

    Args:
        company_site_tag: The unique tag for the company's site 
                         (e.g., 'lever' from jobs.lever.co/lever).
    """
    logger.info(f"Starting Lever scrape for site tag: {company_site_tag}")
    jobs: List[schemas.JobCreate] = []
    # Lever provides a JSON API endpoint
    api_url = f"https://api.lever.co/v0/postings/{company_site_tag}?mode=json"
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; JobBrightBot/1.0; +http://jobbright.ai/botinfo)',
        'Referer': f'https://jobs.lever.co/{company_site_tag}' # Often helpful
    }

    try:
        response = requests.get(api_url, headers=headers, timeout=15)
        response.raise_for_status()
        # Lever API returns a list directly
        data = response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for Lever board {company_site_tag}: {e}")
        return []
    except requests.exceptions.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON from Lever board {company_site_tag}: {e}")
        return []

    if not isinstance(data, list):
        logger.warning(f"Unexpected response format from Lever API for {company_site_tag}. Expected list.")
        return []

    logger.info(f"Found {len(data)} jobs on Lever board: {company_site_tag}")

    for job_item in data:
        try:
            title = job_item.get('text')
            url = job_item.get('hostedUrl')
            location_name = job_item.get('categories', {}).get('location', 'N/A')
            description_html = job_item.get('description')
            description_plain = job_item.get('descriptionPlain', '')
            # Prefer plain text if available, otherwise parse HTML
            description = description_plain if description_plain else BeautifulSoup(description_html, 'html.parser').get_text(separator='\n', strip=True)
            # Lever uses createdAt timestamp (milliseconds since epoch)
            created_at_ms = job_item.get('createdAt')
            date_posted = None
            if created_at_ms:
                try:
                    date_posted = datetime.fromtimestamp(created_at_ms / 1000)
                except Exception as e:
                    logger.warning(f"Could not parse Lever createdAt timestamp {created_at_ms}: {e}")

            # Company name isn't directly in the job posting, use the site tag
            company = company_site_tag

            if title and url:
                job_data = schemas.JobCreate(
                    title=title,
                    company=company,
                    location=location_name,
                    url=url,
                    description=description,
                    source="Lever",
                    date_posted=date_posted
                )
                jobs.append(job_data)
            else:
                 logger.warning(f"Skipping job from {company_site_tag} due to missing title or URL: ID {job_item.get('id')}")

        except Exception as e:
            logger.warning(f"Failed to process job item from Lever board {company_site_tag}: {e} - Item: {job_item.get('id')}")

    logger.info(f"Finished Lever scrape for {company_site_tag}. Found {len(jobs)} valid jobs.")
    return jobs

# --- Main Scraper Function --- 
def run_scrapers() -> List[schemas.JobCreate]:
    """Run all configured scrapers."""
    all_jobs = []
    # Example: Define targets or fetch from config/DB
    try:
        indeed_jobs = scrape_indeed(query="software engineer", location="Remote", pages=1) # Limit pages for now
        all_jobs.extend(indeed_jobs)
    except Exception as e:
        logger.error(f"Error running Indeed scraper: {e}")

    # Add calls to other scrapers (Lever, Greenhouse) here when implemented
    # Example: Fetch list of Greenhouse boards to scrape from config/DB
    greenhouse_boards = ["airbnb", "stripe"] # Example list
    for board_token in greenhouse_boards:
        try:
            greenhouse_jobs = scrape_greenhouse(board_token)
            all_jobs.extend(greenhouse_jobs)
        except Exception as e:
            logger.error(f"Error running Greenhouse scraper for {board_token}: {e}")

    # lever_jobs = scrape_lever(...)
    lever_sites = ["lever", "twitch"] # Example list
    for site_tag in lever_sites:
        try:
            lever_jobs = scrape_lever(site_tag)
            all_jobs.extend(lever_jobs)
        except Exception as e:
            logger.error(f"Error running Lever scraper for {site_tag}: {e}")

    logger.info(f"Finished all scrapers. Found {len(all_jobs)} jobs in total.")
    return all_jobs 