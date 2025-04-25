# -*- coding: utf-8 -*-
# Import necessary libraries
import tempfile
import os
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests
import random
from urllib.parse import urlparse, urljoin
import re
import time

# --- Configuration: Target Websites ---
# ### EDIT HERE ###
# Define the target URLs for scraping.
# Change these URLs to the website/pages you want to scrape.
UVEX_URL = "https://www.uvex-safety.com/en/products/safety-glasses/" # Uvex safety glasses
GLORIA_OAKLEY_URL = "https://www.gloria-eyewear.com/collections/oakley" # Gloria Eyewear Oakley collection

# --- Configuration: Output Directories ---
# ### EDIT HERE ###
# Define where scraped images will be saved. Directories will be created if they don't exist.
# Change these paths if you want to save images elsewhere or name the folders differently.
OUTPUT_DIR_UVEX = 'scraped_images/uvex_safety'
OUTPUT_DIR_GLORIA = 'scraped_images/gloria_oakley'
os.makedirs(OUTPUT_DIR_UVEX, exist_ok=True)
os.makedirs(OUTPUT_DIR_GLORIA, exist_ok=True)

# --- Selenium Configuration ---
# Set up Chrome options for the WebDriver. (Usually no need to change these unless debugging)
temp_user_data_dir = tempfile.mkdtemp() # Isolate browser session
chrome_options = Options()
chrome_options.add_argument(f"--user-data-dir={temp_user_data_dir}")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--headless") # Uncomment for headless mode (no UI)
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")
# Set a common User-Agent to avoid detection.
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
# Options to make Selenium harder to detect.
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

# Automatically manage ChromeDriver. (Usually no need to change)
service = Service(ChromeDriverManager().install())

# --- Utility Functions ---
# (Usually no need to change these unless filename requirements differ)
def sanitize_filename(name):
    """Cleans a string for use as a filename."""
    name = re.sub(r'^https?://[^/]+', '', name) # Remove base URL if present
    name = re.sub(r'[<>:"/\\|?*\s｜]+', '_', name) # Replace invalid chars with underscores
    return name[:100] # Limit length

def download_image(img_url, save_path, session, retries=3):
    """Downloads an image from a URL with retries."""
    for attempt in range(retries):
        try:
            if not img_url or img_url.startswith('data:image'): # Skip invalid/base64 URLs
                print(f"  Skipping invalid URL")
                return False
            print(f"  Attempt {attempt + 1} to download: {img_url[:60]}...")
            # Use the requests session to get the image
            img_response = session.get(img_url, stream=True, timeout=20)
            img_response.raise_for_status() # Check for HTTP errors
            # Save the image content to the specified path
            with open(save_path, 'wb') as f:
                for chunk in img_response.iter_content(8192):
                    f.write(chunk)
            print(f"  Successfully saved to: {os.path.basename(save_path)}")
            time.sleep(random.uniform(1, 3)) # Short random delay after success
            return True
        except requests.exceptions.RequestException as e:
            print(f"  Download attempt {attempt + 1} failed: {e}")
            if attempt + 1 == retries: return False
            time.sleep(random.uniform(3, 6)) # Longer delay before retry
        except Exception as e:
            print(f"  Error saving image {save_path}: {e}")
            return False

# --- Uvex Safety Scraping Logic ---
# ### EDIT HERE ###
# This entire function needs to be adapted for a new website.
# You might rename it (e.g., `scrape_my_website`) and update the call in the main block.
def scrape_uvex(driver, session):
    """Scrapes images from Uvex Safety, handling 'Load more' button."""
    print("\n===== Starting Uvex Safety Scraping =====")
    total_images_uvex = 0
    try:
        # ### EDIT HERE ### Use the correct URL variable defined above
        driver.get(UVEX_URL)
        wait = WebDriverWait(driver, 15) # Wait up to 15 seconds for elements

        # ### EDIT HERE ### Change the CSS selector to match the target website's structure.
        # Use browser developer tools (F12) to inspect elements and find the right selector for initial content.
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.picture-wrap'))) # Wait for initial content
        print("Uvex page loaded.")

        # ### EDIT HERE ### Adapt this loop for the target website's loading mechanism.
        # It might use a "Load more" button, pagination links, or infinite scroll.
        # Change the CSS selector for the button/link.
        # The logic inside the loop (click, wait) might need significant changes.
        while True: # Click "Load more" until it's gone
            try:
                # ### EDIT HERE ### CSS selector for the "Load more" button or pagination element
                load_more_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[role="button"].btn.btn-link')))
                print("Clicking 'Load more'...")
                driver.execute_script("arguments[0].scrollIntoView();", load_more_button)
                load_more_button.click()
                time.sleep(random.uniform(2, 4)) # Wait for new content
                # ### EDIT HERE ### Wait condition might need adjustment based on how new content loads.
                wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.picture-wrap img.img-fluid')))
            except Exception:
                print("No more 'Load more' button found.")
                break # Exit loop when button is gone or fails

        # ### EDIT HERE ### Change the CSS selector to find all image elements on the target site.
        image_elements = driver.find_elements(By.CSS_SELECTOR, 'div.picture-wrap img.img-fluid')
        print(f"Found {len(image_elements)} total thumbnail images.")

        if not image_elements:
            print("No images found on Uvex page.")
            return total_images_uvex

        # Collect unique image URLs
        urls_to_download = set()
        for img_tag in image_elements:
            # ### EDIT HERE ### Change the attribute ('src', 'data-src', 'srcset', etc.) to get the image URL.
            img_url = img_tag.get_attribute('src')
            if img_url:
                # ### EDIT HERE ### Decide if URL cleaning (like removing '?') is needed for the target site.
                img_url = img_url.split('?')[0] # Remove query params for Uvex
                urls_to_download.add(img_url)

        # Download the collected images
        img_index = 1
        for url in urls_to_download:
            # ### EDIT HERE ### Adjust how the filename is generated.
            # Check if 'alt' text is useful, otherwise use index or other available info.
            try: alt_text = image_elements[img_index-1].get_attribute('alt')
            except IndexError: alt_text = None
            product_name = sanitize_filename(alt_text or f"uvex_thumbnail_{img_index}")

            # ### EDIT HERE ### Determine the correct file extension logic or default.
            file_ext = os.path.splitext(urlparse(url).path)[1] or '.jpg' # Get extension, default .jpg
            if file_ext.lower() not in ['.jpg', '.jpeg', '.png', '.webp']: file_ext = '.jpg'

            # ### EDIT HERE ### Use the correct output directory variable defined above.
            filename = f"uvex_{product_name}_{img_index:02d}{file_ext}" # Creates filename like uvex_product_01.jpg
            save_path = os.path.join(OUTPUT_DIR_UVEX, filename)

            if download_image(url, save_path, session):
                total_images_uvex += 1
            img_index += 1

    except Exception as e:
        print(f"Error scraping Uvex: {e}")
    finally:
        # ### EDIT HERE ### Update the print statement to reflect the site scraped.
        print(f"===== Uvex Safety scraping completed, downloaded {total_images_uvex} images =====")
        return total_images_uvex

# --- Gloria Eyewear (Oakley) Scraping Logic ---
# ### EDIT HERE ###
# This entire function needs to be adapted for a new website with pagination.
# Rename it appropriately and update the call in the main block.
def scrape_gloria_oakley(driver, session):
    """Scrapes images from Gloria Eyewear Oakley pages, handling pagination."""
    print("\n===== Starting Gloria Eyewear (Oakley) Scraping =====")
    total_images_gloria = 0
    # ### EDIT HERE ### Adjust the maximum number of pages to check, or implement logic to detect the last page.
    max_pages = 7 # Limit number of pages to check

    for page in range(1, max_pages + 1):
        # ### EDIT HERE ### Adapt the URL structure for pagination if it's different.
        page_url = f"{GLORIA_OAKLEY_URL}?page={page}"
        print(f"\nProcessing page {page}: {page_url}")
        session.headers['Referer'] = page_url # Update Referer header for requests

        try:
            driver.get(page_url)
            wait = WebDriverWait(driver, 15)
            # ### EDIT HERE ### Change CSS selector for initial images on the page.
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.product_image img'))) # Wait for initial images
            print(f"Gloria page {page} loaded.")

            # ### EDIT HERE ### Logic for handling lazy loading might need adjustment (scrolling, waiting).
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            # ### EDIT HERE ### Change CSS selector for waiting for visible images after scroll.
            wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'div.product_image img')))

            # ### EDIT HERE ### Change CSS selector to find all image elements.
            image_elements = driver.find_elements(By.CSS_SELECTOR, 'div.product_image img')
            print(f"Found {len(image_elements)} images on page {page}.")

            if not image_elements:
                print(f"No images found on page {page}. Assuming end of collection.")
                break # Stop if a page has no images

            # Collect unique image URLs
            urls_to_download = set()
            for img_tag in image_elements:
                # ### EDIT HERE ### Change attribute ('src', 'data-src', etc.) for image URL. Prioritize lazy-loading attributes.
                img_url = img_tag.get_attribute('data-src') or img_tag.get_attribute('src')
                if img_url:
                    if img_url.startswith('//'): img_url = 'https:' + img_url # Fix protocol-relative URLs
                    # ### EDIT HERE ### Decide if URL cleaning is needed. Gloria needed query params.
                    urls_to_download.add(img_url) # Keep query params for Gloria

            # Download images for the current page
            img_index = 1
            for url in urls_to_download:
                 # ### EDIT HERE ### Adjust how the filename is generated.
                try: alt_text = image_elements[img_index-1].get_attribute('alt')
                except IndexError: alt_text = None
                product_name = sanitize_filename(alt_text or f"gloria_oakley_page_{page}_{img_index}")

                # ### EDIT HERE ### Determine the correct file extension logic or default.
                file_ext = os.path.splitext(urlparse(url).path)[1] or '.png' # Default .png for Gloria
                if file_ext.lower() not in ['.jpg', '.jpeg', '.png', '.webp']: file_ext = '.png'

                # ### EDIT HERE ### Use the correct output directory variable defined above.
                filename = f"gloria_oakley_{product_name}_{img_index:02d}{file_ext}"
                save_path = os.path.join(OUTPUT_DIR_GLORIA, filename)

                if download_image(url, save_path, session, retries=3):
                    total_images_gloria += 1
                img_index += 1

            # Wait between pages
            print(f"Finished page {page}. Waiting...")
            time.sleep(random.uniform(4, 8)) # Adjust delay as needed

        except Exception as e:
            print(f"Error processing Gloria page {page}: {e}")
            break # Stop if a page fails significantly

    # ### EDIT HERE ### Update the print statement to reflect the site scraped.
    print(f"===== Gloria Eyewear (Oakley) scraping completed, downloaded {total_images_gloria} images =====")
    return total_images_gloria

# --- Main Execution Block ---
if __name__ == "__main__":
    driver = None
    # Create a requests Session for efficient image downloading
    req_session = requests.Session()
    # ### EDIT HERE ### You might want to update the default Referer or other headers if needed.
    req_session.headers.update({ # Set headers for the requests session
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'Referer': GLORIA_OAKLEY_URL, # Set a default Referer
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br'
    })

    try:
        # Start the Selenium WebDriver
        print("Starting browser...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        # Apply script to hide the webdriver flag (usually keep this)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })
        print("Browser started.")

        # ### EDIT HERE ###
        # Call the specific scraping functions you want to run.
        # If you created a new function (e.g., `scrape_my_website`), call that instead.
        # You can comment out calls you don't need.
        scrape_uvex(driver, req_session)
        print("\n--- Waiting before next site ---\n")
        time.sleep(5)
        scrape_gloria_oakley(driver, req_session)

    except Exception as e:
        print(f"An error occurred in the main block: {e}")

    finally:
        # Cleanup: Close browser, session, and remove temp directory (usually keep this)
        if driver:
            print("Closing browser...")
            driver.quit()
            print("Browser closed.")
        req_session.close()
        if os.path.exists(temp_user_data_dir):
            try:
                shutil.rmtree(temp_user_data_dir)
                print(f"Removed temporary directory.")
            except Exception as e:
                print(f"Error removing temporary directory: {e}")
        print("\nScraping tasks finished.")