import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin, urlencode
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time # For potential delays
from typing import List, Optional

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

def scrape_indeed(query: str, location: str, pages: int = 1) -> List[schemas.JobCreate]:
    """Scrapes job listings from Indeed using Playwright."""
    logger.info(f"Starting Indeed Playwright scrape for query='{query}', location='{location}', pages={pages}")
    jobs: List[schemas.JobCreate] = []
    # Selectors (These might need frequent updates based on Indeed's changes)
    # Using data-testid where possible for potentially better stability
    job_card_selector = 'div.job_seen_beacon' # Main container for each job card
    title_link_selector = 'h2.jobTitle > a' # Contains title and link
    company_selector = 'span[data-testid="company-name"]'
    location_selector = 'div[data-testid="text-location"]'
    date_selector = 'span[data-testid="myJobsStateDate"]' # Relative date like "Posted 2 days ago"
    results_container_selector = '#mosaic-provider-jobcards > ul' # Container holding the job cards (li elements)

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True) # Run headless for server environment
            page = browser.new_page()
        except Exception as e:
            logger.error(f"Failed to launch Playwright browser: {e}")
            return []

        for page_num in range(pages):
            start_index = page_num * 15 # Indeed pagination often uses 'start=' with steps of 15
            params = {'q': query, 'l': location, 'start': start_index, 'filter': 0} # filter=0 might help avoid some modals
            search_url = f"{INDEED_BASE_URL}/jobs?{urlencode(params)}"
            logger.info(f"Navigating to URL: {search_url}")

            try:
                page.goto(search_url, timeout=30000) # Increased timeout
                # Wait for the main job results container to be present
                page.wait_for_selector(results_container_selector, timeout=20000)
                logger.info(f"Page {page_num + 1} loaded successfully.")
                # Optional: Add a small delay or wait for network idle if results load slowly
                # page.wait_for_load_state('networkidle', timeout=5000)
                time.sleep(2) # Small fixed delay as fallback

            except PlaywrightTimeoutError:
                logger.warning(f"Timeout waiting for job results container on page {page_num + 1} ({search_url}). Skipping page.")
                continue
            except Exception as e:
                logger.error(f"Navigation or initial wait failed for {search_url}: {e}")
                continue # Skip this page

            # Locate all job cards within the container
            try:
                job_card_elements = page.locator(f'{results_container_selector} > li {job_card_selector}')
                count = job_card_elements.count()
                logger.info(f"Found {count} potential job card elements on page {page_num + 1}.")
                if count == 0:
                    logger.warning(f"No job card elements found using selector '{job_card_selector}' on page {page_num + 1}.")
                    # Optional: Capture page HTML for debugging
                    # logger.debug(page.content())
                    continue
            except Exception as e:
                logger.error(f"Error locating job card elements on page {page_num + 1}: {e}")
                continue

            for i in range(count):
                card = job_card_elements.nth(i)
                title = "N/A"
                company = "N/A"
                location_text = "N/A"
                job_url = None
                date_posted: Optional[datetime] = None
                description = None # Keep description simple for now

                try:
                    # Extract Title and URL
                    title_link_element = card.locator(title_link_selector).first # Use first() to avoid error if multiple matches
                    if title_link_element.count() > 0:
                        title = title_link_element.inner_text(timeout=1000)
                        href = title_link_element.get_attribute('href', timeout=1000)
                        if href:
                            job_url = urljoin(INDEED_BASE_URL, href)
                    else:
                        logger.debug(f"Title link selector '{title_link_selector}' not found in card {i+1}")


                    # Extract Company
                    company_element = card.locator(company_selector).first
                    if company_element.count() > 0:
                         company = company_element.inner_text(timeout=1000)
                    else:
                         logger.debug(f"Company selector '{company_selector}' not found in card {i+1}")


                    # Extract Location
                    location_element = card.locator(location_selector).first
                    if location_element.count() > 0:
                        location_text = location_element.inner_text(timeout=1000)
                    else:
                         logger.debug(f"Location selector '{location_selector}' not found in card {i+1}")


                    # Extract Date
                    date_element = card.locator(date_selector).first
                    if date_element.count() > 0:
                        date_str = date_element.inner_text(timeout=1000)
                        date_posted = parse_relative_date(date_str)
                    else:
                         # Fallback: Try finding date in other common places if needed
                         logger.debug(f"Date selector '{date_selector}' not found in card {i+1}")


                    if title != "N/A" and company != "N/A" and job_url:
                        job_data = schemas.JobCreate(
                            title=title.strip(),
                            company=company.strip(),
                            location=location_text.strip(),
                            url=job_url,
                            source="Indeed",
                            date_posted=date_posted,
                            description=description # Keep None for now
                        )
                        jobs.append(job_data)
                    else:
                        logger.warning(f"Skipping card {i+1} on page {page_num+1} due to missing critical info (Title: {title}, Company: {company}, URL: {job_url})")

                except PlaywrightTimeoutError as te:
                     logger.warning(f"Timeout extracting data from card {i+1} on page {page_num+1}: {te}")
                except Exception as e:
                    logger.warning(f"Error processing card {i+1} on page {page_num+1}: {e}")

            # Optional: Check for next page link and break if not found, or implement clicking 'next'
            # next_button = page.locator('a[data-testid="pagination-page-next"]')
            # if not next_button.is_visible():
            #     logger.info("No next page button found. Ending scrape.")
            #     break

        try:
            browser.close()
        except Exception as e:
            logger.error(f"Error closing Playwright browser: {e}")

    logger.info(f"Finished Indeed Playwright scrape. Found {len(jobs)} jobs.")
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
        # Limit pages for initial testing/development
        indeed_jobs = scrape_indeed(query="software engineer", location="Remote", pages=1)
        all_jobs.extend(indeed_jobs)
    except Exception as e:
        logger.exception(f"Critical error running Indeed scraper: {e}") # Use logger.exception to include traceback

    # Add calls to other scrapers (Lever, Greenhouse) here
    # Example: Fetch list of Greenhouse boards to scrape from config/DB
    greenhouse_boards = ["airbnb", "stripe"] # Example list
    for board_token in greenhouse_boards:
        try:
            greenhouse_jobs = scrape_greenhouse(board_token)
            all_jobs.extend(greenhouse_jobs)
        except Exception as e:
            logger.exception(f"Error running Greenhouse scraper for {board_token}: {e}")

    # lever_jobs = scrape_lever(...)
    lever_sites = ["lever", "twitch"] # Example list
    for site_tag in lever_sites:
        try:
            lever_jobs = scrape_lever(site_tag)
            all_jobs.extend(lever_jobs)
        except Exception as e:
            logger.exception(f"Error running Lever scraper for {site_tag}: {e}")

    logger.info(f"Finished all scrapers. Found {len(all_jobs)} jobs in total.")
    return all_jobs
