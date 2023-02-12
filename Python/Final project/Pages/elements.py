#!/usr/bin/python3
# -*- encoding=utf8 -*-

import time
import selenium
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from settings import DEFAULT_TIMEOUT


class WebElement(object):

    _locator = ('', '')
    _web_driver = None
    _page = None
    _timeout = DEFAULT_TIMEOUT
    _wait_after_click = False

    def __init__(self, timeout=_timeout, wait_after_click=False, **kwargs):
        self._timeout = timeout
        self._wait_after_click = wait_after_click

        for attr in kwargs:
            self._locator = (str(attr).replace('_', ' '), str(kwargs.get(attr)))

    def find(self, timeout=_timeout):
        """ Find element on the page. """

        try:
            element = WebDriverWait(self._web_driver, timeout).until(
               EC.presence_of_element_located(self._locator)
            )
        except:
            print('Element not found on the page!')
            element = None

        return element

    def wait_to_be_clickable(self, timeout=_timeout, check_visibility=True):
        """ Wait until the element will be ready for click. """

        try:
            element = WebDriverWait(self._web_driver, timeout).until(
                EC.element_to_be_clickable(self._locator)
            )
        except:
            print('Element not clickable!')
            element = None

        if check_visibility:
            self.wait_until_not_visible()

        return element

    def is_clickable(self):
        """ Check is element ready for click or not. """

        element = self.wait_to_be_clickable(timeout=0.1)
        return element is not None

    def is_presented(self):
        """ Check that element is presented on the page. """

        element = self.find(timeout=0.1)
        return element is not None

    def is_visible(self):
        """ Check is the element visible or not. """

        element = self.find(timeout=0.1)

        if element:
            return element.is_displayed()

        return False

    def wait_until_not_visible(self, timeout=_timeout):

        element = None
        wait = WebDriverWait(self._web_driver, timeout)

        try:
            element = wait.until(EC.visibility_of_element_located(self._locator))
        except:
            print('Element not visible!')

        if element:
            js = ('return (!(arguments[0].offsetParent === null) && '
                  '!(window.getComputedStyle(arguments[0]) === "none") &&'
                  'arguments[0].offsetWidth > 0 && arguments[0].offsetHeight > 0'
                  ');')
            visibility = self._web_driver.execute_script(js, element)
            iteration = 0

            while not visibility and iteration < 10:
                time.sleep(0.5)

                iteration += 1

                visibility = self._web_driver.execute_script(js, element)
                print('Element {0} visibility: {1}'.format(self._locator, visibility))

        return element

    def send_keys(self, keys, timeout=_timeout):
        """ Send keys to the element. """

        keys = keys.replace('\n', '\ue007')

        element = self.find()

        if element:
            element.click()
            element.clear()
            element.send_keys(keys)
            try:
                WebDriverWait(self._web_driver, timeout).until((EC.text_to_be_present_in_element_value, keys))
            except Exception:
                print(f'Cannot send keys to element {self._locator}')
            # time.sleep(wait)
        else:
            msg = 'Element with locator {0} not found'
            raise AttributeError(msg.format(self._locator))

    def get_text(self):
        """ Get text of the element. """

        element = self.find()
        text = ''

        try:
            text = str(element.text)
        except Exception as e:
            print('Error: {0}'.format(e))

        return text

    def get_attribute(self, attr_name):
        """ Get attribute of the element. """

        element = self.find()

        if element:
            return element.get_attribute(attr_name)

    def _set_value(self, web_driver, value, clear=True):
        """ Set value to the input element. """

        element = self.find()

        if clear:
            element.clear()

        element.send_keys(value)

    def click(self, hold_seconds=0, x_offset=1, y_offset=1, centered=False):
        """ Wait and click the element. """

        element = self.wait_to_be_clickable()
        if centered:
            x_offset, y_offset = element.size['width'] * .5, element.size['height'] * .5

        if element:
            action = ActionChains(self._web_driver)
            action.move_to_element_with_offset(element, x_offset, y_offset).\
                pause(hold_seconds).click(on_element=element).perform()
        else:
            msg = 'Element with locator {0} not found'
            raise AttributeError(msg.format(self._locator))

        if self._wait_after_click:
            self._page.wait_page_loaded()

    def right_mouse_click(self, x_offset=0, y_offset=0, hold_seconds=0):
        """ Click right mouse button on the element. """

        element = self.wait_to_be_clickable()

        if element:
            action = ActionChains(self._web_driver)
            action.move_to_element_with_offset(element, x_offset, y_offset). \
                pause(hold_seconds).context_click(on_element=element).perform()
        else:
            msg = 'Element with locator {0} not found'
            raise AttributeError(msg.format(self._locator))

    def highlight_and_make_screenshot(self, file_name='element.png'):
        """ Highlight element and make the screenshot of all page. """

        element = self.find()

        # Scroll page to the element:
        self._web_driver.execute_script("arguments[0].scrollIntoView();", element)

        # Add red border to the style:
        self._web_driver.execute_script("arguments[0].style.border='3px solid red'", element)

        # Make screen-shot of the page:
        self._web_driver.save_screenshot(file_name)

    def scroll_to_element(self):
        """ Scroll page to the element. """

        element = self.find()

        # Scroll page to the element:
        # Option #1 to scroll to element:
        # self._web_driver.execute_script("arguments[0].scrollIntoView();", element)

        # Option #2 to scroll to element:
        try:
            element.send_keys(Keys.DOWN)
        except Exception as e:
            pass  # Just ignore the error if we can't send the keys to the element

    def delete(self):
        """ Deletes element from the page. """

        element = self.find()

        # Delete element:
        self._web_driver.execute_script("arguments[0].remove();", element)

    def wait_for_disappear(self, timeout=DEFAULT_TIMEOUT):
        wait = WebDriverWait(self._web_driver, timeout)
        wait.until_not(EC.presence_of_element_located(self._locator))


class ManyWebElements(WebElement):

    def __getitem__(self, item):
        """ Get list of elements and try to return required element. """

        elements = self.find()
        return elements[item]

    def find(self, timeout=DEFAULT_TIMEOUT):
        """ Find elements on the page. """

        elements = []

        try:
            elements = WebDriverWait(self._web_driver, timeout).until(
               EC.presence_of_all_elements_located(self._locator)
            )
        except:
            print('Elements not found on the page!')

        return elements

    def _set_value(self, web_driver: selenium.webdriver, value):
        """ Note: this action is not applicable for the list of elements. """
        raise NotImplemented('This action is not applicable for the list of elements')

    def click(self, hold_seconds=0, x_offset=0, y_offset=0, centered=False):
        """ Note: this action is not applicable for the list of elements. """
        raise NotImplemented('This action is not applicable for the list of elements')

    def count(self):
        """ Get count of elements. """

        elements = self.find()
        return len(elements)

    def get_text(self):
        """ Get text of elements. """

        elements = self.find()
        result = []

        for element in elements:
            text = ''

            try:
                text = str(element.text)
            except Exception as e:
                print('Error: {0}'.format(e))

            result.append(text)

        return result

    def get_attribute(self, attr_name):
        """ Get attribute of all elements. """

        results = []
        elements = self.find()

        for element in elements:
            results.append(element.get_attribute(attr_name))

        return results

    def highlight_and_make_screenshot(self, file_name='element.png'):
        """ Highlight elements and make the screenshot of all page. """

        elements = self.find()

        for element in elements:
            # Scroll page to the element:
            self._web_driver.execute_script("arguments[0].scrollIntoView();", element)

            # Add red border to the style:
            self._web_driver.execute_script("arguments[0].style.border='3px solid red'", element)

        # Make screenshot of the page:
        self._web_driver.save_screenshot(file_name)
