import time
import random
import csv
from datetime import datetime
from getpass import getpass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException

# ---- HARD-CODED LINKEDIN SCHOOL PAGE ----
COMPANY_URL = "https://www.linkedin.com/school/scaler-school-of-technology/posts/"
SCROLL_DELAY_RANGE = (2, 5)
MAX_EMPTY_SCROLLS = 4
SCROLL_LIMIT = 50  # Hard limit to avoid infinite loop

# ---- GET CREDENTIALS ----
email = input("📧 Enter your LinkedIn email: ")
password = getpass("🔒 Enter your LinkedIn password: ")

# ---- SETUP BROWSER OPTIONS ----
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=options)

try:
    # ---- STEP 1: LOGIN ----
    driver.get("https://www.linkedin.com/login")
    time.sleep(random.uniform(3, 5))
    driver.find_element(By.ID, "username").send_keys(email)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    time.sleep(random.uniform(5, 7))

    if "checkpoint" in driver.current_url or "captcha" in driver.page_source.lower():
        input("⚠️ CAPTCHA detected. Please solve it and press ENTER to continue...")

    # ---- STEP 2: GO TO COMPANY POSTS PAGE ----
    print(f"🚀 Opening {COMPANY_URL}")
    driver.get(COMPANY_URL)
    time.sleep(random.uniform(5, 6))

    # ---- STEP 3: SCROLLING & DATA COLLECTION ----
    print("🧭 Scrolling and extracting posts...")
    all_posts = set()
    empty_scrolls = 0
    scroll_count = 0

    while empty_scrolls < MAX_EMPTY_SCROLLS and scroll_count < SCROLL_LIMIT:
        post_elements = driver.find_elements(By.CLASS_NAME, "update-components-text")
        new_texts = set(p.text.strip() for p in post_elements if p.text.strip() and p.text.strip() not in all_posts)
        
        if new_texts:
            print(f"   ✅ Scroll #{scroll_count+1}: {len(new_texts)} new posts found.")
            all_posts.update(new_texts)
            empty_scrolls = 0
        else:
            print(f"   ⚠️ Scroll #{scroll_count+1}: No new posts.")
            empty_scrolls += 1

        scroll_count += 1
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
        time.sleep(random.uniform(*SCROLL_DELAY_RANGE))

    # ---- STEP 4: SAVE TO CSV ----
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"scaler_posts_{timestamp}.csv"

    with open(filename, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Post_Text"])
        for post in all_posts:
            writer.writerow([post])

    print(f"\n✅ Done! Extracted {len(all_posts)} posts. Saved to {filename}")

except NoSuchElementException as e:
    print(f"❌ Element not found: {e}")
except WebDriverException as e:
    print(f"❌ WebDriver error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
finally:
    input("\n📦 Press ENTER to close the browser...")
    driver.quit()
