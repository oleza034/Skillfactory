import selenium.webdriver.remote.webelement

from base_page import WebPage
from locators import RegLocators as Loc
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from settings import DEFAULT_TIMEOUT, AUTH_COOKIES, BASE_URL, LOGGED, rnd
from elements import WebElement, ManyWebElements
from time import sleep

class RegPage(WebPage):
    is_banned = False
    first_name: webdriver.remote.webelement = None
    last_name: webdriver.remote.webelement = None
    region: webdriver.remote.webelement = None
    username: webdriver.remote.webelement = None
    password: webdriver.remote.webelement = None
    password2: webdriver.remote.webelement = None
    btn_submit: webdriver.remote.webelement = None
    url = BASE_URL

    def __init__(self, driver: webdriver, timeout = DEFAULT_TIMEOUT, cookies_file = AUTH_COOKIES, logged = LOGGED):
        print('initialization started...')
        # First, open BASE_URL
        if not self._page_loaded(driver):
            super().__init__(driver, self.url, timeout, cookies_file, logged, self.__class__.__name__)
            # The find and click the registration link
            reg_link = driver.find_element(*Loc.REG_LINK)
            reg_link.click()
            # Save current URL (it is needed in tests to make sure registration succeeded or failed)
            self.url = driver.current_url or BASE_URL
            # if driver.find_element()
            self.populate_items(driver)

    def _page_loaded(self, driver:webdriver):
        url = driver.current_url
        if not url or BASE_URL not in url or '?' not in url or '&' not in url or 'execution=' in url \
                or '/registration?' not in url:
            return False
        err_msg = driver.find_elements(*Loc.ERROR_HINT)
        if err_msg and len(err_msg):
            return False
        try:
            self.populate_items(driver)
        except:
            return False
        return True

    def populate_items(self, driver: webdriver):
        driver.implicitly_wait(.1)
        find = driver.find_element
        finds = driver.find_elements
        try:
            if find(*Loc.BANNED_TEXT):
                self.is_banned = True
        except NoSuchElementException:
            self.is_banned = False
        driver.implicitly_wait(self._timeout)

        self.first_name = find(*Loc.FIRST_NAME)
        self.last_name = find(*Loc.LAST_NAME)
        self.region = find(*Loc.REGION)
        self.username = find(*Loc.EMAIL)
        self.password = find(*Loc.PASSWORD)
        self.password2 = find(*Loc.PASSWORD2)
        self.btn_submit = find(*Loc.BTN_SUBMIT)

    def select_region(self, region: (int | str | None)) -> (str | None):
        """
        Opens list with regions and clicks the region by its index or text
        :param region: index or text to be clicked
        :return: new region's name or None if region has not been changed
        """
        # click region to open regions list
        if region == None:
            return self.region.text
        self.region.click()
        wait = WebDriverWait(self._web_driver, DEFAULT_TIMEOUT)
        try:
            # try to find redion list elements
            reg_items = self._web_driver.find_elements(*Loc.REGION_LIST_ITEMS)
            # check if region should be chosen randomly
            if region in ['rnd', 'random', 'rand']:
                if reg_items and len(reg_items):
                    region = rnd(len(reg_items))
                else:
                    self._web_driver.find_element(*Loc.REGIONS_BTN).click()
                    return self.region.text
            # check if region should be the last in the list
            elif region in ['max', 'last']:
                if reg_items and len(reg_items):
                    region = len(reg_items) - 1
                else:
                    region = 0
            elif region in ['min', 'first']:
                if reg_items and len(reg_items):
                    region = 0
            region_texts = [r.text.lower() for r in reg_items]
            if region in region_texts:
                region = region_texts.index(region)
            elif type(region) == str:
                for r in region_texts:
                    if type(region) == str and region.lower() in r:
                        region = region_texts.index(region.lower())
            if type(region) == int and reg_items and len(reg_items) and region in range(len(reg_items)):
                # if index is provided, and it is in range, click corresponded menu item
                new_region = '' + reg_items[region].text
                reg_items[region].click()
                return new_region
            self._web_driver.implicitly_wait(.1)
            try:
                if self._web_driver.find_elements(*Loc.REGION_LIST_ITEMS):
                    self._web_driver.find_element(*Loc.REGIONS_BTN).click()
            except NoSuchElementException:
                pass
            self._web_driver.implicitly_wait(self._timeout)
            return self.region.text
        except NoSuchElementException:
            return self.region.text

    def check_cookies(self):
        if not self._web_driver.get_cookies() and self._cookies and (cookies := self._cookies.get_cookies()):
            for cookie in cookies:
                self._web_driver.add_cookie(cookie)

    def has_errors(self) -> bool:
        errors = self._web_driver.find_elements(*Loc.ERROR_HINT)
        if errors and len(errors):
            return True
        return False

    def reload(self):
        self.get(self.url)
        self.populate_items(self._web_driver)

    def check_code_input_container(self) -> bool:
        """Checks if page contains input code locator and returns True or False depending on result"""
        self._web_driver.implicitly_wait(0)
        try:
            container = self._web_driver.find_element(*Loc.CODE_INPUT)
        except NoSuchElementException:
            self._web_driver.implicitly_wait(self._timeout)
            return False
        self._web_driver.implicitly_wait(self._timeout)
        return True

    def check_account_exist(self) -> bool:
        """Checks if account exist warning appeared"""
        self._web_driver.implicitly_wait(0)
        try:
            elem = self._web_driver.find_element(*Loc.ACCOUNT_EXISTS)
            return True
        except NoSuchElementException:
            return False