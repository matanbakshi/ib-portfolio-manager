import subprocess
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import json

from src.logger import logger

LOGIN_SUCCEEDS_PHRASE = "Client login succeeds"
BIN_HEADLESS_CHROMIUM = "../bin/headless-chromium"
CREDS_FILE_PATH = "../config/ib_creds.json"


def launch_ib_gateway(run_script_path, conf_path, work_dir_path):
    subprocess.Popen([run_script_path, conf_path], cwd=work_dir_path)

    # Authenticate via headless browser

    pass


def _load_ib_creds():
    with open(CREDS_FILE_PATH, "r") as creds_file:
        creds = json.load(creds_file)
        return creds["user_name"], creds["password"]


def _automate_auth():
    user_name, password = _load_ib_creds()

    driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true'])

    driver.get("https://localhost:5000")

    # try:
    #     WebDriverWait(driver, 3).until(EC.presence_of_all_elements_located((By.ID, "user_name")))
    # except TimeoutException:
    #     logger.error("Login to IB failed, page loading timed out")
    #     raise

    un_box = driver.find_element_by_id("user_name")
    pw_box = driver.find_element_by_id("password")
    submit_btn = driver.find_element_by_id("submitForm")

    un_box.send_keys(user_name)
    pw_box.send_keys(password)

    submit_btn.click()

    try:
        assert LOGIN_SUCCEEDS_PHRASE in driver.page_source
    finally:
        driver.quit()


if __name__ == "__main__":
    _automate_auth()
