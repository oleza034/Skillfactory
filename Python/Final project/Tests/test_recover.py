import os

import pytest
from selenium import webdriver
from Pages.recover_page import RecoverPage
from settings import DEFAULT_WIDTH, DEFAULT_HEIGHT, conf_chrome, conf_firefox, conf_safari, conf_edge, rnd_str, \
    ValidData as Valid, DELETE_UNNEEDED_SCREENSHOTS
from time import sleep


# ADD 'safari' when testing not on Mac
@pytest.fixture(params=['chrome', 'firefox', 'edge'], scope='session')  # , 'safari'], scope='session')
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


@pytest.mark.parametrize('auth_type,username,captcha,description,expectation',
                         [
                             ('email', 'valid email', None, 'Positive test with valid email', True),
                             ('phone', 'valid phone', None, 'Positive test with valid phone number', True),
                             # ('username', 'valid username', None, 'Positive test with valid username', True),
                             # ('ls', 'valid ls', None, 'Positive test with valid account number', True),
                             ('email', 'valid phone', None, 'Negative test with wrong auth type', False),
                             ('email', 'valid email', '', 'Negative test with empty captcha', False),
                             ('phone', 'valid phone', rnd_str(), 'Negative test with empty username and wrong captcha',
                              False),
                             # ('email', 'adsfkjh@troiue.dk', None, 'Negative test with unregistered email address',
                             #  False),
                             # ('phone', '39485', None, 'Negative test with short phone number', False),
                             # ('phone', rnd_str(256, 'd'), None, 'Negative test with long phone number', False)
                             # ('email', rnd_str(64) + '@' +
                             #  '.'.join([rnd_str(64), rnd_str(64), rnd_str(64), rnd_str(64)]),
                             #  None, 'Negative test with long email address', False),
                             # ('username', rnd_str(15, 'ls'), None, 'Negative test with special symbols in username', False),
                             # ('email', 'Василий@Пупкин.рф', None,
                             # 'Negative test with Russian symbols in email address', False),
                         ],
                         ids=[
                             'Positive test with valid email',
                             'Positive test with valid phone number',
                             # 'Positive test with valid username',
                             # 'Positive test with valid account number',
                             'Negative test with wrong auth type',
                             'Negative test with empty captcha',
                             'Negative test with empty username and wrong captcha',
                             # 'Negative test with unregistered email address',
                             # 'Negative test with short phone number',
                             # 'Negative test with long phone number',
                             # 'Negative test with long email address',
                             # 'Negative test with special symbols in username',
                             # 'Negative test with Russian symbols in email address',
                         ])
def test_recover(init_driver, auth_type:str, username: str, captcha: (str | None), description: str, expectation: bool):
    """
    Test of password recover form. Please note that test REQUIRES operator to manually enter captcha for each test.
    :param auth_type: must be one of following: 'phone', 'email', 'username', 'ls'
    :param username: text of username. Special cases: 'valid phone', 'valid email', 'valid username', 'valid ls'
    :param captcha: text to paste in Captcha. if None, user must manually enter captcha for CAPTCHA_TIMEOUT seconds
    :param description: test description used in log file
    :param expectation: True if test is positive or False otherwise
    """
    # Screenshots that saved during the test. If test passed, screenshots are deleted.
    # Otherwise, screenshots are reported in log
    screenshots = []

    # get valid data from settings
    valid = Valid()
    if 'valid' in username and username[:5] == 'valid':
        if 'phone' in username or username == 'valid' and auth_type == 'phone':
            username = valid.phone
        elif 'mail' in username or username == 'valid' and auth_type in ['mail', 'username']:
            username = valid.email
        elif 'username' in username or username == 'valid' and auth_type == 'username':
            username = valid.login
        elif 'ls' in username or username == 'valid' and auth_type == 'ls':
            username = valid.ls

        # make sure we got the right value
        # For instance if we don't have valid test data
        if not username:
            pytest.xfail(f'Cannot get valid_{auth_type} from .env file.')
        elif 'valid' in username and username.index('valid') == 0:
            pytest.xfail(f'cannot determine the type of valid username. Incorrect auth_type = {auth_type}.')

    # Initialize Recover page and log file
    page = RecoverPage(init_driver)
    page.log.append('=' * 30)
    page.log.append(f'{"Positive" if expectation else "Negative"} test of Recover page with:')
    if description:
        page.log.append(f'  {description}')
    page.log.append(f'  - auth_type = {auth_type}, username = {username}, and '
                    f'{"incorrect" if captcha else ("valid" if captcha is None else "empty")} captcha')
    # Fill test data and submit form
    page.fill_and_submit_form(auth_type, username, captcha)
    if s:= page.save_screenshot():
        screenshots.append(s)
    page.btn_continue.click()

    # Check results
    result = page.form_sent_successfully(expectation)
    if s := page.save_screenshot():
        screenshots.append(s)

    if result:
        page.log.append(f'  ... FAILED: {result}')
        if screenshots:
            page.log.append(f'  Screenshot{"s" if len(screenshots) > 1 else ""} taken:')
            for s in screenshots:
                page.log.append(f'  - {s}')
        assert False, result
    page.log.append('  ... OK')

    # delete screenshots for passed test
    if DELETE_UNNEEDED_SCREENSHOTS:
        for s in screenshots:
            if os.path.exists(s):
                os.remove(s)
    elif screenshots:
        page.log.append(f'  Screenshot{"s" if len(screenshots) > 1 else ""} taken:')
        for s in screenshots:
            page.log.append(f'  - {s}')
