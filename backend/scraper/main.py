# main.py

import time
import os
import csv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils import human_like_scroll, create_stealth_driver

TARGET_RECORDS = int(os.environ.get('SCRAPER_TARGET_RECORDS', '100'))
MAX_SCROLL_SECONDS = int(os.environ.get('SCRAPER_MAX_SCROLL_SECONDS', '300'))

def get_url_input():
    # Ask the user if they have a URL or need to enter city/keyword
    print("Select an option:")
    print("1. Provide a URL")
    print("2. Enter City/Keyword")
    choice = input("Enter the number of your choice (1 or 2): ").strip()

    if choice == '1':
        url = input("Enter the URL: ").strip()
    elif choice == '2':
        city = input("Enter the city name: ").replace(' ', '-')
        keyword = input("Enter the search keyword: ").replace(' ', '-')
        base_url = "https://www.justdial.com/"
        url = f"{base_url}{city}/{keyword}/"
    else:
        print("Invalid choice. Exiting.")
        exit()

    return url

def get_url_from_file(filename):
    # Read the URL from the specified file
    try:
        with open(filename, 'r') as file:
            url = file.readline().strip()
            if url:
                return url
            else:
                print(f"The file '{filename}' is empty. Exiting.")
                exit()
    except FileNotFoundError:
        print(f"The file '{filename}' does not exist. Exiting.")
        exit()

# Clean up stop file at the start of the execution if it exists
if os.path.exists('stop.txt'):
    try:
        os.remove('stop.txt')
    except Exception:
        pass

# Determine backend root and support tmp/temp_url.txt (or legacy temp_url.txt)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
tmp_path = os.path.join(ROOT_DIR, 'tmp', 'temp_url.txt')
legacy_temp = os.path.join(ROOT_DIR, 'temp_url.txt')

if os.path.exists(tmp_path):
    url = get_url_from_file(tmp_path)
elif os.path.exists(legacy_temp):
    url = get_url_from_file(legacy_temp)
else:
    # Use the original URL fetching method if no temp file exists
    url = get_url_input()

# Set up WebDriver using undetected-chromedriver
import sys
headless = '--headless' in sys.argv or os.environ.get('SCRAPER_HEADLESS') == 'true'
driver = create_stealth_driver(headless=headless)

try:
    driver.get(url)
    print("Opened URL:", url)

    # Check for 'Maybe Later' popup and click it if found
    time.sleep(5)
    try:
        maybe_later_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'maybelater'))
        )
        if maybe_later_button.is_displayed():
            maybe_later_button.click()
            print("Clicked 'Maybe Later' button.")
    except Exception as e:
        print(f"Maybe Later popup not found or failed to click: {str(e)}")

    human_like_scroll(
        driver,
        target_results=TARGET_RECORDS,
        max_duration=MAX_SCROLL_SECONDS
    )

    # Fetch and save page source for debugging
    page_source = driver.page_source
    with open('page_source.html', 'w', encoding='utf-8') as f:
        f.write(page_source)
    print("Page source saved to 'page_source.html'.")

    # Prefer a `data` folder for outputs; fall back to legacy `Scrapped`
    data_dir = os.path.join(ROOT_DIR, 'data')
    legacy_dir = os.path.join(ROOT_DIR, 'Scrapped')
    if not os.path.exists(data_dir):
        if os.path.exists(legacy_dir):
            output_dir = legacy_dir
        else:
            os.makedirs(data_dir, exist_ok=True)
            output_dir = data_dir
    else:
        output_dir = data_dir

    # Find and save data in CSV
    csv_filename = os.path.join(output_dir, f"{url.split('/')[-2]}.csv")
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Name', 'Address', 'Phone']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        # Try multiple parent selectors and use the one that finds the most elements
        parent_divs = []
        best_selector = None
        max_elements = 0
        
        for parent_selector in [
            (By.CLASS_NAME, 'resultbox_info'),
            (By.CSS_SELECTOR, 'li.cntanr'),
            (By.CSS_SELECTOR, 'div.jsx-resultbox'),
            (By.CSS_SELECTOR, 'div.store-details'),
            (By.CSS_SELECTOR, 'div[class*="resultbox"]'),
            (By.CSS_SELECTOR, 'li[class*="cntanr"]')
        ]:
            try:
                elements = driver.find_elements(*parent_selector)
                if len(elements) > max_elements:
                    max_elements = len(elements)
                    parent_divs = elements
                    best_selector = parent_selector
            except Exception:
                continue
                
        if parent_divs:
            print(f"Found {len(parent_divs)} elements using selector: {best_selector}")

        if not parent_divs:
            print("No parent divs found. Check the class name and page source.")
        else:
            saved_rows = 0
            seen_names = set()
            for index, parent_div in enumerate(parent_divs):
                try:
                    # Name extraction with fallbacks
                    name = ""
                    for name_selector in [
                        (By.CLASS_NAME, 'resultbox_title_anchor'),
                        (By.CSS_SELECTOR, 'span.jcn a'),
                        (By.CSS_SELECTOR, 'span[class*="jcn"] a'),
                        (By.CSS_SELECTOR, 'h2[class*="store-name"]'),
                        (By.CSS_SELECTOR, 'a[class*="title"]'),
                        (By.CSS_SELECTOR, 'a')
                    ]:
                        try:
                            name_div = parent_div.find_element(*name_selector)
                            name = name_div.text.strip()
                            if name:
                                break
                        except Exception:
                            continue

                    # Address extraction with fallbacks
                    address = ""
                    for addr_selector in [
                        (By.CLASS_NAME, 'resultbox_address'),
                        (By.CSS_SELECTOR, 'span.cont_fl_addr'),
                        (By.CSS_SELECTOR, 'span[class*="address"]'),
                        (By.CSS_SELECTOR, 'span[class*="adr"]'),
                        (By.CSS_SELECTOR, '.address')
                    ]:
                        try:
                            address_div = parent_div.find_element(*addr_selector)
                            address = address_div.text.strip()
                            if address:
                                break
                        except Exception:
                            continue

                    # Click "Show Number" button to reveal phone number with fallbacks
                    phone_number = "N/A"
                    for phone_selector in [
                        (By.CLASS_NAME, 'callcontent'),
                        (By.CSS_SELECTOR, 'span[class*="call"]'),
                        (By.CSS_SELECTOR, 'a[href^="tel:"]')
                    ]:
                        try:
                            phone_div = parent_div.find_element(*phone_selector)
                            try:
                                phone_div.click()
                                time.sleep(0.3)  # Wait for phone number to appear
                            except Exception:
                                pass
                            phone_number = phone_div.text.strip()
                            if phone_number and phone_number != "N/A":
                                break
                        except Exception:
                            continue

                    normalized_name = name.lower()
                    if name and normalized_name not in seen_names:
                        writer.writerow({'Name': name, 'Address': address or 'N/A', 'Phone': phone_number})
                        seen_names.add(normalized_name)
                        saved_rows += 1
                        if saved_rows >= TARGET_RECORDS:
                            print(f"Saved target record count: {saved_rows}/{TARGET_RECORDS}")
                            break
                    else:
                        print(f"Missing name in parent div {index}. Address: '{address}'")

                except Exception as e:
                    with open('error_log.txt', 'a', encoding='utf-8') as error_file:
                        error_file.write(f"An error occurred in parent div {index}: {str(e)}\n")

    print(f"Data extraction completed and saved to '{csv_filename}'.")

except Exception as e:
    print(f"An unexpected error occurred: {str(e)}")

finally:
    # Print script completion message
    print("Script execution completed.")
    
    # Wait for 3 seconds
    time.sleep(3)
    
    # Keep page_source.html for debugging selector/page-load failures.
    if os.path.exists('stop.txt'):
        os.remove('stop.txt')
    print("Deleted stop file")
