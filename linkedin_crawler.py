import logging
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

# Constants Variables
LOG_FILE = 'app.log'
LOG_FORMAT = '[%(asctime)s] %(levelname)-10s %(name)-14s %(message)s'
# HOMEPAGE_URL = 'https://www.linkedin.com'
# LOGIN_URL = 'https://www.linkedin.com/login'
# TARGET_URL=''


# Create Logger
logger = logging.getLogger(__name__)

# Create Handler
file_handler = logging.FileHandler(LOG_FILE, mode='w')
file_handler.setLevel(logging.INFO)

# Create Formatter and set it to Handler
file_format = logging.Formatter(LOG_FORMAT)
file_handler.setFormatter(file_format)

# Add Handler to the Logger
logger.addHandler(file_handler)


logger.warning('This is a warning message')
logger.error('This is an error message')
logger.critical('This is a critical message')
logger.info('This is an info message')
