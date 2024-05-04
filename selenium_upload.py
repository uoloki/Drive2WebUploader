"""
This script uses selenium to perform an authorization on a website and upload PNG-files into
a specified section
"""

import os
import time
import logging

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

# Setup logging
logging.basicConfig(level=logging.INFO, filename='drive_funcs.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

def perform_login(driver, url, username, username_html_id, password, password_html_id, log_btn_id):
    """
    Function to handle the login
    """
    try:
        driver.get(url)
        driver.find_element(By.ID, username_html_id).send_keys(username)
        driver.find_element(By.ID, password_html_id).send_keys(password)
        driver.find_element(By.CSS_SELECTOR, log_btn_id).click()
        logging.info("Successfully logged in to %s.", url)
        return True
    except Exception as error:
        logging.error("Failed to log in to %s: %s", url, str(error))
        return False

def upload_files(credentials_path):
    """
    Function to upload files
    """
    options = Options()
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    options.add_argument('user-agent=%s' % user_agent)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        with open(credentials_path, "r") as file:
            lines = [line.strip() for line in file]
            url = lines[1]
            username, username_html_id = lines[3], lines[4]
            password, password_html_id = lines[6], lines[7]
            log_btn_id = lines[9]
            second_url = lines[11]
            upload_css_selector = lines[13]
            save_btn_css_selector = lines[15]
    except Exception as error:
        logging.error("Failed to read credentials from %s: %s", credentials_path, str(error))
        driver.quit()
        return

    if not perform_login(driver, url, username, username_html_id, password, password_html_id, log_btn_id):
        driver.quit()
        return

    try:
        driver.get(second_url)
        file_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, upload_css_selector))
        )
    except Exception as error:
        logging.error("Failed to navigate to or find the file input at %s: %s", second_url, str(error))
        driver.quit()
        return

    png_files = [file for file in os.listdir(os.getcwd()) if file.endswith('.png')]
    uploaded_files = []

    for file_name in png_files:
        file_path = os.path.join(os.getcwd(), file_name)
        file_size = os.path.getsize(file_path)
        if file_size > 1024 * 1024:
            logging.warning("File %s exceeds the size limit of 1MB and will not be uploaded.", file_name)
            continue

        try:
            file_input.send_keys(file_path)

            time.sleep(1)

            button = driver.find_element(By.CSS_SELECTOR, save_btn_css_selector)
            actions = ActionChains(driver)
            actions.move_to_element(button).click().perform()

            uploaded_files.append(file_name)
            logging.info("Successfully uploaded %s.", file_name)
        except Exception as error:
            logging.error('Failed to upload %s: %s', file_name, str(error))

    for file_name in uploaded_files:
        os.remove(os.path.join(os.getcwd(), file_name))



if __name__ == "__main__" :
    upload_files('C:/passwords/cpa.credentials.txt')

