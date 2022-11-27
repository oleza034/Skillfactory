import os
import platform
# import random

import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytest
from settings import base_url, chrome_cfg_options, firefox_cfg_options, edge_cfg_options, safari_cfg_options, \
    default_timeout, valid_email, valid_password


def wait_find_element(driver: (webdriver.Chrome | webdriver.Edge | webdriver.Firefox), locator,
                      condition: str = None, timeout: int = default_timeout):
    if condition not in ['elem_visibility', 'presence_of_all', 'elem_clickable']:
        cond = EC.presence_of_element_located(locator)
    elif condition == 'elem_visibility':
        cond = EC.visibility_of_element_located(locator)
    elif condition == 'presence_of_all':
        cond = EC.presence_of_all_elements_located(locator)
    else:
        cond = EC.element_to_be_clickable(locator)

    return WebDriverWait(driver, timeout).until(cond)


@pytest.fixture(params=['chrome', 'firefox', 'edge', 'safari'], scope='function',)
# @pytest.fixture(params=['firefox'], scope='function')
def init_driver(request):
    """
    initialize webdriver
    """
    web_driver = None
    if request.param == 'firefox':
        firefox_options = firefox_cfg_options(webdriver.FirefoxOptions())
        web_driver = webdriver.Firefox(options=firefox_options)
    elif request.param == 'chrome':
        chrome_options = chrome_cfg_options(webdriver.ChromeOptions())
        web_driver = webdriver.Chrome(options=chrome_options)
    elif request.param == 'edge':
        edge_options = edge_cfg_options(webdriver.EdgeOptions())
        web_driver = webdriver.Edge(options=edge_options)
    elif request.param == 'safari':
        safari_options = safari_cfg_options(SafariOptions())
        if safari_options:
            web_driver = webdriver.Safari(options=safari_options)
        else:
            web_driver = None
    if web_driver:
        web_driver.maximize_window()

    yield web_driver
    if web_driver:
        web_driver.close()


@pytest.mark.usefixtures('init_driver')
@pytest.fixture
def my_pets(init_driver):
    """
    login user and load my_pets page
    """
    if not init_driver:
        return None

    init_driver.get(base_url + 'login')

    # add email
    field_email = wait_find_element(init_driver, (By.ID, 'email'))
    field_email.clear()
    field_email.send_keys(valid_email)

    # add password
    field_pass = wait_find_element(init_driver, (By.ID, 'pass'))
    field_pass.clear()
    field_pass.send_keys(valid_password)

    btn_submit = wait_find_element(init_driver, (By.XPATH, "//button[@type='submit']"), 'elem_clickable')
    btn_submit.click()

    try:
        my_pets_btn = wait_find_element(init_driver, (By.XPATH, '//a[contains(@href, "my_pets")]'), 'elem_clickable')
    except selenium.common.exceptions.TimeoutException:
        assert False, 'Cannot click \'My Pets\' button'
    else:
        my_pets_btn.click()

    # pets_created = create_pets(init_driver)

    yield init_driver

    # if pets_created:
    #     delete_pets(init_driver)


@pytest.mark.usefixtures('my_pets')
def test_1(my_pets: (webdriver.Chrome | webdriver.Edge | webdriver.Firefox | SafariOptions)):
    if not my_pets:
        return True
    assert my_pets.current_url == base_url + 'my_pets'
    txt = wait_find_element(my_pets, (By.XPATH, '//div[contains(@class,".col-sm-4")]')).text
    animal_count = int(txt[txt.index(' ', txt.index('Питомцев:')) + 1:txt.index('\n', txt.index('Питомцев:'))])
    assert type(animal_count) == int and animal_count, 'Pets list is empty'
    pets = []
    assert wait_find_element(my_pets, (By.XPATH, '//*[@id="all_my_pets"]//tbody/tr/*'), 'presence_of_all')
    pet_rows = len(my_pets.find_elements(By.XPATH, '//div[@id="all_my_pets"]//tbody/tr'))
    assert pet_rows == animal_count, 'Pets count dismatch or element by XPATH found incorrectly'
    for i in range(1, pet_rows + 1):
        img = my_pets.find_element(By.XPATH, f'//div[@id="all_my_pets"]//tbody//tr[{i}]//img').get_attribute('src')[:31]
        name = my_pets.find_element(By.XPATH, f'//div[@id="all_my_pets"]//tbody//tr[{i}]/td[1]').text
        animal_type = my_pets.find_element(By.XPATH, f'//div[@id="all_my_pets"]//tbody//tr[{i}]/td[2]').text[:31]
        age = my_pets.find_element(By.XPATH, f'//div[@id="all_my_pets"]//tbody//tr[{i}]/td[3]').text[:31]
        pets.append({'img': img, 'name': name, 'type': animal_type, 'age': age})
    assert len([p for p in pets if type(p) == dict and 'img' in p.keys() and p['img']]) >= int(.1 + animal_count / 2), \
        'too many pets without photo'
    for p in pets:
        assert p['name'], 'Pet has missing name'
        assert [p['name'] for p in pets].count(p['name']) == 1, f'pet\'s name \'{p["name"]}\' is not unique!'
        assert p['type'], 'Pet has missing animal type'
        assert p['age'], 'Pet has missing age'
