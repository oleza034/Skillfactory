import os

import pytest
from selenium import webdriver
from Pages.auth_page import AuthPage
from settings import DEFAULT_WIDTH, DEFAULT_HEIGHT, conf_chrome, conf_firefox, conf_safari, conf_edge, \
    ValidData as Valid, rnd_str
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


@pytest.mark.parametrize('auth_type,login,password,expectation',
                         [('phone', 'valid phone', 'valid', True),
                          ('mail', 'valid username', 'valid', True),
                          ('login', 'valid login', 'valid', True),
                          ('ls', 'valid ls', 'valid', True),
                          ('phone', 'valid username', 'valid', False),
                          ('mail', '123456', rnd_str(10), False)])
def test_auth_page(init_driver, auth_type, login, password, expectation):
    screenshots = []
    # Get valid data from .env file...
    valid = Valid()
    if 'valid' in login and login[:5] == 'valid':
        if 'phone' in login or login == 'valid' and auth_type == 'phone':
            login = valid.phone
        elif 'mail' in login or login == 'valid' and auth_type in ['mail', 'username']:
            login = valid.email
        elif 'login' in login or login == 'valid' and auth_type == 'login':
            login = valid.login
        elif 'ls' in login or login == 'valid' and auth_type == 'ls':
            login = valid.ls

        #make sure we got the right value
        if not login:
            pytest.xfail(f'Cannot get valid_{auth_type} from .env file.')
        elif 'valid' in login and login.index('valid') == 0:
            pytest.xfail(f'cannot determine the type of valid login. Incorrect auth = {auth_type}.')
    if 'valid' in password and password.index('valid') == 0:
        password = valid.password
        if 'valid' in password or not password:
            pytest.xfail('Cannot get valid_password from .env file.')

    #Print test data
    print(f'auth = \'{auth_type}\', login = \'{login}\', password = \'{password}\', expectation = {expectation}')
    page = AuthPage(init_driver)
    page.log.append(f' {"Positive" if expectation else "Negative"} test of AuthPage with:')
    page.log.append(f'   auth = \'{auth_type}\', login = \'{login}\', password = \'{password}\'')

    # Change auth type when needed
    if auth_type == 'username':
        auth_type = 'mail'
    assert auth_type in ['phone', 'mail', 'login', 'ls'], f'incorrect test \'auth\' param = {auth_type}'
    assert page.select_login_type(auth_type)

    page.login.send_keys(login)
    page.password.send_keys(password)
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

    # delete screenshots if test has passed
    for s in screenshots:
        os.remove(s)
