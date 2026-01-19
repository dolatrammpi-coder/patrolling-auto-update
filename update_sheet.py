import os
import time
import json
from datetime import datetime

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

service = Service()
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

    time.sleep(8)


    # ===============================
    # REPORT PAGE
    # ===============================
    REPORT_URL = (
        "https://ip3.rilapp.com/railways/patrollingReport.php"
        "?fdate=18/01/2026&ftime=23:00"
        "&tdate=19/01/2026&ttime=07:10"
        "&category=-PM&Submit=Update"
    )

    driver.get(REPORT_URL)


    # ===============================
    # READ TABLE
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

for prefix in ["RG-PM-CH-HGJ/", "RG P"]:
    device = device.replace(prefix, "")

device = device.split("#")[0].strip()
            end_time = cols[4].text.strip()
            km_run = cols[6].text.strip()
            last_location = cols[5].text.strip()

            if device and end_time:
                # Convert End Time to datetime for sorting
                end_dt = datetime.strptime(end_time, "%d/%m/%Y %H:%M:%S")

                data.append([
                    device,
                    end_time,   # display
                    end_dt,     # sorting key
                    km_run,
                    last_location
                ])

    if not data:
        raise RuntimeError("No data extracted from table")


    # ===============================
    # SORT BY END TIME (ASCENDING)
    # ===============================
    data.sort(key=lambda x: x[2])


    # ===============================
    # PREPARE FINAL ROWS (REMOVE SORT KEY)
    # ===============================
    final_rows = [
        [row[0], row[1], row[3], row[4]]
        for row in data
    ]


    # ===============================
    # GOOGLE SHEET UPDATE
    # ===============================
    sheet.clear()
    sheet.update(
        "A1",
        [["Device", "End Time", "KM Run", "Last Location"]] + final_rows
    )

    print(f"SUCCESS: {len(final_rows)} rows updated in ascending End Time order")

finally:
    driver.quit()
