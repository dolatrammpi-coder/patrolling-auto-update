import os
import time
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# ---------- ENV VARIABLES ----------
LOGIN_USERNAME = os.getenv("LOGIN_USERNAME")
LOGIN_PASSWORD = os.getenv("LOGIN_PASSWORD")
GOOGLE_JSON = os.getenv("GOOGLE_JSON")
SHEET_NAME = os.getenv("SHEET_NAME")

# ---------- GOOGLE SHEET AUTH ----------
scope = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(
    eval(GOOGLE_JSON), scopes=scope
)
gc = gspread.authorize(creds)
sheet = gc.open(SHEET_NAME).sheet1

# ---------- SELENIUM SETUP ----------
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)

try:
    # 1️⃣ Login page
    driver.get("https://ip3.rilapp.com")
    time.sleep(5)

    # ⚠️ ये IDs वेबसाइट के अनुसार बदल सकती हैं
    driver.find_element(By.ID, "username").send_keys(LOGIN_USERNAME)
    driver.find_element(By.ID, "password").send_keys(LOGIN_PASSWORD)
    driver.find_element(By.ID, "loginBtn").click()

    time.sleep(8)

    # 2️⃣ Report Page
    driver.get("https://ip3.rilapp.com/patrolling-report")
    time.sleep(10)

    # 3️⃣ Table Read
    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")

    data = []
    for r in rows:
        cols = r.find_elements(By.TAG_NAME, "td")
        if len(cols) >= 6:
            data.append([
                cols[0].text,   # Device ID
                cols[3].text,   # End Time
                cols[4].text,   # KM Run
                cols[5].text    # Last Location
            ])

    df = pd.DataFrame(data, columns=[
        "Device ID", "End Time", "KM Run", "Last Location"
    ])

    # 4️⃣ Google Sheet Update
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

finally:
    driver.quit()
