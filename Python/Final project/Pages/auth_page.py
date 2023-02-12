from time import sleep
from settings import BASE_URL, AUTH_COOKIES, DEFAULT_TIMEOUT, CAPTCHA_TIMEOUT, LOGGED
from base_page import WebPage
from locators import AuthLocators as Loc
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


class AuthPage(WebPage):
    is_banned = False
    login = None
    password = None
    captcha = None
    btn = None
    by_phone = None
    by_email = None
    by_login = None
    by_ls = None
    login_type = None
    error_msg = None
    _url = BASE_URL

    def __init__(self, driver: webdriver, timeout: float = DEFAULT_TIMEOUT, cookies_file = AUTH_COOKIES,
                 logged = LOGGED):
        url = self._url # + AUTH_PATH
        super().__init__(driver, url, timeout, cookies_file, logged, self.__class__.__name__)
        if not self.populate_elements():
            sleep(1)
            self.get(url)
            self.populate_elements()

    def populate_elements(self):
        # Check whether user is banned
        self._web_driver.implicitly_wait(.1)
        try:
            if self._web_driver.find_element(*Loc.BANNED_TEXT):
                self.is_banned = True
                return False
        except NoSuchElementException:
            self.is_banned = False

        # Check if the user is already logged in
        try:
            logout = self._web_driver.find_element(*Loc.LOGOUT)
            if logout: logout.click()
        except:
            logout = None
        self._web_driver.implicitly_wait(self._timeout)

        try:
            self.login = self._web_driver.find_element(*Loc.AUTH_LOGIN) # login field: either phone, username, login or ls
        except NoSuchElementException:
            return False
        self.password = self._web_driver.find_element(*Loc.AUTH_PASS)
        self.btn = self._web_driver.find_element(*Loc.AUTH_BTN)

        # auth type switches
        self.by_phone = self._web_driver.find_element(*Loc.BY_PHONE)
        self.by_email = self._web_driver.find_element(*Loc.BY_EMAIL)
        self.by_login = self._web_driver.find_element(*Loc.BY_LOGIN)
        self.by_ls = self._web_driver.find_element(*Loc.BY_LS)
        self._web_driver.implicitly_wait(.1)
        try:
            self.error_msg = self._web_driver.find_element(*Loc.ERROR_MSG)
        except:
            self.error_msg = None
        self._web_driver.implicitly_wait(self._timeout)

        # active auth type switch
        self.login_type = self._web_driver.find_element(*Loc.ACTIVE_LOGIN).get_attribute('value')
        return True

    def check_cookies(self):
        if not self._web_driver.get_cookies() and self._cookies and (cookies := self._cookies.get_cookies()):
            for cookie in cookies:
                self._web_driver.add_cookie(cookie)

    def enter_login(self, value: str):
        self.login.send_keys(value)

    def enter_password(self, value: str):
        self.password.send_keys(value)

    def btn_click(self):
        # Check captcha
        self._web_driver.implicitly_wait(0.1)
        try:
            # if captcha requested, click the field and give user time to deal with it
            captcha = self._web_driver.find_element(*Loc.CAPTCHA)
            captcha.click()
            sleep(CAPTCHA_TIMEOUT)
        except NoSuchElementException:
            captcha = None
        self._web_driver.implicitly_wait(self._timeout)
        self.btn.click()
        self.check_cookies()

    def select_login_type(self, new_login, timeout = DEFAULT_TIMEOUT) -> bool:
        """
        changes auth type on page
        :param new_login: *must* be one of following: ['phone', 'username', 'login', 'ls']
        :param timeout:
        :return:
        """
        if new_login.lower() not in ['phone', 'mail', 'login', 'ls']:
            print('incorrect selector')
            return False
        if self.login_type.lower() == new_login.lower():
            print('selector already active')
            return True

        print(f'switching login from {self.login_type} to {new_login}...')
        if new_login.lower() == 'phone':
            self.by_phone.click()
        elif new_login.lower() in ['username', 'mail']:
            self.by_email.click()
        elif new_login.lower() == 'login':
            self.by_login.click()
        else:
            self.by_ls.click()

        i = 0
        while i < 10:
            self.login_type = self._web_driver.find_element(*Loc.ACTIVE_LOGIN).get_attribute('value')
            if self.login_type.lower() == new_login.lower() \
                    or 'mail' in self.login_type.lower() and 'mail' in new_login.lower():
                return True
            else:
                i += 1
                sleep(.5)

        print(f'login not changed. Current login: \'{self.login_type}\' != \'{new_login}\'')
        return True
