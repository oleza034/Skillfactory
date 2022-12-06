from settings import base_url, auth_path
from .base_page import BasePage
from .locators import AuthLocators
from selenium import webdriver


class AuthPage(BasePage):
    def __init__(self, driver: webdriver, timeout: float = 10):
        url = base_url + auth_path
        super().__init__(driver, url, timeout)
        driver.get(url)
        self.email = driver.find_element(*AuthLocators.AUTH_EMAIL)
        self.password = driver.find_element(*AuthLocators.AUTH_PASS)
        self.btn = driver.find_element(*AuthLocators.AUTH_BTN)

    def enter_email(self, value: str):
        self.email.send_keys(value)

    def enter_password(self, value: str):
        self.password.send_keys(value)

    def btn_click(self):
        self.btn.click()
