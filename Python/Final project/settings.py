import os
from pathlib import Path
import random
from selenium.webdriver import ChromeOptions, FirefoxOptions, EdgeOptions
from selenium.webdriver.safari.options import Options as SafariOptions
from dotenv import load_dotenv
from datetime import datetime
from shutil import rmtree

DEFAULT_TIMEOUT = 10.0
CAPTCHA_TIMEOUT = 30.0
BASE_URL = 'https://b2c.passport.rt.ru/'
AUTH_COOKIES = 'auth_cookies.dat'
auth_data_filename = os.path.join('tests', 'test_data_login.json')
LOGGED = True
DEFAULT_WIDTH = 1600
DEFAULT_HEIGHT = 900
CAPTCHA_WARNING = os.path.join(os.path.dirname(__file__), 'sounds', 'captcha_warning.mp3')
BANNED_TIMEOUT = 10
BANNED_ATTEMPTS = 10
TS_FORMAT = '%Y-%m-%d_%H-%M'
TIME_FORMAT = '%H:%M:%S' # %f = fractional second part, microseconds, 6 digits. Not needed
SLEEP_TIME = 1
WIPE_OLD_LOGS = True

def get_log_file_folder_names(log_folder_name='log', wipe_old_data=False) -> (str, str):
    ts = datetime.now().strftime(TS_FORMAT)
    folder_name = os.path.join(os.path.dirname(__file__), log_folder_name)
    if wipe_old_data:
        rmtree(folder_name, ignore_errors=True)
    path = Path(folder_name)
    path.mkdir(parents=True, exist_ok=True)
    folder_name = os.path.join(folder_name, f'%slog_{ts}')
    log_file = os.path.join(folder_name, f'%slog_{ts}.txt')
    return log_file, folder_name


def conf_chrome() -> ChromeOptions:
    chrome_options = ChromeOptions()
    chrome_options.add_argument('no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    # chrome_options.add_argument('--headless')
    # chrome_options.headless = True
    return chrome_options


def conf_edge() -> EdgeOptions:
    edge_options = EdgeOptions()
    edge_options.add_argument('no-sandbox')
    edge_options.add_argument('--disable-gpu')
    # edge_options.add_argument('--headless')
    # edge_options.headless = True
    return edge_options


def conf_firefox() -> FirefoxOptions:
    firefox_options = FirefoxOptions()
    # firefox_options.add_argument('-headless')
    return firefox_options


def conf_safari() -> (SafariOptions, None):
    try:
        safari_options = SafariOptions()
        # safari_options.add_argument('-headless')
        return safari_options
    except:
        return None


def rnd_str(length:int=15, symbols='ld'):
    """
    generates str of specified length
    :param length: length of generated string
    :param symbols: types of symbols. Default 'ld'.
        - 'l' - Latin letters,
        - 'd' - digits,
        - 's' - special symbols (ASCII)
        - 'r' - Russian letters
        - 'u' - some of non-ASCII letters(Thai, Hebrew)
    :return:
    """
    if type(length) != int or type(symbols) != str:
        return ''
    for s in symbols:
        if s not in 'ldsru':
            return ''.join(random.choices(symbols, k = length))
    l = 'qwertyuiopasdfghjklzxcvbnm' #letters
    d = '0123456789' # digits
    s = '~`!@#$%^&*()\\|/.,"\';:?[]{}' # special symbols
    r = 'йцукенгшщзхъфывапролджэячсмитьбю'
    u = 'ႠႡႢႣႤႥႦႧႨႩႪႫႬႭႯႰႱႲႳႴႵႶႷႸႹႺႻႼႽႾႿჀჁჂჃჄჅჇჍაბგდევზთიკლმნოპჟრსტუ฿ფ'
    string = l + l.upper() if 'l' in symbols else ''
    string += d if 'd' in symbols else ''
    string += s if 's' in symbols else ''
    string += r + r.upper() if 'r' in symbols else ''
    string += u + u.upper() if 'u' in symbols else ''
    return ''.join(random.choices(string, k = length))

def rnd(max_value=15):
    return random.randint(0, max_value - 1)

class ValidData:
    email = None
    password = None
    phone = None
    login = None
    ls = None

    def __init__(self):
        load_dotenv()
        self.email = os.getenv('valid_email')
        self.password = os.getenv('valid_password')
        self.phone = os.getenv('valid_phone')
        self.login = os.getenv('valid_login')
        self.ls = os.getenv('valid_ls')

if LOGGED:
    log_folder, log_file_name = get_log_file_folder_names('log', WIPE_OLD_LOGS)
else:
    log_folder, log_file_name = '', ''
