import os
import time
import json
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ===============================
# ENV VARIABLES
# ===============================
LOGIN_USERNAME = os.getenv("LOGIN_USERNAME")
LOGIN_PASSWORD = os.getenv("LOGIN_PASSWORD")
GOOGLE_JSON = os.getenv("GOOGLE_JSON")
SHEET_NAME = os.getenv("SHEET_NAME")

if not GOOGLE_JSON or len(GOOGLE_JSON.strip()) < 20:
    raise ValueError("GOOGLE_JSON secret is empty or invalid")


# ===============================
# GOOGLE SHEET AUTH
# ===============================
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    json.loads(GOOGLE_JSON),
    scopes=scope
)

gc = gspread.authorize(creds)
sheet = gc.open(SHEET_NAME).sheet1


# ===============================
# SELENIUM SETUP  (⚠️ ORDER IMPORTANT)
# ===============================
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)

# ✅ wait MUST be after driver
wait = WebDriverWait(driver, 20)


try:
    # ===============================
    # LOGIN (ROBUST)
    # ===============================
    driver.get("https://ip3.rilapp.com")
    time.sleep(10)

    # iframe handle (अगर हो)
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    if iframes:
        driver.switch_to.frame(iframes[0])

    # Username
    username_box = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//input[not(@type='password')]")
        )
    )
    username_box.clear()
    username_box.send_keys(LOGIN_USERNAME)

    # Password
    password_box = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//input[@type='password']")
        )
    )
    password_box.clear()
    password_box.send_keys(LOGIN_PASSWORD)

    # Login button
    login_button = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button | //input[@type='submit']")
        )
    )
    login_button.click()

    time.sleep(12)

    # ===============================
    # REPORT PAGE
    # ===============================
    driver.get("https://ip3.rilapp.com/patrolling-report")
    time.sleep(12)

    # ===============================
    # TABLE READ
    # ===============================
    rows = wait.until(
        EC.presence_of_all_elements_located(
            (By.XPATH, "//table//tbody//tr")
        )
    )

    data = []
    for r in rows:
        cols = r.find_elements(By.TAG_NAME, "td")
        if len(cols) >= 6:
            data.append([
                cols[0].text.strip(),   # Device ID
                cols[3].text.strip(),   # End Time
                cols[4].text.strip(),   # KM Run
                cols[5].text.strip()    # Last Location
            ])

    if not data:
        raise ValueError("No data found in report table")

    df = pd.DataFrame(
        data,
        columns=["Device ID", "End Time", "KM Run", "Last Location"]
    )

    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

finally:
    driver.quit()

# अगर page iframe में हो तो switch
iframes = driver.find_elements(By.TAG_NAME, "iframe")
if iframes:
    driver.switch_to.frame(iframes[0])

# Username (generic catch)
username_box = wait.until(
    EC.presence_of_element_located(
        (By.XPATH, "//input[not(@type='password')]")
    )
)
username_box.clear()
username_box.send_keys(LOGIN_USERNAME)

# Password
password_box = wait.until(
    EC.presence_of_element_located(
        (By.XPATH, "//input[@type='password']")
    )
)
password_box.clear()
password_box.send_keys(LOGIN_PASSWORD)

# Login button (any clickable submit)
login_button = wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//button | //input[@type='submit']")
    )
)
login_button.click()

time.sleep(12)

    time.sleep(10)

    # ===============================
    # REPORT PAGE
    # ===============================
    driver.get("https://ip3.rilapp.com/patrolling-report")
    time.sleep(12)

    # ===============================
    # TABLE READ
    # ===============================
    rows = wait.until(
        EC.presence_of_all_elements_located(
            (By.XPATH, "//table//tbody//tr")
        )
    )

    data = []

    for r in rows:
        cols = r.find_elements(By.TAG_NAME, "td")
        if len(cols) >= 6:
            data.append([
                cols[0].text.strip(),   # Device ID
                cols[3].text.strip(),   # End Time
                cols[4].text.strip(),   # KM Run
                cols[5].text.strip()    # Last Location
            ])

    df = pd.DataFrame(
        data,
        columns=["Device ID", "End Time", "KM Run", "Last Location"]
    )

    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())


finally:
    driver.quit()
