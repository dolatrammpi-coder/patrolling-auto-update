import os
import time
import json

import gspread
from google.oauth2.service_account import Credentials

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ===============================
# ENV VARIABLES (REQUIRED)
# ===============================
LOGIN_USERNAME = os.getenv("LOGIN_USERNAME")
LOGIN_PASSWORD = os.getenv("LOGIN_PASSWORD")
GOOGLE_JSON = os.getenv("GOOGLE_JSON")
SHEET_NAME = os.getenv("SHEET_NAME")

if not LOGIN_USERNAME or not LOGIN_PASSWORD:
    raise RuntimeError("LOGIN_USERNAME / LOGIN_PASSWORD missing")

if not GOOGLE_JSON or len(GOOGLE_JSON.strip()) < 20:
    raise RuntimeError("GOOGLE_JSON missing or invalid")

if not SHEET_NAME:
    raise RuntimeError("SHEET_NAME missing")


# ===============================
# GOOGLE SHEETS AUTH
# ===============================
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    json.loads(GOOGLE_JSON),
    scopes=SCOPES
)

gc = gspread.authorize(creds)
sheet = gc.open(SHEET_NAME).sheet1


# ===============================
# SELENIUM SETUP
# ===============================
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service()   # Selenium Manager handles driver
driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driver, 30)


try:
    # ===============================
    # LOGIN
    # ===============================
    driver.get("https://ip3.rilapp.com/railways/")

    username_box = wait.until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    password_box = wait.until(
        EC.presence_of_element_located((By.NAME, "password"))
    )

    username_box.clear()
    password_box.clear()

    username_box.send_keys(LOGIN_USERNAME)
    password_box.send_keys(LOGIN_PASSWORD)

    login_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
    )
    login_btn.click()

    # Login complete
    time.sleep(8)


    # ===============================
    # REPORT PAGE (CHANGE DATES IF NEEDED)
    # ===============================
    REPORT_URL = (
        "https://ip3.rilapp.com/railways/patrollingReport.php"
        "?fdate=17/01/2026&ftime=04:00"
        "&tdate=18/01/2026&ttime=16:00"
        "&category=-PM&Submit=Update"
    )

    driver.get(REPORT_URL)

    # ===============================
    # WAIT FOR TABLE
    # ===============================
    rows = wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "#example tbody tr")
        )
    )

    data = []
    for r in rows:
        cols = r.find_elements(By.TAG_NAME, "td")
        if len(cols) >= 7:
            device = cols[1].text.strip()
            end_time = cols[4].text.strip()
            km_run = cols[6].text.strip()
            last_location = cols[5].text.strip()

            if device:
                data.append([
                    device,
                    end_time,
                    km_run,
                    last_location
                ])

    if not data:
        raise RuntimeError("No data extracted from table")


    # ===============================
    # GOOGLE SHEET UPDATE
    # ===============================
    sheet.clear()
    sheet.update(
        "A1",
        [["Device", "End Time", "KM Run", "Last Location"]] + data
    )

    print(f"SUCCESS: {len(data)} rows updated in Google Sheet")

finally:
    driver.quit()
