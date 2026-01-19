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
# ENV VARIABLES
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
sheet = gc.open(SHEET_NAME).sheet
