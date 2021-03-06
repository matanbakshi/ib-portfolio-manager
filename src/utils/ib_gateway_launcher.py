import subprocess, fcntl, os
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from time import time
from selenium.webdriver.support.wait import WebDriverWait
from src.logger import logger
from src.utils.config_loader import creds_conf

from src.utils.mfa_sms_receiver import MFASMSReceiver

LOGIN_SUCCEEDS_PHRASE = "Client login succeeds"
GATEWAY_RUNNING_PHRASE = "Open https://localhost:5000 to login"
GATEWAY_RUN_PATH = "bin/run.sh"
GATEWAY_CONF_ATH = "root/conf.yaml"
GATEWAY_WORKDIR_PATH = "external_bin/clientportal.beta.gw"
TIMEOUT_SECONDS = 10


def launch_ib_gateway_and_auth():
    _open_gateway_process()
    _automate_auth()


def relaunch():
    _kill_gateway_process()

    launch_ib_gateway_and_auth()


def _kill_gateway_process():
    kill_cmd = "kill -9 $(netstat -ltnp 2>/dev/null | grep 0.0.0.0:5000 | awk '{print $7}' | cut -d \"/\" -f 1)"

    proc = subprocess.run(kill_cmd, stdout=subprocess.PIPE)

    logger.info(f"Run command output: {proc.stdout.readline()}")


def _open_gateway_process():
    p = subprocess.Popen([GATEWAY_RUN_PATH, GATEWAY_CONF_ATH], cwd=GATEWAY_WORKDIR_PATH,
                         stdout=subprocess.PIPE)

    # Reading stdout without blocking (https://stackoverflow.com/a/8980466/10249811)
    fcntl.fcntl(p.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)

    # Read stdout until gateway launch finish or timeout reached
    start = time()
    time_elapsed_sec = 0

    aggregated_output = b""
    while GATEWAY_RUNNING_PHRASE not in str(aggregated_output) and time_elapsed_sec <= TIMEOUT_SECONDS:
        current_output = p.stdout.read()
        if current_output is not None:
            aggregated_output += current_output
        sleep(1)
        time_elapsed_sec = start - time()

    if GATEWAY_RUNNING_PHRASE not in str(aggregated_output):
        raise SystemError(f"IB gateway failed to launch, output: {aggregated_output}")

    return True


def _automate_auth():
    user_name, password, is_live = creds_conf["ib_user_name"], creds_conf["ib_password"], creds_conf[
        "is_live_account"]

    sms_receiver = MFASMSReceiver(60)
    if is_live:
        sms_receiver.start_listening_for_auth_code()

    driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true'],
                                 service_log_path="/tmp/phantom_logs.log")
    driver.get("https://localhost:5000")

    un_box = driver.find_element_by_id("user_name")
    pw_box = driver.find_element_by_id("password")
    submit_btn = driver.find_element_by_id("submitForm")

    un_box.send_keys(user_name)
    pw_box.send_keys(password)
    submit_btn.click()

    if is_live:
        # IB uses MFA only for live accounts
        SECURITY_CODE_BOX_ID = "chlginput"
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, SECURITY_CODE_BOX_ID)))
        except TimeoutException:
            logger.error("IB auth failed: MFA security code element wasn't present")
            driver.quit()
            raise

        auth_code = sms_receiver.auth_code
        if auth_code is not None:
            sec_code_box = driver.find_element_by_id(SECURITY_CODE_BOX_ID)
            sec_code_box.send_keys(auth_code)

            submit_btn = driver.find_element_by_id("submitForm")
            submit_btn.click()
        else:
            raise SystemError("IB auth code for MFA was not received")

    try:
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "pre"), LOGIN_SUCCEEDS_PHRASE))
    except TimeoutException:
        logger.error(f"Login to IB failed, success page loading timed out, page source: {driver.page_source}")
        raise
    finally:
        driver.quit()

    return True


if __name__ == "__main__":
    launch_ib_gateway_and_auth()
