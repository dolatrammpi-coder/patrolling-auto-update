import os
import time
import json
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


# ===============================
# ENV VARIABLES (GitHub Secrets)
# ===============================
LOGIN_USERNAME = os.getenv("LOGIN_USERNAME")
LOGIN_PASSWORD = os.getenv("LOGIN_PASSWORD")
GOOGLE_JSON = os.getenv("GOOGLE_JSON")
SHEET_NAME = os.getenv("SHEET_NAME")


# ===============================
# GOOGLE SHEET AUTH
# ===============================
scope = ["https://www.googleapis.com/auth/spreadsheets"]

creds = Credentials.from_service_account_info(
    json.loads(GOOGLE_JSON),
    scopes=scope
)

gc = gspread.authorize(creds)
sheet = gc.open(SHEET_NAME).sheet1


# ===============================
# SELENIUM (CHROME) SETUP
# ===============================
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)


try:
    # ===============================
    # 1️⃣ LOGIN PAGE
    # ===============================
    driver.get("https://ip3.rilapp.com")
    time.sleep(6)

    # ⚠️ NOTE:
    # अगर आगे NoSuchElement error आए,
    # तो यहाँ ID बदलनी पड़ेगी
    driver.find_element(By.ID, "username").send_keys(LOGIN_USERNAME)
    driver.find_element(By.ID, "password").send_keys(LOGIN_PASSWORD)
    driver.find_element(By.ID, "loginBtn").click()

    time.sleep(10)

    # ===============================
    # 2️⃣ PATROLLING REPORT PAGE
    # ===============================
    driver.get("https://ip3.rilapp.com/patrolling-report")
    time.sleep(12)

    # ===============================
    # 3️⃣ TABLE READ
    # ===============================
    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")

    data = []

    for r in rows:
        cols = r.find_elements(By.TAG_NAME, "td")

        # Safety check
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

    # ===============================
    # 4️⃣ GOOGLE SHEET UPDATE
    # ===============================
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())


finally:
    driver.quit()
