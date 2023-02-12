from settings import BASE_URL, DEFAULT_TIMEOUT, CAPTCHA_TIMEOUT, AUTH_COOKIES, LOGGED
from base_page import WebPage
from locators import RecoverLocators as Loc
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
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

    def __init__(self, driver: webdriver, timeout: float = DEFAULT_TIMEOUT, cookies_file = AUTH_COOKIES, logged = LOGGED):
        url = BASE_URL
        super().__init__(driver, url, timeout, cookies_file, logged, self.__class__.__name__)
        self.populate_elements()

    def populate_elements(self):
        self._web_driver.implicitly_wait(.1)
        try:
            if self._web_driver.find_element(*Loc.BANNED_TEXT):
                self.is_banned = True
        except NoSuchElementException:
            self.is_banned = False
        self._web_driver.implicitly_wait(self._timeout)

        # mail elements
        self.login = self._web_driver.find_element(*Loc.AUTH_LOGIN) # login field: either phone, username, login or ls
        self.captcha = self._web_driver.find_element(*Loc.CAPTCHA)
        self.btn_continue = self._web_driver.find_element(*Loc.CONTINUE_BTN)

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

    def select_login_type(self, new_login, timeout = DEFAULT_TIMEOUT) -> bool:
        """
        changes auth type on page
        :param new_login: *must* be one of following: ['PHONE', 'EMAIL', 'LOGIN', 'LS']
        :param timeout:
        :return:
        """
        if new_login not in ['PHONE', 'EMAIL', 'LOGIN', 'LS']:
            # print('incorrect selector')
            return False
        if self.login_type == new_login:
            # print('selector already active')
            return True

        # print(f'switching login from {self.login_type} to {new_login}...')
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
                # print('login type changed successfully')
                return True
            else:
                i += 1
                sleep(.5)

        # print(f'login not changed. Current login: \'{self.login_type}\' != \'{new_login}\'')
        return True

    def fill_captcha(self, captcha_text: (str | None) = None, timeout=CAPTCHA_TIMEOUT):
        """
        Fill captcha with captcha_text or wait for user to provide captcha
        :param captcha_text: fill captcha with captcha_text (assumed to be incorrect) or, if None provided,
               wait for user's input
        :param timeout: timeout used to wait for user's input
        :return:
        """
        # cannot implement. Using just sleep by timeout
        if type(captcha_text) == str:
            if captcha_text:
                self.captcha.send_keys(captcha_text)
        else:
            self.captcha.send_keys('please_provide_captcha')
            sleep(timeout)

    def fill_form(self, login_type, login, captcha=None, timeout=CAPTCHA_TIMEOUT):
        self.select_login_type(login_type.upper())
        self.login.send_keys(login)
        self.fill_captcha(captcha, timeout)
        self.btn_continue.click()