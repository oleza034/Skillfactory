from urllib.parse import urlparse
from selenium import webdriver


class BasePage(object):
    def __init__(self, driver: webdriver, url: str, timeout:float = 10):
        self.driver = driver
        self.url = url
        self.driver.implicitly_wait(timeout)

    def get_relative_link(self):
        url = urlparse(self.driver.current_url)
        return url.path
