#!/usr/bin/python3
# -*- encoding=utf8 -*-

import time
import os
import selenium
from selenium.webdriver import chrome, firefox, edge, safari
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from settings import DEFAULT_TIMEOUT, LOGGED, TIME_FORMAT, SLEEP_TIME, log_folder, log_file_name
from logger import Logger, MyCookies
from Pages.elements import WebElement
from pathlib import Path
from datetime import datetime


class WebPage(object):

    _web_driver: selenium.webdriver = None
    _cookies: (MyCookies | None) = None
    log = None
    _timeout = 0
    logged = LOGGED
    log_file_name = ''
    log_location = ''
    _screenshot_number = 1

    def __init__(self, web_driver: selenium.webdriver, url='about:blank', timeout: float = DEFAULT_TIMEOUT,
                 cookies_file = 'page_coolies.dat', logged = LOGGED, log_prefix = ''):
        """
        Initializes a base page
        """
        self._web_driver = web_driver
        self._web_driver.implicitly_wait(timeout)
        self._timeout = timeout
        self.logged = logged
        self.get(url, False)
        if logged:
            # get timed file / folder names for logs and screenshots. Add module name if needed (log_prefix)
            prefix = log_prefix + '_' if log_prefix else ''
            self.log_file_name = log_file_name % (prefix, prefix)
            self.log_location = log_folder % prefix
            print(f'started logger in {self.log_file_name}')
            self.log = Logger(self.log_file_name, False)
            self.log.append('=' * 30)
            self.log.append(f'{datetime.strftime(datetime.now(), "")} Open page: {url}')
        if c := self._web_driver.get_cookies():
            self._cookies = MyCookies(cookies_file, c)

    def get(self, url, logged=logged):
        if self._cookies and (cookies := self._cookies.get_cookies()):
            for cookie in cookies:
                self._web_driver.add_cookie(cookie)
        if logged:
            time_stamp = datetime.now().strftime(TIME_FORMAT)
            self.log.append(f'{time_stamp}: Open page: {url}')
            self.save_screenshot()
        self._web_driver.get(url)
        self.wait_page_loaded()

    def go_back(self):
        self._web_driver.back()
        self.wait_page_loaded()

    def refresh(self):
        self._web_driver.refresh()
        self.wait_page_loaded()

    def save_screenshot(self, file_name='', logged=logged):
        time_stamp = datetime.now().strftime(TIME_FORMAT.replace(':', '-'))
        if not file_name:
            # Generate screenshot name based on time_stamp
            file_name = f'{self.__class__.__name__}_screenshot_{time_stamp}_{self._screenshot_number}'
            self._screenshot_number += 1
            file_name = os.path.join(self.log_location, file_name)
        # make sure the screenshots folder exists
        path = Path(os.path.dirname(file_name))
        try:
            path.mkdir(parents=True, exist_ok=True)
        except FileExistsError:
            pass

        # check if screenshot with such a name is already taken

        if self._web_driver.save_screenshot(file_name + '.png'):
            message = 'screenshot taken:'
        else:
            message = 'failed to take screenshot:'

        if message == 'screenshot taken:':
            return file_name + '.png'
        else:
            return None

    def scroll_down(self, offset=0):
        """ Scroll the page down. """

        if offset:
            self._web_driver.execute_script('window.scrollTo(0, {0});'.format(offset))
        else:
            self._web_driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')

    def scroll_up(self, offset=0):
        """ Scroll the page up. """

        if offset:
            self._web_driver.execute_script('window.scrollTo(0, -{0});'.format(offset))
        else:
            self._web_driver.execute_script('window.scrollTo(0, -document.body.scrollHeight);')

    def switch_to_iframe(self, iframe):
        """ Switch to iframe by it's name. """

        self._web_driver.switch_to.frame(iframe)

    def switch_out_iframe(self):
        """ Cancel iframe focus. """
        self._web_driver.switch_to.default_content()

    def get_current_url(self):
        """ Returns current browser URL. """

        return self._web_driver.current_url

    def get_page_source(self):
        """ Returns current page body. """

        source = ''
        try:
            source = self._web_driver.page_source
        except:
            print('Can not get page source')

        return source

    def check_js_errors(self, ignore_list=None):
        """ This function checks JS errors on the page. """

        ignore_list = ignore_list or []

        logs = self._web_driver.get_log('browser')
        for log_message in logs:
            if log_message['level'] != 'WARNING':
                ignore = False
                for issue in ignore_list:
                    if issue in log_message['message']:
                        ignore = True
                        break

                assert ignore, 'JS error "{0}" on the page!'.format(log_message)

    def wait_page_loaded(self, timeout=60, check_js_complete=True,
                         check_page_changes=False, check_images=False,
                         wait_for_element=None,
                         wait_for_xpath_to_disappear='',
                         sleep_time=SLEEP_TIME):
        """ This function waits until the page will be completely loaded.
            We use different ways to detect is page loaded or not:

            1) Check JS status
            2) Check modification in source code of the page
            3) Check that all images uploaded completely
               (Note: this check is disabled by default)
            4) Check that expected elements presented on the page
        """

        page_loaded = False
        double_check = False
        k = 0

        if sleep_time:
            time.sleep(sleep_time)

        # Get source code of the page to track changes in HTML:
        source = ''
        try:
            source = self._web_driver.page_source
        except:
            pass

        # Wait until page loaded (and scroll it, to make sure all objects will be loaded):
        while not page_loaded:
            time.sleep(0.5)
            k += 1

            if check_js_complete:
                # Scroll down and wait when page will be loaded:
                try:
                    self._web_driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                    page_loaded = self._web_driver.execute_script("return document.readyState == 'complete';")
                except Exception as e:
                    pass

            if page_loaded and check_page_changes:
                # Check if the page source was changed
                new_source = ''
                try:
                    new_source = self._web_driver.page_source
                except:
                    pass

                page_loaded = new_source == source
                source = new_source

            # Wait when some element will disappear:
            if page_loaded and wait_for_xpath_to_disappear:
                bad_element = None

                try:
                    bad_element = WebDriverWait(self._web_driver, 0.1).until(
                        EC.presence_of_element_located((By.XPATH, wait_for_xpath_to_disappear))
                    )
                except:
                    pass  # Ignore timeout errors

                page_loaded = not bad_element

            if page_loaded and wait_for_element:
                try:
                    page_loaded = WebDriverWait(self._web_driver, 0.1).until(
                        EC.element_to_be_clickable(wait_for_element._locator)
                    )
                except:
                    pass  # Ignore timeout errors

            assert k < timeout, 'The page loaded more than {0} seconds!'.format(timeout)

            # Check two times that page completely loaded:
            if page_loaded and not double_check:
                page_loaded = False
                double_check = True

        # Go up:
        self._web_driver.execute_script('window.scrollTo(document.body.scrollHeight, 0);')

    def scroll_to_bottom(self):
        self._web_driver.executeScript("window.scrollBy(0,document.body.scrollHeight)", "")

    def get_cookies(self):
        return self._web_driver.get_cookies()