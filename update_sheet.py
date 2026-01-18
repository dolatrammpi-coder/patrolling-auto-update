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

if not LOGIN_USERNAME or not LOGIN_PASSWORD:
    raise ValueError("LOGIN_USERNAME / LOGIN_PASSWORD missing")

if not SHEET_NAME:
    raise ValueError("SHEET_NAME missing")


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
# SELENIUM SETUP
# ===============================
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 20)


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

if not LOGIN_USERNAME or not LOGIN_PASSWORD:
    raise ValueError("LOGIN_USERNAME / LOGIN_PASSWORD missing")

if not SHEET_NAME:
    raise ValueError("SHEET_NAME missing")


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
# SELENIUM SETUP
# ===============================
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 30)


# ===============================
# LOGIN PAGE
# ===============================
driver.get("https://ip3.rilapp.com/railways/")
time.sleep(15)

iframes = driver.find_elements(By.TAG_NAME, "iframe")
if iframes:
    driver.switch_to.frame(iframes[0])

username_box = wait.until(
    EC.presence_of_element_located(
        (By.XPATH, "//input[not(@type='password')]")
    )
)
username_box.clear()
username_box.send_keys(LOGIN_USERNAME)

password_box = wait.until(
    EC.presence_of_element_located(
        (By.XPATH, "//input[@type='password']")
    )
)
password_box.clear()
password_box.send_keys(LOGIN_PASSWORD)

login_button = wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//button | //input[@type='submit']")
    )
)
login_button.click()

time.sleep(20)


# ===============================
# REPORT PAGE (DIRECT URL)
# ===============================

driver.get(
    "https://ip3.rilapp.com/railways/patrollingReport.php"
    "?fdate=17/01/2026"
    "&ftime=04:00"
    "&tdate=18/01/2026"
    "&ttime=16:00"
    "&category=-PM"
    "&Submit=Update"
)

time.sleep(20)


# ===============================
# ===============================
# TABLE READ (DATATABLES #example)
# ===============================

# DataTables पूरी तरह initialize होने का wait
rows = wait.until(
    EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "#example tbody tr")
    )
)

data = []

for r in rows:
    cols = r.find_elements(By.TAG_NAME, "td")

    # Columns index (HTML से confirm)
    # 0 = Section (blank)
    # 1 = Device
    # 2 = Start Time
    # 3 = Start Address
    # 4 = End Time
    # 5 = End Address
    # 6 = KM Run

    if len(cols) >= 7:
        device = cols[1].text.strip()
        end_time = cols[4].text.strip()
        km_run = cols[6].text.strip()
        last_location = cols[5].text.strip()

        if device and end_time:
            data.append([
                device,
                end_time,
                km_run,
                last_location
            ])

if not data:
    raise RuntimeError("Table found but no usable data extracted")
