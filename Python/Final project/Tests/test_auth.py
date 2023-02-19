import os
from datetime import datetime

import pytest
from selenium import webdriver
from Pages.auth_page import AuthPage
from settings import DEFAULT_WIDTH, DEFAULT_HEIGHT, conf_chrome, conf_firefox, conf_safari, conf_edge, \
    ValidData as Valid, rnd_str, DELETE_UNNEEDED_SCREENSHOTS
from time import sleep


def get_captcha() -> str:
    return input('Please provide captcha: ')


# ADD 'safari' when testing not on Mac
@pytest.fixture(params=['chrome', 'firefox', 'edge'], scope='session')  # , 'safari'], scope='function')
def init_driver(request, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT):
    """
    initialize webdriver
    """
    web_driver = None
    if request.param == 'firefox':
        firefox_options = conf_firefox()
        web_driver = webdriver.Firefox(options=firefox_options)
    elif request.param == 'chrome':
        chrome_options = conf_chrome()
        web_driver = webdriver.Chrome(options=chrome_options)
    elif request.param == 'edge':
        edge_options = conf_edge()
        web_driver = webdriver.Edge(options=edge_options)
    elif request.param == 'safari':
        safari_options = conf_safari()
        assert safari_options, 'Cannot run test with Safari browser. Make sure you\'re using Mac with Safari browser'
        web_driver = webdriver.Safari(options=safari_options)
    if web_driver:
        web_driver.set_window_size(width, height)

    yield web_driver

    web_driver.close()


@pytest.mark.parametrize('auth_type,username,password,expectation',
                         [('phone', 'valid phone', 'valid', True),
                          ('mail', 'valid email', 'valid', True),
                          # ('login', 'valid login', 'valid', True),
                          # ('ls', 'valid ls', 'valid', True),
                          # ('', '', '', False),
                          ('mail', 'valid email', '', False),
                          # ('phone', 'valid email', 'valid', False),
                          # ('phone', '7', rnd_str(10), False),
                          # ('mail', '@. ', rnd_str(), False),
                          ('mail', f'{rnd_str(5, "l")}@{rnd_str(7, "l")}.{rnd_str(3, "l")}', rnd_str(), False),
                          ('phone', rnd_str(20, 'd'), rnd_str(), False),
                          # ('mail', f'{rnd_str(64), "l"}@{rnd_str(128, "l")}.{rnd_str(128, "l")}', False),
                          ],
                         ids=[
                             'positive test with valid phone',
                             'positive test with valid email',
                             # 'positive test with valid login',
                             # 'positive test with valid LS',
                             # 'negative test with empty data',
                             'negative test with empty password'
                             # 'negative test with wrong auth_type',
                             # 'negative test with short phone number',
                             # 'negative test with invalid email address',
                             'negative test with unregistered email address',
                             'negative test with long phone number',
                             # 'negative test with long email address',
                         ])
def test_auth_page(init_driver, auth_type, username, password, expectation):
    # print(f'{datetime.now().strftime("%M:%S.%f")}: starting test')
    screenshots = []
    # Get valid data from .env file...
    valid = Valid()
    if 'valid' in username and username[:5] == 'valid':
        if 'phone' in username or username == 'valid' and auth_type == 'phone':
            username = valid.phone
        elif 'mail' in username or username == 'valid' and auth_type in ['mail', 'email']:
            username = valid.email
        elif 'username' in username or username == 'valid' and auth_type == 'login':
            username = valid.login
        elif 'ls' in username or username == 'valid' and auth_type == 'ls':
            username = valid.ls

        #make sure we got the right value
        if not username:
            pytest.xfail(f'Cannot get valid_{auth_type} from .env file.')
        elif username[:5] == 'valid':
            pytest.xfail(f'cannot determine the type of valid username. Incorrect auth = {auth_type}.')
    # Take valid password, if needed
    if password[:5] == 'valid':
        password = valid.password
        if not password or password[:5] == 'valid':
            pytest.xfail('Cannot get valid_password from .env file.')

    #Print test data
    # print(f'{datetime.now().strftime("%M:%S.%f")}: test data determined')
    # print(f'auth = \'{auth_type}\', username = \'{username}\', password = \'{password}\', expectation = {expectation}')
    page = AuthPage(init_driver)
    page.log.append('=' * 30)
    page.log.append(f' {"Positive" if expectation else "Negative"} test of AuthPage with:')
    page.log.append(f'   auth = \'{auth_type}\', username = \'{username}\', password = \'{password}\'')
    # print(f'{datetime.now().strftime("%M:%S.%f")}: test log written')

    # Change auth type when needed
    if auth_type == 'email':
        auth_type = 'mail'
    assert auth_type in ['phone', 'mail', 'login', 'ls'], f'incorrect test \'auth\' param = {auth_type}'

    # fill the form, take screenshot, send data and take another screenshot after form is submitted
    page.fill_auth_form(auth_type, username, password)
    if s := page.save_screenshot():
        screenshots.append(s)
    page.btn_click()
    if s := page.save_screenshot():
        screenshots.append(s)

    if expectation and '/auth/' in page.get_current_url():
        page.log.append(f'  Test failed: Auth succeeded when expected to fail.')
        assert False, 'Auth succeeded when expected to fail.'
    elif not expectation and '/auth/' not in page.get_current_url():
        page.log.append(f'  Test failed: Auth failed when expected to succeed.')
        assert '/auth/' in page.get_current_url(), 'Auth failed when expected tu succeed.'
        # print(f'{datetime.now().strftime("%M:%S.%f")}: test done')

    # delete screenshots if test has passed
    if DELETE_UNNEEDED_SCREENSHOTS:
        for s in screenshots:
            os.remove(s)
