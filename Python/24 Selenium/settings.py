import platform

from selenium import webdriver
from selenium.webdriver.safari.options import Options as SafariOptions
import os
from dotenv import load_dotenv

load_dotenv()
valid_email = os.getenv('valid_email')
valid_password = os.getenv('valid_password')

base_url = 'https://petfriends.skillfactory.ru/'
if 'mac' in platform.system().lower() or 'darwin' in platform.system().lower():
    chrome_location = r'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    firefox_location = r'/Applications/Firefox.app/Contents/MacOS/firefox'
    edge_location = r'/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge'
    safari_location = r'/Applications/Safari.app'
    edge_driver = os.path.join(os.path.dirname(__file__), 'venv', 'bin', 'msedgedriver')
    safari_driver = r'/usr/bin/safaridriver'
    firefox_driver = os.path.join(os.path.dirname(__file__), 'venv', 'bin', 'geckodriver')
    chrome_driver = os.path.join(os.path.dirname(__file__), 'venv', 'bin', 'chromedriver')
else:  # 'win' in platform.system() or 'nt' in platform.system():
    chrome_location = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
    firefox_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
    edge_location = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    safari_location = None
    chrome_driver = os.path.join(os.path.dirname(__file__), 'Scripts', 'chromedriver.exe')
    firefox_driver = os.path.join(os.path.dirname(__file__), 'Scripts', 'geckodriver.exe')
    edge_driver = os.path.join(os.path.dirname(__file__), 'Scripts', 'msedgedriver.exe')
    safari_driver = None
default_timeout = 5


if not os.path.exists(chrome_driver):
    chrome_driver = None
if not os.path.exists(firefox_driver):
    firefox_driver = None
if not os.path.exists(edge_driver):
    edge_driver = None
if not safari_driver or not os.path.exists(safari_driver):
    safari_driver = None


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

def safari_cfg_options(safari_options: SafariOptions):
    if safari_driver:
        safari_options.add_argument('-headless')
        # safari_options.headless = True
        return safari_options
    else:
        return None