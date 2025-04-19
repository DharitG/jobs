import logging
import asyncio
import time
import json # Import json
from pathlib import Path # Import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Type
from urllib.parse import urlparse

from playwright.async_api import async_playwright, Browser, Page, Locator, Error as PlaywrightError
from playwright_stealth import stealth_async # For stealth
from sentence_transformers import SentenceTransformer, util # For semantic fallback
import torch # Sentence Transformers dependency
# Telemetry Imports (Placeholders - require installation and configuration)
# from prometheus_client import Counter, Gauge # Example
# from opentelemetry import trace # Example
# from opentelemetry.trace.status import Status, StatusCode # Example

from sqlalchemy.orm import Session
from sqlalchemy import func

from .. import models, schemas, crud
from ..db.session import SessionLocal # To get DB sessions if needed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Telemetry Placeholders ---
# tracer = trace.get_tracer(__name__) # Example OTel tracer
# AUTOSUBMIT_SUCCESS_COUNTER = Counter('autosubmit_success_total', 'Total successful auto-submissions') # Example Prometheus Counter
# AUTOSUBMIT_FAILURE_COUNTER = Counter('autosubmit_failure_total', 'Total failed auto-submissions', ['adapter', 'state']) # Example Prometheus Counter with labels
# ACTIVE_AUTOSUBMIT_GAUGE = Gauge('autosubmit_active_tasks', 'Number of auto-submit tasks currently running') # Example Prometheus Gauge


# --- Data Structures ---

@dataclass
class TaskResult:
    """Holds the outcome and artifacts of an auto-apply task."""
    success: bool = False
    message: str = ""
    state: str = "START" # Last successful state (e.g., LOGIN, FORM_FILL, VERIFY)
    html: Optional[str] = None
    screenshot: Optional[bytes] = None
    har: Optional[Dict] = None # Playwright HAR data
    error: Optional[str] = None

@dataclass
class JobApplicationTask:
    """Input data for the AutoSubmitter."""
    application_id: int
    job_url: str
    resume_path: str
    profile: Dict[str, Any] # User profile data (first_name, email, etc.)
    credentials: Dict[str, str] = field(default_factory=dict) # Site-specific login credentials (if needed/stored)

# --- CAPTCHA Handling ---

class CaptchaGate:
    """Placeholder for CAPTCHA detection and solving logic."""
    @staticmethod
    async def solve(page: Page) -> bool:
        """
        Detects and attempts to solve CAPTCHAs.
        Returns True if no CAPTCHA found or solved successfully, False otherwise.
        """
        # TODO: Implement CAPTCHA detection (iframes, common selectors)
        # TODO: Implement Tier 1: Avoidance (already done via stealth)
        # TODO: Implement Tier 2: Auto-solve (2Captcha, etc.)
        # TODO: Implement Tier 3: AI-solve (OCR for simple ones)
        # TODO: Implement Tier 4: Human-loop escalation
        logger.info("CaptchaGate: Checking for CAPTCHAs (placeholder)...")
        # For now, assume no CAPTCHA or it's handled externally/avoided
        is_captcha_visible = await page.locator('iframe[src*="captcha"]').is_visible() # Basic check
        if is_captcha_visible:
            logger.warning("CaptchaGate: Detected potential CAPTCHA iframe (solving not implemented).")
            # return False # Uncomment to block if CAPTCHA detected
        return True

# --- Selector Loading ---
SELECTOR_DIR = Path(__file__).parent / "ats_selectors"

def load_selectors(adapter_name: str) -> Dict[str, str]:
    """Loads selectors from the corresponding JSON file."""
    selector_file = SELECTOR_DIR / f"{adapter_name.lower()}.json"
    if not selector_file.exists():
        logger.error(f"Selector file not found: {selector_file}")
        return {}
    try:
        with open(selector_file, 'r') as f:
            data = json.load(f)
            return data.get("selectors", {})
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading selector file {selector_file}: {e}")
        return {}

# --- Semantic Fallback Helper ---

# Load model globally or cache it to avoid reloading on every call
# Consider moving model loading to a separate initialization step if memory is a concern
try:
    # Use a smaller, faster model suitable for label matching
    semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
    logger.info("SentenceTransformer model 'all-MiniLM-L6-v2' loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load SentenceTransformer model: {e}", exc_info=True)
    semantic_model = None

async def find_element_by_semantic_label(page: Page, target_label: str, element_type: str = "input") -> Optional[Locator]:
    """
    Finds an element (input, textarea, select) whose associated label semantically matches the target_label.
    Uses sentence-transformers for embedding comparison.
    """
    if not semantic_model:
        logger.warning("Semantic model not loaded, cannot perform semantic search.")
        return None

    logger.info(f"Attempting semantic search for '{target_label}' in elements of type '{element_type}'...")
    candidate_elements = page.locator(f"{element_type}")
    count = await candidate_elements.count()
    if count == 0:
        logger.info(f"No candidate elements of type '{element_type}' found.")
        return None

    logger.debug(f"Found {count} candidate {element_type} elements.")
    labels = []
    elements = []

    # Heuristics to find associated labels:
    # 1. Check label[for=element_id]
    # 2. Check element[aria-labelledby] -> points to ID of label element(s)
    # 3. Check parent label element (input inside label)
    # 4. Check preceding sibling label element
    # This part is complex and may need refinement based on common ATS patterns.

    for i in range(count):
        element = candidate_elements.nth(i)
        label_text = None
        try:
            # Heuristic 1: label[for=element_id]
            element_id = await element.get_attribute("id")
            if element_id:
                label_locator_for = page.locator(f'label[for="{element_id}"]')
                if await label_locator_for.count() > 0 and await label_locator_for.first.is_visible():
                    label_text = await label_locator_for.first.inner_text()
                    logger.debug(f"Label Heuristic 1 (for='{element_id}'): '{label_text}'")

            # Heuristic 2: element[aria-labelledby]
            if not label_text:
                aria_labelledby = await element.get_attribute("aria-labelledby")
                if aria_labelledby:
                    # aria-labelledby can be a space-separated list of IDs
                    label_ids = aria_labelledby.split()
                    aria_labels = []
                    for label_id in label_ids:
                        label_locator_aria = page.locator(f'#{label_id}')
                        if await label_locator_aria.count() > 0 and await label_locator_aria.first.is_visible():
                             aria_labels.append(await label_locator_aria.first.inner_text())
                    if aria_labels:
                        label_text = " ".join(aria_labels)
                        logger.debug(f"Label Heuristic 2 (aria-labelledby='{aria_labelledby}'): '{label_text}'")

            # Heuristic 3: Parent label (e.g., <label>Text <input></label>)
            if not label_text:
                 parent_label_locator = element.locator('xpath=./ancestor::label')
                 if await parent_label_locator.count() > 0 and await parent_label_locator.first.is_visible():
                     # Try to get text excluding the input's own text/value if nested deeply
                     full_parent_text = await parent_label_locator.first.inner_text()
                     # This is tricky, might need more specific exclusion logic
                     # For now, just take the text, might include input value sometimes
                     label_text = full_parent_text
                     logger.debug(f"Label Heuristic 3 (parent label): '{label_text}'")


            # Heuristic 4: Preceding sibling label
            # This is less reliable and harder to implement correctly with Playwright locators alone.
            # Skipping for now, focus on the more direct associations.
            # logger.debug("Skipping Heuristic 4 (preceding sibling label)")


            # Placeholder check (use cautiously as fallback)
            if not label_text:
                placeholder = await element.get_attribute("placeholder")
            #     if placeholder:
            #         label_text = placeholder
            #         logger.debug(f"Using placeholder as label for element {i}: '{label_text}'")

            if label_text:
                cleaned_label = label_text.strip().replace("*", "").lower() # Basic cleaning
                if cleaned_label:
                    labels.append(cleaned_label)
                    elements.append(element)

        except Exception as e:
            logger.warning(f"Error getting label/attributes for element {i}: {e}")
            continue # Skip element if error occurs

    if not labels:
        logger.info("No associated labels found for candidate elements.")
        return None

    # Generate embeddings
    try:
        logger.debug(f"Generating embeddings for {len(labels)} labels: {labels}")
        label_embeddings = semantic_model.encode(labels, convert_to_tensor=True)
        target_embedding = semantic_model.encode([target_label.lower()], convert_to_tensor=True)

        # Calculate cosine similarities
        cosine_scores = util.pytorch_cos_sim(target_embedding, label_embeddings)[0]
        logger.debug(f"Cosine scores: {cosine_scores}")

        # Find the best match above a threshold
        best_match_idx = torch.argmax(cosine_scores).item()
        best_score = cosine_scores[best_match_idx].item()

        similarity_threshold = 0.6 # Adjust this threshold based on testing
        logger.info(f"Best semantic match for '{target_label}': '{labels[best_match_idx]}' (Score: {best_score:.4f})")

        if best_score >= similarity_threshold:
            logger.info(f"Semantic match found above threshold {similarity_threshold}.")
            return elements[best_match_idx]
        else:
            logger.info("No semantic match found above threshold.")
            return None

    except Exception as e:
        logger.error(f"Error during semantic embedding/comparison: {e}", exc_info=True)
        return None


# --- Adapters ---

class BaseAdapter:
    """Abstract base class for ATS-specific interaction logic."""
    def __init__(self, task: JobApplicationTask):
        self.task = task
        adapter_name = self.__class__.__name__.replace("Adapter", "")
        self.selectors = load_selectors(adapter_name)
        if not self.selectors:
             logger.warning(f"No selectors loaded for {self.__class__.__name__}. Adapter may not function correctly.")

    async def login(self, page: Page) -> bool:
        """Handles site login if necessary."""
        logger.info(f"{self.__class__.__name__}: Login step (default: no login required).")
        # Most direct application links don't require login initially
        return True # Assume success if no login needed

    async def fill_form(self, page: Page) -> bool:
        """Fills the main application form."""
        raise NotImplementedError

    async def submit(self, page: Page) -> bool:
        """Clicks the final submit button."""
        raise NotImplementedError

    async def verify(self, page: Page) -> bool:
        """Verifies if the submission was successful."""
        raise NotImplementedError

    async def _apply_stealth_humanization(self, page: Page, action_description: str, target_locator: Optional[Locator] = None):
        """Applies delays, scrolls, and mouse movements to mimic human behavior."""
        base_delay = 0.15
        random_delay = time.time() % 0.3 # More randomness
        scroll_amount = 150 + (time.time() % 1 * 200) # Random scroll amount
        wait_time = base_delay + random_delay

        logger.debug(f"Humanizing before: {action_description} (wait: {wait_time:.2f}s, scroll: {scroll_amount:.0f}px)")

        # Simulate mouse movement towards the target element if provided
        if target_locator:
            try:
                target_box = await target_locator.bounding_box()
                if target_box:
                    start_x, start_y = await page.mouse.position() # Get current mouse position (might be 0,0 initially)
                    # Move mouse in a slightly randomized path towards the element center
                    target_x = target_box['x'] + target_box['width'] / 2 + (time.time() % 10 - 5) # Add small random offset
                    target_y = target_box['y'] + target_box['height'] / 2 + (time.time() % 10 - 5)
                    steps = int(5 + time.time() % 5) # Random number of steps for movement
                    logger.debug(f"Moving mouse towards ({target_x:.0f}, {target_y:.0f}) in {steps} steps")
                    await page.mouse.move(target_x, target_y, steps=steps)
                    await asyncio.sleep(0.05 + (time.time() % 0.1)) # Short pause after moving
            except Exception as move_error:
                 logger.warning(f"Could not simulate mouse movement: {move_error}") # Non-critical if fails

        # Scroll randomly
        await page.mouse.wheel(0, scroll_amount)
        await asyncio.sleep(wait_time) # Wait after scrolling/moving

class GreenhouseAdapter(BaseAdapter):
    """Adapter for Greenhouse ATS."""

    async def _fill_field(self, page: Page, field_key: str, target_label: str, value: str, element_type: str = "input"):
        """Helper to fill a field using static selector with semantic fallback."""
        if field_key not in self.selectors:
            logger.warning(f"GreenhouseAdapter: Static selector for '{field_key}' not found.")
            # Optionally attempt semantic search directly if static selector is missing
            element = await find_element_by_semantic_label(page, target_label, element_type)
            if element:
                logger.info(f"GreenhouseAdapter: Found '{target_label}' using semantic search (no static selector).")
                await element.fill(value)
            else:
                logger.warning(f"GreenhouseAdapter: Could not find element for '{target_label}' semantically either.")
            return # Skip if no selector and semantic fails

        try:
            static_locator = page.locator(self.selectors[field_key])
            # Use a short timeout for the static selector attempt
            await static_locator.wait_for(state="visible", timeout=5000)
            await static_locator.fill(value)
            logger.info(f"GreenhouseAdapter: Filled '{target_label}' using static selector.")
        except PlaywrightError:
            logger.warning(f"GreenhouseAdapter: Static selector failed for '{field_key}'. Trying semantic fallback for '{target_label}'.")
            element = await find_element_by_semantic_label(page, target_label, element_type)
            if element:
                await element.fill(value)
                logger.info(f"GreenhouseAdapter: Filled '{target_label}' using semantic fallback.")
                # TODO: Log this success for potential selector map update suggestion
            else:
                logger.error(f"GreenhouseAdapter: Semantic fallback failed for '{target_label}'. Could not fill field.")
                raise ValueError(f"Failed to find element for {target_label} using static or semantic methods.") # Raise error to stop the process if critical field fails

    async def fill_form(self, page: Page) -> bool:
        logger.info("GreenhouseAdapter: Filling form using loaded selectors with semantic fallback...")
        if not self.selectors: return False
        try:
            # Pass locator to humanization function
            first_name_locator = page.locator(self.selectors.get("first_name", "null")) # Use .get to avoid KeyError if missing
            await self._apply_stealth_humanization(page, "Filling First Name", target_locator=first_name_locator)
            await self._fill_field(page, "first_name", "First Name", self.task.profile.get("first_name", ""))

            last_name_locator = page.locator(self.selectors.get("last_name", "null"))
            await self._apply_stealth_humanization(page, "Filling Last Name", target_locator=last_name_locator)
            await self._fill_field(page, "last_name", "Last Name", self.task.profile.get("last_name", ""))

            email_locator = page.locator(self.selectors.get("email", "null"))
            await self._apply_stealth_humanization(page, "Filling Email", target_locator=email_locator)
            await self._fill_field(page, "email", "Email", self.task.profile.get("email", ""))

            phone_locator = page.locator(self.selectors.get("phone", "null"))
            await self._apply_stealth_humanization(page, "Filling Phone", target_locator=phone_locator)
            await self._fill_field(page, "phone", "Phone", self.task.profile.get("phone", ""))

            # Resume Upload
            if "resume_upload_input" in self.selectors:
                resume_locator = page.locator(self.selectors["resume_upload_input"])
                await self._apply_stealth_humanization(page, "Uploading Resume", target_locator=resume_locator)
                logger.info(f"Uploading resume from: {self.task.resume_path}")
                try:
                    await resume_locator.wait_for(state="attached", timeout=10000)
                    await resume_locator.set_input_files(self.task.resume_path)
                    await asyncio.sleep(1) # Wait a bit for upload potentially
                    logger.info("GreenhouseAdapter: Uploaded resume using static selector.")
                except PlaywrightError as e:
                     logger.error(f"GreenhouseAdapter: Failed to upload resume using static selector: {e}")
                     return False # Fail if resume upload fails
            else:
                logger.error("GreenhouseAdapter: Resume upload selector not found in config.")
                return False # Fail if resume upload selector is missing

            # LinkedIn URL (Optional)
            if "linkedin_url" in self.selectors:
                 linkedin_locator = page.locator(self.selectors["linkedin_url"])
                 await self._apply_stealth_humanization(page, "Filling LinkedIn", target_locator=linkedin_locator)
                 try:
                     # Check visibility within _fill_field now
                     await self._fill_field(page, "linkedin_url", "LinkedIn Profile", self.task.profile.get("linkedin_url", ""))
                 except ValueError: # Catch the error raised by _fill_field if both methods fail
                      logger.info("GreenhouseAdapter: LinkedIn field not found or not visible, skipping.")
            else:
                      logger.info("GreenhouseAdapter: LinkedIn selector not configured, skipping.")

            # --- Placeholder for Custom Questions & EEOC ---
            logger.info("GreenhouseAdapter: Attempting to handle custom questions/EEOC (placeholder)...")
            # Example: Try to find common EEOC questions semantically
            common_eeoc_labels = ["Gender", "Race", "Ethnicity", "Veteran Status", "Disability Status"]
            for label in common_eeoc_labels:
                # Primarily look for 'select' or radio buttons for EEOC
                select_element = await find_element_by_semantic_label(page, label, element_type="select")
                if select_element:
                    logger.warning(f"GreenhouseAdapter: Found potential EEOC select field for '{label}'. Answering logic not implemented.")
                    # TODO: Implement logic to select a default/user-provided answer (e.g., "Decline to self-identify")
                    # Example: await select_element.select_option(label="Decline to self-identify") # Requires exact option text
                else:
                    # Check for radio buttons as well
                    # Finding radio groups semantically is harder, might need specific selectors or DOM structure analysis
                    logger.debug(f"GreenhouseAdapter: No 'select' found for EEOC label '{label}'. Radio button check not implemented.")

            # Example: Try to find common work authorization questions
            work_auth_labels = ["Work Authorization", "Sponsorship", "Authorized to work"]
            for label in work_auth_labels:
                 input_element = await find_element_by_semantic_label(page, label, element_type="input")
                 if input_element:
                     logger.warning(f"GreenhouseAdapter: Found potential work auth input field for '{label}'. Answering logic not implemented.")
                     # TODO: Implement logic based on user profile data
                 else:
                     select_element = await find_element_by_semantic_label(page, label, element_type="select")
                     if select_element:
                         logger.warning(f"GreenhouseAdapter: Found potential work auth select field for '{label}'. Answering logic not implemented.")
                         # TODO: Implement logic based on user profile data (e.g., select "Yes" or "No")

            logger.info("GreenhouseAdapter: Finished placeholder handling for custom questions/EEOC.")
            # --- End Placeholder ---

            return True
        except PlaywrightError as e:
            logger.error(f"GreenhouseAdapter: Playwright error during fill_form: {e}")
            return False
        except Exception as e:
            logger.error(f"GreenhouseAdapter: Unexpected error during fill_form: {e}")
            return False

    async def submit(self, page: Page) -> bool:
        logger.info("GreenhouseAdapter: Clicking submit...")
        if not self.selectors: return False
        try:
            submit_locator = page.locator(self.selectors["submit_button"])
            await self._apply_stealth_humanization(page, "Clicking Submit", target_locator=submit_locator)
            # Add randomized click position
            await submit_locator.click(position={'x': time.time() % 5 + 3, 'y': time.time() % 5 + 3}) # Click near top-left corner with slight random offset
            return True
        except PlaywrightError as e:
            logger.error(f"GreenhouseAdapter: Playwright error during submit: {e}")
            return False
        except Exception as e:
            logger.error(f"GreenhouseAdapter: Unexpected error during submit: {e}")
            return False

    async def verify(self, page: Page) -> bool:
        logger.info("GreenhouseAdapter: Verifying submission...")
        if not self.selectors: return False
        success_selector = self.selectors["success_message"]
        # Add common error selectors (these are examples, adjust based on real observations)
        error_selector_text = "text=/error|please fix|required/i" # Check for common error text patterns
        error_selector_class = ".error, [class*='error-message'], [aria-invalid='true']" # Check for error classes/attributes

        try:
            # Wait for EITHER success or a known error indicator, whichever comes first
            await page.wait_for_selector(f"{success_selector}, {error_selector_text}, {error_selector_class}", timeout=15000)

            # Check if an error indicator is now visible
            if await page.locator(error_selector_text).count() > 0 or await page.locator(error_selector_class).count() > 0:
                 logger.warning("GreenhouseAdapter: Verification failed (error indicator found).")
                 return False

            # If no error found, assume success selector matched (or timeout occurred without error)
            # Re-check success selector explicitly to be sure (optional, but safer)
            if await page.locator(success_selector).count() > 0:
                 logger.info("GreenhouseAdapter: Verification successful (confirmation text found).")
                 return True
            else:
                 logger.warning("GreenhouseAdapter: Verification failed (timeout without success or error indicator).")
                 return False

        except PlaywrightError:
             # Timeout occurred without finding success OR error selectors we defined
             logger.warning("GreenhouseAdapter: Verification failed (timeout waiting for success/error).")
             return False
        except Exception as e:
            logger.error(f"GreenhouseAdapter: Unexpected error during verify: {e}")
            return False

class LeverAdapter(BaseAdapter):
    """Adapter for Lever ATS."""

    async def _fill_field(self, page: Page, field_key: str, target_label: str, value: str, element_type: str = "input"):
        """Helper to fill a field using static selector with semantic fallback."""
        if field_key not in self.selectors:
            logger.warning(f"LeverAdapter: Static selector for '{field_key}' not found.")
            element = await find_element_by_semantic_label(page, target_label, element_type)
            if element:
                logger.info(f"LeverAdapter: Found '{target_label}' using semantic search (no static selector).")
                await element.fill(value)
            else:
                logger.warning(f"LeverAdapter: Could not find element for '{target_label}' semantically either.")
            return

        try:
            static_locator = page.locator(self.selectors[field_key])
            await static_locator.wait_for(state="visible", timeout=5000)
            await static_locator.fill(value)
            logger.info(f"LeverAdapter: Filled '{target_label}' using static selector.")
        except PlaywrightError:
            logger.warning(f"LeverAdapter: Static selector failed for '{field_key}'. Trying semantic fallback for '{target_label}'.")
            element = await find_element_by_semantic_label(page, target_label, element_type)
            if element:
                await element.fill(value)
                logger.info(f"LeverAdapter: Filled '{target_label}' using semantic fallback.")
            else:
                logger.error(f"LeverAdapter: Semantic fallback failed for '{target_label}'. Could not fill field.")
                raise ValueError(f"Failed to find element for {target_label} using static or semantic methods.")

    async def fill_form(self, page: Page) -> bool:
        logger.info("LeverAdapter: Filling form using loaded selectors with semantic fallback...")
        if not self.selectors: return False
        try:
            # Lever often uses a single 'name' field
            full_name_locator = page.locator(self.selectors.get("full_name", "null"))
            await self._apply_stealth_humanization(page, "Filling Full Name", target_locator=full_name_locator)
            await self._fill_field(page, "full_name", "Full Name", f"{self.task.profile.get('first_name', '')} {self.task.profile.get('last_name', '')}")

            email_locator = page.locator(self.selectors.get("email", "null"))
            await self._apply_stealth_humanization(page, "Filling Email", target_locator=email_locator)
            await self._fill_field(page, "email", "Email", self.task.profile.get("email", ""))

            phone_locator = page.locator(self.selectors.get("phone", "null"))
            await self._apply_stealth_humanization(page, "Filling Phone", target_locator=phone_locator)
            await self._fill_field(page, "phone", "Phone", self.task.profile.get("phone", ""))

            # Resume Upload
            if "resume_upload_input" in self.selectors:
                resume_locator = page.locator(self.selectors["resume_upload_input"])
                await self._apply_stealth_humanization(page, "Uploading Resume", target_locator=resume_locator)
                logger.info(f"Uploading resume from: {self.task.resume_path}")
                try:
                    await resume_locator.wait_for(state="visible", timeout=10000)
                    await resume_locator.set_input_files(self.task.resume_path)
                    await asyncio.sleep(1) # Wait a bit for upload potentially
                    logger.info("LeverAdapter: Uploaded resume using static selector.")
                except PlaywrightError as e:
                    logger.error(f"LeverAdapter: Failed to upload resume using static selector: {e}")
                    return False # Fail if resume upload fails
            else:
                 logger.error("LeverAdapter: Resume upload selector not found in config.")
                 return False # Fail if resume upload selector is missing

            # LinkedIn URL (Optional)
            if "linkedin_url" in self.selectors:
                linkedin_locator = page.locator(self.selectors["linkedin_url"])
                await self._apply_stealth_humanization(page, "Filling LinkedIn", target_locator=linkedin_locator)
                try:
                    await self._fill_field(page, "linkedin_url", "LinkedIn Profile URL", self.task.profile.get("linkedin_url", ""))
                except ValueError:
                    logger.info("LeverAdapter: LinkedIn field not found or not visible, skipping.")
            else:
                logger.info("LeverAdapter: LinkedIn selector not configured, skipping.")

            logger.warning("LeverAdapter: Custom question/EEOC handling not implemented.")
            return True
        except PlaywrightError as e:
            logger.error(f"LeverAdapter: Playwright error during fill_form: {e}")
            return False
        except Exception as e:
            logger.error(f"LeverAdapter: Unexpected error during fill_form: {e}")
            return False

    async def submit(self, page: Page) -> bool:
        logger.info("LeverAdapter: Clicking submit...")
        if not self.selectors: return False
        try:
            submit_locator = page.locator(self.selectors["submit_button"])
            await self._apply_stealth_humanization(page, "Clicking Submit", target_locator=submit_locator)
            await submit_locator.click(position={'x': time.time() % 5 + 3, 'y': time.time() % 5 + 3}) # Randomized click
            return True
        except PlaywrightError as e:
            logger.error(f"LeverAdapter: Playwright error during submit: {e}")
            return False
        except Exception as e:
            logger.error(f"LeverAdapter: Unexpected error during submit: {e}")
            return False

    async def verify(self, page: Page) -> bool:
        logger.info("LeverAdapter: Verifying submission...")
        if not self.selectors: return False
        success_selector = self.selectors["success_message"]
        # Add common error selectors for Lever
        error_selector_text = "text=/error|fix the following|required/i"
        error_selector_class = ".error, .warning, [class*='error'], [aria-invalid='true']" # Lever might use 'warning' class too

        try:
            # Wait for EITHER success or a known error indicator
            await page.wait_for_selector(f"{success_selector}, {error_selector_text}, {error_selector_class}", timeout=15000)

            # Check if an error indicator is now visible
            if await page.locator(error_selector_text).count() > 0 or await page.locator(error_selector_class).count() > 0:
                 logger.warning("LeverAdapter: Verification failed (error indicator found).")
                 return False

            # If no error found, assume success selector matched (or timeout occurred without error)
            if await page.locator(success_selector).count() > 0:
                 logger.info("LeverAdapter: Verification successful (confirmation text found).")
                 return True
            else:
                 logger.warning("LeverAdapter: Verification failed (timeout without success or error indicator).")
                 return False

        except PlaywrightError:
             logger.warning("LeverAdapter: Verification failed (timeout waiting for success/error).")
             return False
        except Exception as e:
            logger.error(f"LeverAdapter: Unexpected error during verify: {e}")
            return False

class IndeedAdapter(BaseAdapter):
    """Adapter for Indeed ATS (Placeholder)."""
    async def fill_form(self, page: Page) -> bool:
        logger.error("IndeedAdapter: fill_form not implemented.")
        raise NotImplementedError("Indeed form filling not implemented.")

    async def submit(self, page: Page) -> bool:
        logger.error("IndeedAdapter: submit not implemented.")
        raise NotImplementedError("Indeed submit logic not implemented.")

    async def verify(self, page: Page) -> bool:
        logger.error("IndeedAdapter: verify not implemented.")
        raise NotImplementedError("Indeed verification logic not implemented.")

class WorkdayAdapter(BaseAdapter):
    """Adapter for Workday ATS (Placeholder)."""
    async def fill_form(self, page: Page) -> bool:
        logger.error("WorkdayAdapter: fill_form not implemented.")
        raise NotImplementedError("Workday form filling not implemented.")

    async def submit(self, page: Page) -> bool:
        logger.error("WorkdayAdapter: submit not implemented.")
        raise NotImplementedError("Workday submit logic not implemented.")

    async def verify(self, page: Page) -> bool:
        logger.error("WorkdayAdapter: verify not implemented.")
        raise NotImplementedError("Workday verification logic not implemented.")


# --- Site Detection ---

def detect_site(url: str) -> Optional[Type[BaseAdapter]]:
    """
    Detects the ATS based on the URL and returns the appropriate adapter class.
    """
    hostname = urlparse(url).hostname
    if not hostname:
        return None

    logger.info(f"Detecting site for hostname: {hostname}")
    if "greenhouse.io" in hostname:
        logger.info("Detected: Greenhouse")
        return GreenhouseAdapter
    elif "lever.co" in hostname:
        logger.info("Detected: Lever")
        return LeverAdapter
    elif "myworkdayjobs.com" in hostname or "workday.com/recruiting" in url: # Common Workday patterns
        logger.info("Detected: Workday")
        return WorkdayAdapter
    elif "indeed.com" in hostname: # Note: Indeed often uses iframes or redirects
        logger.info("Detected: Indeed")
        return IndeedAdapter
    # TODO: Add detection for Taleo, iCIMS, etc.
    # TODO: Implement DOM fingerprinting as fallback/confirmation
    else:
        logger.warning(f"Unsupported ATS/hostname: {hostname} for URL: {url}")
        return None

# --- AutoSubmitter Class (State Machine) ---

class AutoSubmitter:
    """Manages the state machine for a single job application attempt."""
    def __init__(self, task: JobApplicationTask):
        self.task = task
        self.adapter_class = detect_site(task.job_url)
        self.result = TaskResult(state="INIT")

    async def run(self) -> TaskResult:
        """Executes the auto-apply state machine."""
        if not self.adapter_class:
            self.result.success = False
            self.result.message = "Unsupported job site/ATS."
            self.result.state = "DETECT_SITE_FAILED"
            self.result.error = "No adapter found for URL."
            logger.error(f"AutoSubmitter: {self.result.message} URL: {self.task.job_url}")
            return self.result

        adapter = self.adapter_class(self.task)
        self.result.state = "DETECT_SITE_SUCCESS"

        # ACTIVE_AUTOSUBMIT_GAUGE.inc() # Increment active task gauge (Prometheus Placeholder)
        # with tracer.start_as_current_span("auto_submit_run", attributes={"application.id": self.task.application_id, "job.url": self.task.job_url}) as span: # OTel Placeholder
        try:
            # span.set_attribute("adapter.name", adapter.__class__.__name__) # OTel Placeholder
            async with async_playwright() as p:
                # --- Proxy Setup (Placeholder) ---
                # TODO: Implement proxy selection logic (e.g., from a pool, residential proxies)
                # proxy_config = get_proxy_for_domain(urlparse(self.task.job_url).hostname) # Example function call
                proxy_config = None # No proxy for now
                launch_options = {"headless": True} # Set headless=False for debugging
                if proxy_config:
                    launch_options["proxy"] = proxy_config
                    logger.info(f"Using proxy: {proxy_config.get('server')}")

                browser = await p.chromium.launch(**launch_options)

                # --- Browser Context Setup ---
                # TODO: Implement realistic header rotation (User-Agent, sec-ch-ua, etc.)
                # TODO: Implement fingerprint injection (canvas, webgl, fonts, etc. - potentially using external libraries/services)
                # TODO: Randomize viewport, locale, timezone, etc.
                context_options = {
                     "user_agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36', # Example UA
                     "viewport": {'width': 1920, 'height': 1080}, # Example viewport
                     "locale": 'en-US', # Example locale
                     "timezone_id": 'America/New_York' # Example timezone
                     # Add other stealth options here
                }
                context = await browser.new_context(**context_options)

                page = await context.new_page()
                await stealth_async(page) # Apply playwright-stealth

                # Start HAR recording (optional, for debugging)
                # await context.tracing.start(screenshots=True, snapshots=True, sources=True)

                try:
                    logger.info(f"Navigating to {self.task.job_url}...")
                    await page.goto(self.task.job_url, wait_until='domcontentloaded', timeout=60000)
                    self.result.state = "NAVIGATION_SUCCESS"

                    # --- State Machine Execution ---
                    if not await adapter.login(page):
                        self.result.message = "Login failed."
                        self.result.state = "LOGIN_FAILED"
                        raise ValueError("Login Step Failed")
                    self.result.state = "LOGIN_SUCCESS"

                    if not await adapter.fill_form(page):
                        self.result.message = "Form filling failed."
                        self.result.state = "FORM_FILL_FAILED"
                        raise ValueError("Form Fill Step Failed")
                    self.result.state = "FORM_FILL_SUCCESS"

                    if not await CaptchaGate.solve(page):
                        self.result.message = "CAPTCHA detected and could not be solved."
                        self.result.state = "CAPTCHA_FAILED"
                        raise ValueError("CAPTCHA Step Failed")
                    self.result.state = "CAPTCHA_SUCCESS" # Or bypassed

                    if not await adapter.submit(page):
                        self.result.message = "Submission click failed."
                        self.result.state = "SUBMIT_FAILED"
                        raise ValueError("Submit Step Failed")
                    self.result.state = "SUBMIT_SUCCESS"

                    if not await adapter.verify(page):
                        self.result.message = "Submission verification failed."
                        self.result.state = "VERIFY_FAILED"
                        raise ValueError("Verify Step Failed")
                    self.result.state = "VERIFY_SUCCESS"

                    # If all steps passed
                    self.result.success = True
                    self.result.message = "Application submitted and verified successfully."
                    logger.info(f"AutoSubmitter: {self.result.message} AppID: {self.task.application_id}")
                    # AUTOSUBMIT_SUCCESS_COUNTER.inc() # Prometheus Placeholder
                    # span.set_status(Status(StatusCode.OK)) # OTel Placeholder

                except Exception as step_error:
                    self.result.success = False
                    # Message and state should be set within the step that failed
                    if not self.result.message: # Set generic message if not already set
                        self.result.message = f"Error during state {self.result.state}: {step_error}"
                    self.result.error = str(step_error)
                    logger.error(f"AutoSubmitter: Step failed for AppID {self.task.application_id}. State: {self.result.state}, Error: {step_error}", exc_info=True) # Add exc_info for traceback
                    # AUTOSUBMIT_FAILURE_COUNTER.labels(adapter=adapter.__class__.__name__, state=self.result.state).inc() # Prometheus Placeholder
                    # span.set_status(Status(StatusCode.ERROR, description=f"Failed at state {self.result.state}: {step_error}")) # OTel Placeholder
                    # span.record_exception(step_error) # OTel Placeholder

                    # Capture artifacts on failure - Ensure page object is valid
                    if page and not page.is_closed():
                        try:
                            logger.info(f"Capturing failure artifacts for AppID {self.task.application_id}...")
                            self.result.html = await page.content()
                            self.result.screenshot = await page.screenshot(full_page=True)
                            logger.info(f"Successfully captured HTML and Screenshot for AppID {self.task.application_id}.")
                            # TODO: Add logic to upload these artifacts (e.g., to S3)
                        except Exception as artifact_error:
                            logger.error(f"AutoSubmitter: Failed to capture artifacts after error for AppID {self.task.application_id}: {artifact_error}", exc_info=True)
                    else:
                         logger.warning(f"AutoSubmitter: Page closed or invalid, cannot capture artifacts for AppID {self.task.application_id}.")


                finally:
                    # Stop HAR recording and save (optional) - Ensure context is valid
                    # har_path = f"application_{self.task.application_id}_trace.zip"
                    # await context.tracing.stop(path=har_path)
                    # logger.info(f"Saved trace/HAR to {har_path}") # Need logic to upload this

                    # if context and not context.is_closed(): # Check if context is valid before stopping trace
                    #     har_path = f"application_{self.task.application_id}_trace.zip"
                    #     await context.tracing.stop(path=har_path)
                    #     logger.info(f"Saved trace/HAR to {har_path}") # Need logic to upload this

                    if context and not context.is_closed():
                         logger.info(f"Closing browser context for AppID: {self.task.application_id}")
                         await context.close()
                    if browser and browser.is_connected():
                         logger.info(f"Closing browser for AppID: {self.task.application_id}")
                         await browser.close()

        except PlaywrightError as pw_error:
            self.result.success = False
            self.result.message = f"Playwright setup/navigation error: {pw_error}"
            self.result.state = "PLAYWRIGHT_ERROR"
            self.result.error = str(pw_error)
            logger.error(f"AutoSubmitter: Playwright setup error for AppID {self.task.application_id}: {pw_error}", exc_info=True)
            # AUTOSUBMIT_FAILURE_COUNTER.labels(adapter='N/A', state='PLAYWRIGHT_ERROR').inc() # Prometheus Placeholder
            # span.set_status(Status(StatusCode.ERROR, description=f"Playwright setup error: {pw_error}")) # OTel Placeholder
            # span.record_exception(pw_error) # OTel Placeholder
        except Exception as e:
            self.result.success = False
            self.result.message = f"Unexpected error during auto-submit execution: {e}"
            self.result.state = "EXECUTION_ERROR"
            self.result.error = str(e)
            logger.exception(f"AutoSubmitter: Unexpected error for AppID {self.task.application_id}", exc_info=e)
            # AUTOSUBMIT_FAILURE_COUNTER.labels(adapter=adapter.__class__.__name__ if 'adapter' in locals() else 'N/A', state='EXECUTION_ERROR').inc() # Prometheus Placeholder
            # span.set_status(Status(StatusCode.ERROR, description=f"Unexpected execution error: {e}")) # OTel Placeholder
            # span.record_exception(e) # OTel Placeholder

        # ACTIVE_AUTOSUBMIT_GAUGE.dec() # Decrement active task gauge (Prometheus Placeholder)
        return self.result


# --- Main Entry Point (Called by Celery Worker) ---

async def apply_to_job_async(db: Session, application_id: int):
    """
    Async function to handle the auto-application process for a single job application record.
    """
    logger.info(f"Starting async auto-apply process for application ID: {application_id}")
    application: models.Application | None = None
    try:
        # --- Fetch Application Details ---
        application = db.query(models.Application).filter(models.Application.id == application_id).first()
        if not application:
            logger.error(f"Application not found for ID: {application_id}")
            return
        if not application.user or not application.job or not application.resume:
            logger.error(f"Missing user, job, or resume for application ID: {application_id}")
            # Update status to error in DB
            application.status = models.ApplicationStatus.ERROR
            application.notes = "Missing required data (user, job, or resume)."
            db.add(application)
            db.commit()
            return
        if not application.resume.file_path:
            logger.error(f"Resume file path not found for resume ID: {application.resume.id}, application {application_id}")
            application.status = models.ApplicationStatus.ERROR
            application.notes = "Resume file path missing."
            db.add(application)
            db.commit()
            return

        user = application.user
        job = application.job
        resume = application.resume

        # --- Check Quota ---
        remaining_quota = check_user_quota(db=db, user=user)
        if remaining_quota <= 0:
            logger.warning(f"User {user.id} has no auto-apply quota remaining. Skipping application {application_id}.")
            application.status = models.ApplicationStatus.ERROR # Or a specific 'QUOTA_EXCEEDED' status
            application.notes = "Auto-apply quota exceeded for the month."
            db.add(application)
            db.commit()
            return

        logger.info(f"User {user.id} has {remaining_quota} auto-apply quota remaining. Proceeding with application {application_id}.")

        # --- Elite Tier Throttling (Placeholder) ---
        if user.subscription_tier == models.SubscriptionTier.ELITE:
            # TODO: Implement actual throttling logic (e.g., check last N application timestamps)
            throttle_delay_seconds = 5.0 + (time.time() % 5) # Example: Wait 5-10 seconds
            logger.info(f"Elite tier user {user.id}. Applying placeholder throttle delay of {throttle_delay_seconds:.1f} seconds.")
            await asyncio.sleep(throttle_delay_seconds)

        # --- Prepare Task Data ---
        user_profile = {
            "first_name": user.first_name or "", # Use new field
            "last_name": user.last_name or "",   # Use new field
            "email": user.email or "",
            "phone": user.phone_number or "", # Use new field
            "linkedin_url": user.linkedin_url or "" # Use new field
        }
        task_data = JobApplicationTask(
            application_id=application_id,
            job_url=job.url,
            resume_path=resume.file_path, # Ensure this is an accessible path for the worker
            profile=user_profile
            # credentials can be added if/when needed
        )

        # --- Execute AutoSubmitter ---
        submitter = AutoSubmitter(task=task_data)
        result = await submitter.run()

        # --- Update Application Status Based on Outcome ---
        if result.success:
            application.status = models.ApplicationStatus.APPLIED
            application.applied_at = datetime.utcnow()
            application.notes = result.message or "Auto-applied successfully."
        else:
            application.status = models.ApplicationStatus.ERROR # Or a more specific failure status
            application.notes = f"Auto-apply failed at state '{result.state}'. Reason: {result.message or result.error or 'Unknown error'}"

        db.add(application)
        db.commit()
        logger.info(f"Finished auto-apply attempt for application ID: {application_id}. Success: {result.success}. Final State: {result.state}. Message: {application.notes}")

    except Exception as e:
        logger.exception(f"Critical error during async auto-apply for application {application_id}", exc_info=e)
        if application: # Attempt to mark as error if possible
            try:
                application.status = models.ApplicationStatus.ERROR
                application.notes = f"Critical error during execution: {e}"
                db.add(application)
                db.commit()
            except Exception as final_update_e:
                logger.error(f"Failed to update application {application_id} status to ERROR after critical failure: {final_update_e}")
                db.rollback()
        else:
             db.rollback() # Rollback if commit failed or application not fetched


# --- Quota Checking Logic (Unchanged) ---
QUOTA_LIMITS = {
    models.SubscriptionTier.FREE: 50,
    models.SubscriptionTier.PRO: 10000,  # Effectively unlimited
    models.SubscriptionTier.ELITE: 10000, # Effectively unlimited
}

def check_user_quota(db: Session, user: models.User) -> int:
    """
    Checks the remaining auto-apply quota for the user in the current calendar month.
    Returns the number of applications remaining.
    """
    limit = QUOTA_LIMITS.get(user.subscription_tier, 0)
    # Check for Pro or Elite tiers specifically for unlimited quota
    if user.subscription_tier in [models.SubscriptionTier.PRO, models.SubscriptionTier.ELITE]:
        logger.info(f"User {user.id} has '{user.subscription_tier}' tier. Granting unlimited auto-apply quota.")
        return 99999 # Return a very large number to signify unlimited

    # For FREE tier or any other tiers without explicit unlimited quota
    now = datetime.utcnow()
    start_of_month = datetime(now.year, now.month, 1)

    try:
        applied_count = db.query(func.count(models.Application.id))\
            .filter(
                models.Application.user_id == user.id,
                models.Application.status == models.ApplicationStatus.APPLIED,
                models.Application.applied_at >= start_of_month
            ).scalar() or 0

        remaining = limit - applied_count
        logger.info(f"User {user.id} (Tier: {user.subscription_tier}): Monthly Limit={limit}, Used This Month={applied_count}, Remaining={max(0, remaining)}")
        return max(0, remaining) # Ensure non-negative return

    except Exception as e:
        logger.error(f"Error checking quota for user {user.id}: {e}")
        return 0
