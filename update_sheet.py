from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

wait = WebDriverWait(driver, 20)

# --- Open login page ---
driver.get("https://ip3.rilapp.com")
time.sleep(5)

# --- Username ---
username_box = wait.until(
    EC.presence_of_element_located(
        (By.XPATH, "//input[@type='text' or @name='username' or @id='username']")
    )
)
username_box.clear()
username_box.send_keys(LOGIN_USERNAME)

# --- Password ---
password_box = wait.until(
    EC.presence_of_element_located(
        (By.XPATH, "//input[@type='password']")
    )
)
password_box.clear()
password_box.send_keys(LOGIN_PASSWORD)

# --- Login button ---
login_button = wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//button[@type='submit' or contains(text(),'Login') or contains(text(),'Sign')]")
    )
)
login_button.click()

time.sleep(10)
