import logging
import sqlite3
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from sqlite3 import Error

# Constants Variables
LOG_FILE_PATH = 'linkedin.log'
LOG_FORMAT = '[%(asctime)s] %(levelname)-10s %(name)-14s %(message)s'
SQLITE_PATH = 'linkedin.sqlite'
LINKEDIN_EMAIL = ''
LINKEDIN_PASSWORD = ''
LINKEDIN_LOGIN_URL = 'https://www.linkedin.com/login'
LINKEDIN_CONNECTIONS_URL='https://www.linkedin.com/mynetwork/invite-connect/connections/'


# SQLite3 Queries
create_linkedin_table = """
CREATE TABLE IF NOT EXISTS linkedin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    headline TEXT,
    education TEXT,
    experience TEXT,
    location TEXT,
    about TEXT
);
"""
insert_data_linkedin_table = """
INSERT INTO
    linkedin (full_name, headline, education, experience, location, about)
VALUES
    ()
"""


def create_logger(path, log_format):
    """
    Create and configuring the logger
    """

    logger = logging.getLogger(__name__)
    logger.setLevel('INFO')

    file_handler = logging.FileHandler(path, mode='w')

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


def execute_query(sqlite_db, query, logger):
    """
    Execute queries and log the messages
    """

    cursor = sqlite_db.cursor()

    try:
        cursor.execute(query)
        sqlite_db.commit()
        logger.info("Query Executed Successfully")
    except Error as e:
        logger.error(f"Query Execution Error: {e}")


def insert_into_db(sqlite_db, logger):
    """
    Inserting Linkedin data to the DB
    """

    pass


logger = create_logger(LOG_FILE_PATH, LOG_FORMAT)
app_db = create_connection(SQLITE_PATH, logger)
execute_query(app_db, create_linkedin_table, logger)

# logger.warning('This is a warning message')
# logger.error('This is an error message')
# logger.critical('This is a critical message')
# logger.info('This is an info message')
