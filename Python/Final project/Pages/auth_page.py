from datetime import datetime
from Pages.elements import WebElement
from time import sleep
from settings import BASE_URL, AUTH_COOKIES, DEFAULT_TIMEOUT, CAPTCHA_TIMEOUT, LOGGED
from Pages.base_page import WebPage
from Pages.locators import AuthLocators as Loc
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Keys


class AuthPage(WebPage):
    is_banned = False
    username = None
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
        # print(f'{datetime.now().strftime("%M:%S.%f")}: init stated...')
        url = self._url # + AUTH_PATH
        super().__init__(driver, url, timeout, cookies_file, logged, self.__class__.__name__)
        if not self.populate_elements():
            sleep(1)
            self.get(url)
            self.populate_elements()
            # print(f'{datetime.now().strftime("%M:%S.%f")}: init done.')

    def populate_elements(self):
        # Check whether user is banned
        # print(f'{datetime.now().strftime("%M:%S.%f")}: populating elements...')
        self._web_driver.implicitly_wait(.1)
        try:
            if self._web_driver.find_element(*Loc.BANNED_TEXT):
                self.is_banned = True
                # print(f'{datetime.now().strftime("%M:%S.%f")}: error')
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
            # username field: either phone, mail, login or ls
            self.username = self._web_driver.find_element(*Loc.AUTH_LOGIN)
        except NoSuchElementException:
            # print(f'{datetime.now().strftime("%M:%S.%f")}: error2.')
            return False
        self.password = self._web_driver.find_element(*Loc.AUTH_PASS)
        self.btn = self._web_driver.find_element(*Loc.AUTH_BTN)

        # auth type switches
        self.by_phone = self._web_driver.find_element(*Loc.BY_PHONE)
        self.by_email = self._web_driver.find_element(*Loc.BY_EMAIL)
        self.by_login = self._web_driver.find_element(*Loc.BY_LOGIN)
        self.by_ls = self._web_driver.find_element(*Loc.BY_LS)
        # active auth type switch
        self.login_type = self._web_driver.find_element(*Loc.ACTIVE_LOGIN).get_attribute('value')

        # Try to find error message and captcha
        self._web_driver.implicitly_wait(.1)
        try:
            self.error_msg = self._web_driver.find_element(*Loc.ERROR_MSG)
        except:
            self.error_msg = None
        try:
            self.captcha = self._web_driver.find_element(*Loc.CAPTCHA)
        except NoSuchElementException:
            self.captcha = None
        self._web_driver.implicitly_wait(self._timeout)
        # print(f'{datetime.now().strftime("%M:%S.%f")}: done')
        return True

    def check_cookies(self):
        # print(f'{datetime.now().strftime("%M:%S.%f")}: checking cookies')
        if not self._web_driver.get_cookies() and self._cookies and (cookies := self._cookies.get_cookies()):
            for cookie in cookies:
                self._web_driver.add_cookie(cookie)
        # print(f'{datetime.now().strftime("%M:%S.%f")}: done')

    def safe_clear_and_fill_username(self, value: str):
        # print(f'{datetime.now().strftime("%M:%S.%f")}: entering \'{value}\' into username...')
        old_txt = self.username.get_attribute('value')
        # print(f'old_txt = \'{old_txt}\'')
        if old_txt:
            self.username.clear()
            WebDriverWait(self._web_driver, .5).until_not(EC.text_to_be_present_in_element_value(Loc.AUTH_LOGIN, old_txt))
        if value:
            self.username.send_keys(value)
        # print(f'{datetime.now().strftime("%M:%S.%f")}: done')

    def btn_click(self):
        # print(f'{datetime.now().strftime("%M:%S.%f")}: clicking button')
        self.btn.click()
        self.check_cookies()
        # print(f'{datetime.now().strftime("%M:%S.%f")}: done')

    def select_login_type(self, new_login, timeout = DEFAULT_TIMEOUT) -> bool:
        """
        changes auth type on page
        :param new_login: *must* be one of following: ['phone', 'username', 'username', 'ls']
        :param timeout:
        :return:
        """
        # print(f'{datetime.now().strftime("%M:%S.%f")}: selecting login type: {new_login}')
        if new_login.lower() not in ['phone', 'mail', 'username', 'ls']:
            self.log.append(f'{datetime.now().strftime("%M:%S.%f")}: invalid auth_type in test data: {new_login}")')
            # print(f'{datetime.now().strftime("%M:%S.%f")}: done')
            return False
        if self.login_type.lower() == new_login.lower():
            # print('selector already active')
            # print(f'{datetime.now().strftime("%M:%S.%f")}: done')
            return True

        # print(f'switching username from {self.login_type} to {new_login}...')
        if new_login.lower() == 'phone':
            self.by_phone.click()
        elif new_login.lower() in ['username', 'mail']:
            self.by_email.click()
        elif new_login.lower() == 'username':
            self.by_login.click()
        else:
            self.by_ls.click()

        i = 0
        while i < 10:
            self.login_type = self._web_driver.find_element(*Loc.ACTIVE_LOGIN).get_attribute('value')
            if self.login_type.lower() == new_login.lower() \
                    or 'mail' in self.login_type.lower() and 'mail' in new_login.lower():
                # print(f'{datetime.now().strftime("%M:%S.%f")}: done')
                return True
            else:
                i += 1
                sleep(.5)

        # print(f'username not changed. Current username: \'{self.login_type}\' != \'{new_login}\'')
        # print(f'{datetime.now().strftime("%M:%S.%f")}: done')
        return True

    def fill_auth_form(self, auth_type: str, username: str, password: str):
        # print(f'{datetime.now().strftime("%M:%S.%f")}: filling the form...')
        self.select_login_type(auth_type)
        self.safe_clear_and_fill_username(username)
        self.password.clear()
        self.password.send_keys(password)
        try:
            self._web_driver.implicitly_wait(.1)
            self.captcha = self._web_driver.find_element(*Loc.CAPTCHA)
            self.captcha.send_keys('pls enter...')
            self.captcha.send_keys(Keys.CONTROL, 'a')
            sleep(CAPTCHA_TIMEOUT)
        except NoSuchElementException:
            pass
        self._web_driver.implicitly_wait(self._timeout)
        # print(f'{datetime.now().strftime("%M:%S.%f")}: done')
