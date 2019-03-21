import subprocess, fcntl, os
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import json

from selenium.webdriver.support.wait import WebDriverWait

from src.logger import logger

LOGIN_SUCCEEDS_PHRASE = "Client login succeeds"
CREDS_FILE_PATH = "../config/ib_creds.json"
GATEWAY_RUNNING_PHRASE = "Open https://localhost:5000 to login"
GATEWAY_RUN_PATH = "bin/run.sh"
GATEWAY_CONF_ATH = "root/conf.yaml"
GATEWAY_WORKDIR_PATH = "../bin/ib_gateway"
GATEWAY_AUTH_SCRIPT_PATH = "../bin/ib_gateway/auth.sh"


def launch_ib_gateway_and_auth(retry_auth=False):
    if not retry_auth:
        open_gateway_process()
        _automate_auth()
    _run_post_auth_script()


def _run_post_auth_script():
    subprocess.run([GATEWAY_AUTH_SCRIPT_PATH])


def open_gateway_process():
    p = subprocess.Popen([GATEWAY_RUN_PATH, GATEWAY_CONF_ATH], cwd=GATEWAY_WORKDIR_PATH,
                         stdout=subprocess.PIPE)

    # Reading stdout without blocking (https://stackoverflow.com/a/8980466/10249811)
    fcntl.fcntl(p.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)

    # Read stdout until gateway launch finish
    sleep(1)
    aggregated_output = b""
    current_output = p.stdout.read()
    while current_output:
        aggregated_output += current_output
        sleep(0.5)
        current_output = p.stdout.read()

    if GATEWAY_RUNNING_PHRASE not in str(aggregated_output):
        raise SystemError(f"IB gateway failed to launch, output: {aggregated_output}")

    return True


def _load_ib_creds():
    with open(CREDS_FILE_PATH, "r") as creds_file:
        creds = json.load(creds_file)
        return creds["user_name"], creds["password"]


def _automate_auth():
    user_name, password = _load_ib_creds()

    driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true'])
    driver.get("https://localhost:5000")

    un_box = driver.find_element_by_id("user_name")
    pw_box = driver.find_element_by_id("password")
    submit_btn = driver.find_element_by_id("submitForm")

    un_box.send_keys(user_name)
    pw_box.send_keys(password)
    submit_btn.click()

    try:
        WebDriverWait(driver, 3).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "pre"), LOGIN_SUCCEEDS_PHRASE))
    except TimeoutException:
        logger.error("Login to IB failed, page loading timed out")
        raise
    finally:
        driver.quit()

    return True


if __name__ == "__main__":
    launch_ib_gateway_and_auth()
