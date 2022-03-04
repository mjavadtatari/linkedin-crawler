import logging
import sqlite3
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlite3 import Error

# Constants Variables
LOG_FILE_PATH = 'linkedin.log'
LOG_FORMAT = '[%(asctime)s] %(levelname)-9s %(name)-10s %(funcName)-30s %(message)s'
SQLITE_PATH = 'linkedin.sqlite'
LINKEDIN_EMAIL = ''
LINKEDIN_PASSWORD = ''
LINKEDIN_LOGIN_URL = 'https://www.linkedin.com/login'
MY_LINKEDIN_URL = 'https://www.linkedin.com/in/mjavadtatari'
LINKEDIN_CONNECTIONS_URL = 'https://www.linkedin.com/mynetwork/invite-connect/connections'


create_linkedin_table = """
CREATE TABLE IF NOT EXISTS linkedin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    headline TEXT,
    connect_time TEXT,
    page_id TEXT
);
"""


def create_logger(path, log_format):
    """
    Create and configuring the logger
    """

    logger = logging.getLogger(__name__)
    logger.setLevel('INFO')

    file_handler = logging.FileHandler(path, mode='w', encoding='utf-8')

    file_format = logging.Formatter(log_format)
    file_handler.setFormatter(file_format)

    logger.addHandler(file_handler)

    return logger


def create_connection(path, logger):
    """
    Create a connection and returns the sqlite3 object
    """

    sqlite_db = None

    try:
        sqlite_db = sqlite3.connect(path)
        logger.info("Connected to SQLite DB successfully")
    except Error as e:
        logger.error(f"SQLite Error: {e}")

    return sqlite_db


def execute_query(sqlite_db, query, logger, msg):
    """
    Execute queries and log the messages
    """

    cursor = sqlite_db.cursor()

    try:
        cursor.execute(query)
        sqlite_db.commit()
        logger.info(f"{msg} Query executed successfully")
    except Error as e:
        logger.error(f"Query Execution Error: {e}")


def insert_into_db(sqlite_db, logger, full_name, headline, connect_time, page_id):
    """
    Inserting Linkedin data to the DB
    """

    for f, h, c, p in zip(full_name, headline, connect_time, page_id):

        insert_data_linkedin_table = f"""
        INSERT INTO
            linkedin (full_name, headline, connect_time, page_id)
        VALUES
            ('{f}', '{h.replace("'", "''")}', '{c}', '{p}')
        """

        execute_query(sqlite_db, insert_data_linkedin_table, logger, f)


def create_driver():
    """
    creates a driver object and returns it
    """

    driver = None

    try:
        driver = webdriver.Firefox()
        logger.info('Driver Created Successfully')
    except Error as e:
        logger.error(f"Driver Creation Error: {e}")

    return driver


def login_into_linkedin(driver, url, email, password, logger):
    """
    tries to log in to LinkedIn by email and password
    """

    try:
        driver.get(url)

        email_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, 'session_key')))
        email_input.send_keys(email)

        password_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, 'session_password')))
        password_input.send_keys(password)

        login_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Sign in"]')))
        login_btn.click()

        time.sleep(2)

        if driver.current_url != 'https://www.linkedin.com/feed/':
            logger.warning(
                'Operation Stopped due to Linkedin Security Check, Sleep for 10 Seconds')
            time.sleep(100)
            if driver.current_url != 'https://www.linkedin.com/feed/':
                logger.critical(
                    'Operation Aborted due to Linkedin Security Check')
                driver.close()

        logger.info('Logged in Successfully')
    except Exception as e:
        logger.error(e.stacktrace[1])


def add_my_linkedin_page(driver, url, sqlite_db,  logger):
    """
    gets my LinkedIn page and scraping data from it
    """

    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.XPATH, '//h1[@class="text-heading-xlarge inline t-24 v-align-middle break-words"]')))

        my_full_name = driver.find_element(
            by=By.XPATH, value='//h1[@class="text-heading-xlarge inline t-24 v-align-middle break-words"]').text
        my_headline = driver.find_element(
            by=By.XPATH, value='//div[@class="text-body-medium break-words"]').text
        my_page_id = url.split('/')[-1]
    except Exception as e:
        logger.error(e.stacktrace[1])

    insert_into_db(sqlite_db, logger, [my_full_name],
                   [my_headline], ['Null'], [my_page_id])


def save_connections_info(driver, url, sqlite_db, logger):
    """
    gets the URL and loops until the end of the page, then scraping data and pass them to insert_into_db()
    """

    users_full_name = []
    users_headline = []
    users_connect_time = []
    users_page_id = []

    driver.get(url)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.XPATH, '//span[@class="mn-connection-card__name t-16 t-black t-bold"]')))

    last_scroll_point = driver.execute_script(
        'return document.body.scrollHeight')

    while True:
        try:
            # Make sure the page loaded completely
            load_more = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                (By.XPATH, '//button[@class="artdeco-button artdeco-button--muted artdeco-button--1 artdeco-button--full artdeco-button--secondary ember-view scaffold-finite-scroll__load-button"]')))
            load_more.click()
            time.sleep(2)
        except Exception as e:
            pass

        driver.execute_script(
            'window.scrollTo(0, document.body.scrollHeight)')

        time.sleep(2)

        present_scroll_point = driver.execute_script(
            'return document.body.scrollHeight')

        if present_scroll_point == last_scroll_point:
            break

        last_scroll_point = present_scroll_point

    try:
        temp_full_names = driver.find_elements(
            by=By.XPATH, value='//span[@class="mn-connection-card__name t-16 t-black t-bold"]')
        temp_headline = driver.find_elements(
            by=By.XPATH, value='//span[@class="mn-connection-card__occupation t-14 t-black--light t-normal"]')
        temp_connect_time = driver.find_elements(
            by=By.XPATH, value='//time[@class="time-badge t-12 t-black--light t-normal"]')
        temp_page_id = driver.find_elements(
            by=By.XPATH, value='//div[@class="mn-connection-card__details"]/a')

        logger.info(f'Connections Page Scraped Successfully')
    except Exception as e:
        logger.error(e.stacktrace[1])

    for i in temp_full_names:
        users_full_name.append(i.text)

    for i in temp_headline:
        users_headline.append(i.text)

    for i in temp_connect_time:
        users_connect_time.append(i.text)

    for i in temp_page_id:
        temp_x = i.get_attribute('href').split('/')
        users_page_id.append(temp_x[-2])

    insert_into_db(sqlite_db, logger, users_full_name,
                   users_headline, users_connect_time, users_page_id)


def close_program(driver, logger):
    driver.close()
    logger.info('Program Finished Successfully')


logger = create_logger(LOG_FILE_PATH, LOG_FORMAT)
app_db = create_connection(SQLITE_PATH, logger)

execute_query(app_db, create_linkedin_table, logger, 'Create table')

driver = create_driver()

login_into_linkedin(driver, LINKEDIN_LOGIN_URL,
                    LINKEDIN_EMAIL, LINKEDIN_PASSWORD, logger)

add_my_linkedin_page(driver, MY_LINKEDIN_URL, app_db, logger)

save_connections_info(driver, LINKEDIN_CONNECTIONS_URL, app_db, logger)

close_program(driver, logger)
