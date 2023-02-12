import os

import pytest
from selenium import webdriver
from Pages.reg_page import RegPage
from settings import DEFAULT_WIDTH, DEFAULT_HEIGHT, conf_chrome, conf_firefox, conf_safari, conf_edge, rnd_str, \
    screenshot_folder_name
from time import sleep


# ADD 'safari' when testing not on Mac
# @pytest.fixture(params=['chrome', 'firefox', 'edge'], scope='session')  # , 'safari'], scope='session')
@pytest.fixture(params=['chrome'], scope='session')
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


@pytest.mark.parametrize('first_name,last_name,region,username,password,password2,expectation',
                         [
                             ('Марья', 'Петровна', 'Владивосток', '+79991235689', 'dxoOd386', 'same', True),
                             ('Максим', 'Квакин', 'rnd', 'max_kvakin@ya.ya.ru', 'boWu2Mx601', 'same', True),
                             ('Василий', 'Иваныч', 0, '+79112223344', rnd_str(), 'same', False),
                             ('User', 'Lastname', 'last', 'user@mail.com', rnd_str(), 'same', False),
                             ('Супер', 'Админ', 'rnd', 'admin@rt.ru', 'passkey', 'same', False),
                         ],
                         ids = [
                             'Positive registration by phone number', 'Positive registration by email',
                             'Registration with taken username', 'Negative test with invalid names',
                             'Negative test with weak password'
                         ])
def test_reg_page(init_driver, first_name: str, last_name: str, region, username, password, password2, expectation: bool):
    """Test of RegPage"""
    screenshots = []
    if password2 == 'same':
        password2 = password
    page = RegPage(init_driver)
    page.select_region(region)
    region = page.region.text
    page.log.append(f' {"Positive" if expectation else "Negative"} test of RegPage with:')
    page.log.append(f'   first_name = \'{first_name}\', last_name = \'{last_name}\', region = \'{region}\',')
    page.log.append(f'   username = \'{username}\', password = \'{password}\', password2 = \'{password2}\'')
    page.first_name.clear()
    page.first_name.send_keys(first_name)
    page.last_name.clear()
    page.last_name.send_keys(last_name)
    page.username.clear()
    page.username.send_keys(username)
    page.password.clear()
    page.password.send_keys(password)
    page.password2.clear()
    page.password2.send_keys(password2)

    if s := page.save_screenshot():
        screenshots.append(s)
    page.btn_submit.click()
    if s := page.save_screenshot():
        screenshots.append(s)

    chk = page.check_code_input_container()
    if chk == expectation:
        for s in screenshots:
            if os.path.exists(s):
                os.remove(s)
        page.log.append('    ... ok')
    else:
        page.log.append('   ... failed')
        screenshots = set(screenshots)
        if screenshots:
            page.log.append('   Screenshots taken:')
        for s in screenshots:
            page.log.append('   - ' + s)
        if expectation:
            assert False, "Registration failed on positive test"
        assert False, "Registration succeeded on negative test"