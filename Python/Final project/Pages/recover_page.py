from settings import BASE_URL, DEFAULT_TIMEOUT, CAPTCHA_TIMEOUT, AUTH_COOKIES, LOGGED
from Pages.base_page import WebPage
from Pages.locators import RecoverLocators as Loc
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from time import sleep


class RecoverPage(WebPage):
    login = None
    captcha = None
    btn_continue = None
    by_phone = None
    by_email = None
    by_login = None
    by_ls = None
    login_type = None
    error_msg = None
    is_banned = None
    reset_choose_form = None

    def __init__(self, driver: webdriver, timeout: float = DEFAULT_TIMEOUT, cookies_file = AUTH_COOKIES, logged = LOGGED):
        url = BASE_URL
        super().__init__(driver, url, timeout, cookies_file, logged, self.__class__.__name__)
        self.populate_elements()

    def populate_elements(self):
        driver = self._web_driver
        driver.implicitly_wait(.1)
        try:
            if driver.find_element(*Loc.BANNED_TEXT):
                self.is_banned = True
        except NoSuchElementException:
            self.is_banned = False

        driver.implicitly_wait(self._timeout)

        try:
            # First, we need to follow 'forgot password' link
            driver.find_element(*Loc.FORGOT_PWD_LINK).click()
        except NoSuchElementException:
            return None

        # mail elements
        self.login = driver.find_element(*Loc.AUTH_LOGIN) # username field: either phone, username, username or ls
        self.captcha = driver.find_element(*Loc.CAPTCHA)
        self.btn_continue = driver.find_element(*Loc.CONTINUE_BTN)

        # auth type switches
        self.by_phone = driver.find_element(*Loc.BY_PHONE)
        self.by_email = driver.find_element(*Loc.BY_EMAIL)
        self.by_login = driver.find_element(*Loc.BY_LOGIN)
        self.by_ls = driver.find_element(*Loc.BY_LS)

        driver.implicitly_wait(.1)
        try:
            self.error_msg = driver.find_element(*Loc.ERROR_MSG)
        except NoSuchElementException:
            self.error_msg = None
        try:
            self.reset_choose_form = driver.find_element(*Loc.RESET_CHOICE_FORM)
        except NoSuchElementException:
            self.reset_choose_form = None
        driver.implicitly_wait(self._timeout)

        # active auth type switch
        self.login_type = driver.find_element(*Loc.ACTIVE_LOGIN).get_attribute('value')

    def select_login_type(self, new_login, timeout = DEFAULT_TIMEOUT) -> bool:
        """
        changes auth type on page
        :param new_login: *must* be one of following: ['PHONE', 'EMAIL', 'LOGIN', 'LS']
        :param timeout:
        :return:
        """
        if new_login not in ['PHONE', 'MAIL', 'EMAIL', 'LOGIN', 'LS']:
            # print('incorrect selector')
            return False
        if self.login_type == new_login:
            # print('selector already active')
            return True

        # print(f'switching username from {self.login_type} to {new_login}...')
        if new_login == 'PHONE':
            self.by_phone.click()
        elif new_login in ['EMAIL', 'MAIL']:
            self.by_email.click()
        elif new_login == 'LOGIN':
            self.by_login.click()
        else:
            self.by_ls.click()

        # print('waiting for selector to be active')
        i = 0
        while i < 10:
            self.login_type = self._web_driver.find_element(*Loc.ACTIVE_LOGIN).get_attribute('value')
            if self.login_type == new_login:
                # print('username type changed successfully')
                return True
            else:
                i += 1
                sleep(.5)

        # print(f'username not changed. Current username: \'{self.login_type}\' != \'{new_login}\'')
        return True

    def fill_captcha(self, captcha_text: (str | None) = None, timeout=CAPTCHA_TIMEOUT) -> str:
        """
        Fill captcha with captcha_text or wait for user to provide captcha
        :param captcha_text: fill captcha with captcha_text (assumed to be incorrect) or, if None provided,
               wait for user's input
        :param timeout: timeout used to wait for user's input
        :return: screenshot file name
        """
        # cannot implement. Using just sleep by timeout
        self.captcha.clear()
        if type(captcha_text) == str:
            self.captcha.send_keys(captcha_text)
        else:
            self.captcha.send_keys('pls enter...')
            self.captcha.send_keys(Keys.CONTROL, 'a')
            sleep(CAPTCHA_TIMEOUT)

    def fill_and_submit_form(self, auth_type, username, captcha=None, timeout=CAPTCHA_TIMEOUT):
        self.select_login_type(auth_type.upper())
        self.login.send_keys(username)
        self.fill_captcha(captcha, timeout)

    def form_sent_successfully(self, expectation: bool) -> str:
        """Checks whether data is sent successfully and returns error message or '' in case test passed"""
        driver = self._web_driver
        driver.implicitly_wait(.1)
        try:
            if driver.find_element(*Loc.AUTH_LOGIN):
                try:
                    if err := driver.find_element(*Loc.ERROR_MSG):
                        driver.implicitly_wait(self._timeout)
                        if expectation:
                            return f'incorrect form submission: {err.text}'
                except NoSuchElementException:
                    driver.implicitly_wait(self._timeout)
                    if expectation:
                        return 'form hasn\'t been submitted'
        except NoSuchElementException:
            driver.implicitly_wait(self._timeout)
            if not expectation:
                return 'form has been submitted successfully in negative test'

        driver.implicitly_wait(self._timeout)
        return ''