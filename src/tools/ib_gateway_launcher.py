import os
import subprocess
from selenium import webdriver

BIN_HEADLESS_CHROMIUM = "../bin/headless-chromium"


def launch_ib_gateway(run_script_path, conf_path, work_dir_path):
    subprocess.run([run_script_path, conf_path], cwd=work_dir_path)

    # Authenticate via headless browser

    pass


def _automate_auth():
    driver = _get_selenium_driver()

    # driver.get("https://localhost:5000")
    driver.get("https://facebook.com")
    print(driver.title)

    driver.close()


def _get_selenium_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1280x1696')
    chrome_options.add_argument('--user-data-dir=/tmp/user-data')
    chrome_options.add_argument('--hide-scrollbars')
    chrome_options.add_argument('--enable-logging')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--log-level=0')
    chrome_options.add_argument('--v=99')
    chrome_options.add_argument('--single-process')
    chrome_options.add_argument('--data-path=/tmp/data-path')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--homedir=/tmp')
    chrome_options.add_argument('--disk-cache-dir=/tmp/cache-dir')
    chrome_options.add_argument(
        'user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')

    chrome_options.binary_location = BIN_HEADLESS_CHROMIUM  # TODO: Change if necessary

    caps = webdriver.DesiredCapabilities().CHROME

    caps["acceptSslCerts"] = True

    return webdriver.Chrome(chrome_options=chrome_options)


if __name__ == "__main__":
    _automate_auth()
