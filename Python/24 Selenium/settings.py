from selenium import webdriver
import os
from dotenv import load_dotenv

load_dotenv()
valid_email = os.getenv('valid_email')
valid_password = os.getenv('valid_password')

base_url = 'https://petfriends.skillfactory.ru/'
chrome_location = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
firefox_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
edge_location = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
default_timeout = 5

chrome_driver = os.path.join(os.path.dirname(__file__), 'Scripts', 'chromedriver.exe')
firefox_driver = os.path.join(os.path.dirname(__file__), 'Scripts', 'geckodriver.exe')
edge_driver = os.path.join(os.path.dirname(__file__), 'Scripts', 'msedgedriver.exe')

if not os.path.exists(chrome_driver):
    chrome_driver = None
if not os.path.exists(firefox_driver):
    firefox_driver = None
if not os.path.exists(edge_driver):
    edge_driver = None


def chrome_cfg_options(chrome_options: webdriver.ChromeOptions()):
    chrome_options.binary_location = chrome_location
    # chrome_options.add_extension('/path/to/extension.crx')
    chrome_options.add_argument('no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1400,1000')
    chrome_options.add_argument('--headless')
    chrome_options.headless = True
    return chrome_options


def firefox_cfg_options(firefox_options: webdriver.FirefoxOptions):
    firefox_options.binary = firefox_location
    firefox_options.add_argument('--headless')
    return firefox_options


def edge_cfg_options(edge_options: webdriver.EdgeOptions):
    edge_options.binary = edge_location
    # edge_options.headless = True
    edge_options.add_argument('disable-gpu')
    return edge_options
