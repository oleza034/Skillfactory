from selenium.webdriver.common.by import By

class BaseLoc:
    # put common locators here
    BANNED_TEXT = (By.XPATH, '//*[contains(text(), "Ваш запрос был отклонен из соображений безопасности.")]')
    BY_PHONE = (By.ID, 't-btn-tab-phone')
    BY_EMAIL = (By.ID, 't-btn-tab-mail')
    BY_LOGIN = (By.ID, 't-btn-tab-login')
    BY_LS = (By.ID, 't-btn-tab-ls')
    AUTH_LOGIN = (By.ID, 'username')

class AuthLocators(BaseLoc):
    AUTH_PASS = (By.ID, 'password')
    AUTH_BTN = (By.ID, 'kc-login')
    ACTIVE_LOGIN = (By.NAME, 'tab_type')
    CAPTCHA = (By.ID, 'captcha')
    ERROR_MSG = (By.ID, 'form-error-message')
    LOGOUT = (By.ID, 'logout-btn')

class RegLocators(BaseLoc):
    REG_LINK = (By.ID, 'kc-register')
    FIRST_NAME = (By.NAME, 'firstName')
    LAST_NAME = (By.NAME, 'lastName')
    REGION = (By.XPATH, '//div[@class="rt-select rt-select--search register-form__dropdown"]//input[@class="rt-inp' \
              'ut__input rt-input__input--rounded rt-input__input--orange"]')
    REGION_LIST_ITEMS = (By.XPATH, '//div[@class="rt-select rt-select--search register-form__dropdown"]' \
                         '//div[@class="rt-select__list-item"]')
    REGIONS_BTN = (By.XPATH, '//div[@class="rt-select rt-select--search register-form__dropdown"]'
                             '//div[@class="rt-input__action"]')
    EMAIL = (By.ID, 'address')
    PASSWORD = (By.ID, 'password')
    PASSWORD2 = (By.ID, 'password-confirm')
    BTN_SUBMIT = (By.XPATH, '//form[@class="register-form"]//button[@type="submit"]')
    ERROR_HINT = (By.XPATH, '//span[@class="rt-input-container__meta rt-input-container__meta--error"]')
    CODE_INPUT = (By.CSS_SELECTOR, 'div.code-input-container')
    ACCOUNT_EXISTS = (By.XPATH, '//h2[contains(text(),"Учётная запись уже существует")]')

class RecoverLocators(BaseLoc):
    FORGOT_PWD_LINK = (By.ID, 'forgot_password')
    CAPTCHA = (By.ID, 'captcha')
    CAPTCHA_IMAGE = (By.ID, 'rt-captcha__image')
    CONTINUE_BTN = (By.ID, 'reset')
    ACTIVE_LOGIN = (By.NAME, 'tab_type')
    ERROR_MSG = (By.ID, 'form-error-message')
    RESET_CHOICE_FORM = (By.CSS_SELECTOR, 'form.reset-choice-form')


"""
list with towns: $$('rt-select__list-wrapper rt-select__list-wrapper--rounded')
List items: $$('div.rt-select__list-item')
selected value: $$(div.rt-select__list-item rt-select__list-item--active')
"""