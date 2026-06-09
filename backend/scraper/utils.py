# utils.py

import time
import random
import os
import platform
# Delay importing undetected_chromedriver until driver creation to avoid
# import-time failures on systems missing optional build tools (e.g. distutils).

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_chrome_major_version():
    """Retrieve the major version of Google Chrome installed on the system."""
    system = platform.system()
    if system == "Windows":
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
            version, _ = winreg.QueryValueEx(key, "version")
            return int(version.split('.')[0])
        except Exception:
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Google Chrome")
                version, _ = winreg.QueryValueEx(key, "DisplayVersion")
                return int(version.split('.')[0])
            except Exception:
                pass
    elif system == "Darwin":  # macOS
        try:
            import subprocess
            output = subprocess.check_output([
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", 
                "--version"
            ]).decode("utf-8").strip()
            parts = output.split()
            if len(parts) >= 3:
                return int(parts[2].split('.')[0])
        except Exception:
            pass
    elif system == "Linux":
        try:
            import subprocess
            for cmd in ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser"]:
                try:
                    output = subprocess.check_output([cmd, "--version"]).decode("utf-8").strip()
                    parts = output.split()
                    for part in parts:
                        if part[0].isdigit():
                            return int(part.split('.')[0])
                except Exception:
                    continue
        except Exception:
            pass
    return None

def create_stealth_driver(headless=False):
    """Create a stealth selenium Chrome driver using undetected-chromedriver."""
    try:
        import undetected_chromedriver as uc
    except ModuleNotFoundError:
        raise RuntimeError(
            "Missing dependency 'undetected-chromedriver'. "
            "Install it with: pip install undetected-chromedriver"
        )

    options = uc.ChromeOptions()
    
    # Headless mode setup for undetected-chromedriver requires special arguments or version support.
    # Generally, headless can be detected more easily, so non-headless is default.
    if headless or os.environ.get('RENDER') == 'true':
        options.add_argument('--headless=new')
        
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    browser_executable_path = None
    if os.path.exists('/usr/bin/chromium'):
        browser_executable_path = '/usr/bin/chromium'
    
    # Detect Chrome version to prevent mismatch issues
    major_version = get_chrome_major_version()
    if major_version:
        print(f"Detected Google Chrome major version: {major_version}")
        driver = uc.Chrome(
            options=options, 
            version_main=major_version,
            browser_executable_path=browser_executable_path
        )
    else:
        print("Could not detect Google Chrome major version. Falling back to default initialization.")
        driver = uc.Chrome(
            options=options,
            browser_executable_path=browser_executable_path
        )
    
    # Set standard window size
    driver.set_window_size(1280, 800)
    
    return driver


def check_and_click_close_popup(driver):
    """Check for the close popup button and click it if found."""
    try:
        close_popup_button = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'jd_modal_close'))
        )
        if close_popup_button.is_displayed():
            close_popup_button.click()
            print("Clicked 'jd_modal_close' button.")
            return True
    except:
        pass  # Silence the exception and avoid printing the error message
    return False

def countdown_timer(seconds):
    """Display a countdown timer in the console."""
    for i in range(seconds, 0, -1):
        print(f"Time remaining: {i} seconds", end='\r')
        time.sleep(1)
    print("Time's up! Stop file will be created.")
    with open('stop.txt', 'w') as f:
        f.write('')

def smooth_scroll_to(driver, target_position, duration=2):
    """Smoothly scroll the page to a target position."""
    start_position = driver.execute_script("return window.pageYOffset")
    distance = target_position - start_position
    start_time = time.time()
    
    while time.time() - start_time < duration:
        elapsed_time = time.time() - start_time
        scroll_position = start_position + (distance * (elapsed_time / duration))
        driver.execute_script(f"window.scrollTo(0, {scroll_position});")
        time.sleep(0.1)  # Adjust sleep time for smoother scrolling

    # Ensure we end exactly at the target position
    driver.execute_script(f"window.scrollTo(0, {target_position});")

RESULT_SELECTORS = [
    (By.CLASS_NAME, 'resultbox_info'),
    (By.CSS_SELECTOR, 'li.cntanr'),
    (By.CSS_SELECTOR, 'div.jsx-resultbox'),
    (By.CSS_SELECTOR, 'div.store-details'),
    (By.CSS_SELECTOR, 'div[class*="resultbox"]'),
    (By.CSS_SELECTOR, 'li[class*="cntanr"]')
]

def count_result_cards(driver):
    """Return the largest visible result-card count found by the known selectors."""
    counts = []
    for selector in RESULT_SELECTORS:
        try:
            counts.append(len(driver.find_elements(*selector)))
        except Exception:
            counts.append(0)
    return max(counts) if counts else 0

def human_like_scroll(
    driver,
    min_scroll_down=9,
    max_scroll_down=10,
    min_scroll_up=2,
    max_scroll_up=3,
    scroll_pause_range=(1, 2),
    stop_file='stop.txt',
    target_results=100,
    max_duration=300,
    idle_timeout=35
):
    last_height = driver.execute_script("return document.body.scrollHeight")
    last_position = driver.execute_script("return window.pageYOffset")  # Store the last scroll position
    start_time = time.time()
    last_content_check_time = time.time()
    best_result_count = count_result_cards(driver)
    print(f"Initial result cards detected: {best_result_count}/{target_results}")

    while True:  # Infinite loop for continuous scrolling
        if time.time() - start_time > max_duration:
            print(f"Max scroll time reached ({max_duration}s). Continuing with {best_result_count} detected cards.")
            return

        current_result_count = count_result_cards(driver)
        if current_result_count > best_result_count:
            best_result_count = current_result_count
            last_content_check_time = time.time()
            print(f"Detected {best_result_count}/{target_results} result cards.")

        if best_result_count >= target_results:
            print(f"Target reached: {best_result_count}/{target_results} result cards loaded.")
            return

        if time.time() - last_content_check_time > idle_timeout and best_result_count > 0:
            print(f"No new cards for {idle_timeout}s. Continuing with {best_result_count} detected cards.")
            return

        # Scrolling Down Phase
        total_scroll_down = random.randint(min_scroll_down, max_scroll_down)
        scroll_down_count = 0
        while scroll_down_count < total_scroll_down:
            # Check if stop file exists
            if os.path.exists(stop_file):
                print("Stop file detected. Stopping scroll.")
                return  # Exit the function and stop scrolling

            driver.execute_script("window.scrollBy(0, window.innerHeight / 2);")
            scroll_down_count += 1
            print(f"Scrolling down, attempt {scroll_down_count}/{total_scroll_down}")

            # Check and handle the popup button
            check_and_click_close_popup(driver)

            time.sleep(random.uniform(*scroll_pause_range))

            # Check if new content is loaded
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height != last_height:
                print("New content detected.")
                last_height = new_height  # Update last_height if new content is loaded
                scroll_down_count = 0  # Reset scroll down counter when new content is detected
                last_content_check_time = time.time()  # Update the content check time
                last_position = driver.execute_script("return window.pageYOffset")  # Update last known position
                best_result_count = max(best_result_count, count_result_cards(driver))

        # Short upward movement helps lazy-loaded pages trigger more loading without losing position.
        total_scroll_up = random.randint(min_scroll_up, max_scroll_up)
        scroll_up_count = 0
        while scroll_up_count < total_scroll_up:
            # Check if stop file exists
            if os.path.exists(stop_file):
                print("Stop file detected. Stopping scroll.")
                return  # Exit the function and stop scrolling

            driver.execute_script("window.scrollBy(0, -window.innerHeight / 2);")
            scroll_up_count += 1
            print(f"Scrolling up, attempt {scroll_up_count}/{total_scroll_up}")

            # Check and handle the popup button
            check_and_click_close_popup(driver)

            time.sleep(random.uniform(*scroll_pause_range))

            # Check if new content is loaded
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height != last_height:
                print("New content detected.")
                last_height = new_height  # Update last_height if new content is loaded
                scroll_up_count = 0  # Reset scroll up counter when new content is detected
                last_content_check_time = time.time()  # Update the content check time
                last_position = driver.execute_script("return window.pageYOffset")  # Update last known position
                best_result_count = max(best_result_count, count_result_cards(driver))

        # If no new content is detected for a long time, scroll to the top like a human, wait a bit, and scroll back to the older location
        if time.time() - last_content_check_time > idle_timeout:
            print("No new content detected for a while. Smoothly scrolling to the top.")
            smooth_scroll_to(driver, 0, duration=3)  # Smoothly scroll to the top in 3 seconds
            time.sleep(3)  # Wait for 3 seconds

            print(f"Smoothly scrolling back to last known position: {last_position}")
            smooth_scroll_to(driver, last_position, duration=3)  # Smoothly scroll back to the last position in 3 seconds

            last_content_check_time = time.time()  # Reset the content check timer

