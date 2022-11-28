import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.safari.options import Options as SafariOptions
import pytest
from settings import base_url, chrome_cfg_options, firefox_cfg_options, edge_cfg_options, valid_email, valid_password, \
    default_timeout, safari_cfg_options


@pytest.fixture(params=['chrome', 'firefox', 'edge'], scope='function')  # , 'safari'], scope='function')
def init_driver(request):
    """
    initialize webdriver
    """
    web_driver = None
    if request.param == 'firefox':
        firefox_options = firefox_cfg_options(webdriver.FirefoxOptions())
        assert firefox_options, 'Cannot run test on Firefox browser'
        web_driver = webdriver.Firefox(options=firefox_options)
    elif request.param == 'chrome':
        chrome_options = chrome_cfg_options(webdriver.ChromeOptions())
        assert chrome_options, 'Cannot run test on Chrome browser'
        web_driver = webdriver.Chrome(options=chrome_options)
    elif request.param == 'edge':
        edge_options = edge_cfg_options(webdriver.EdgeOptions())
        assert edge_options, 'Cannot run test on Safari browser'
        web_driver = webdriver.Edge(options=edge_options)
    elif request.param == 'safari':
        safari_options = safari_cfg_options(SafariOptions())
        assert safari_options, 'Cannot run test on Safari browser'
        web_driver = webdriver.Safari(options=safari_options)
    web_driver.implicitly_wait(default_timeout)

    yield web_driver
    web_driver.close()


@pytest.mark.usefixtures('init_driver')
@pytest.fixture
def my_pets(init_driver):
    """
    login user and load my_pets page
    """
    init_driver.get(base_url + 'login')

    # add email
    field_email = init_driver.find_element(By.ID, "email")
    if '@' not in field_email.get_attribute('value'):
        field_email.clear()
        field_email.send_keys(valid_email)

    # add password
    field_pass = init_driver.find_element(By.ID, "pass")
    if not field_pass.get_attribute('value'):
        field_pass.clear()
        field_pass.send_keys(valid_password)

    btn_submit = init_driver.find_element(By.XPATH, "//button[@type='submit']")
    btn_submit.click()

    my_pets_btn = init_driver.find_element(By.XPATH, '//a[contains(@href, "my_pets")]')
    assert my_pets_btn.is_enabled()
    my_pets_btn.click()


    # pets_created = create_pets(init_driver)

    yield init_driver

    # if pets_created:
    #     delete_pets(init_driver)


@pytest.mark.usefixtures('my_pets')
def test_1(my_pets: (webdriver.Chrome | webdriver.Edge | webdriver.Firefox)):
    assert my_pets.current_url == base_url + 'my_pets'
    txt = my_pets.find_element(By.XPATH, '//div[contains(@class,".col-sm-4")]').text
    animal_count = int(txt[txt.index(' ', txt.index('Питомцев:')) + 1:txt.index('\n', txt.index('Питомцев:'))])
    assert type(animal_count) == int and animal_count, 'Pets list is empty'
    pets = []
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
