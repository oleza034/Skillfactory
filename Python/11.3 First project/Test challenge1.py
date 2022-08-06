from selenium import webdriver
from selenium.webdriver.common.by import By
import time


def test(txt: str):
    """This functions pastes your txt input into the form and submits it"""
    time.sleep(1)

    el = web.find_element(By.XPATH, "//*[@id=\"firstname\"]")
    el.send_keys(txt)

    submit = web.find_element(By.XPATH, "//*[@name=\"formSubmit\"]")
    submit.click()


def test1(txt: str):
    """Special test 1: double click submit button"""
    time.sleep(1)

    el = web.find_element(By.XPATH, "//*[@id=\"firstname\"]")
    el.send_keys(txt)

    submit = web.find_element(By.XPATH, "//*[@name=\"formSubmit\"]")
    submit.click()
    submit.click()


web = webdriver.Chrome()
web.get('http://testingchallenges.thetestingmap.org/index.php')

# Normal value
test('User')

# Characters other than letters
test('User1')

# Empty value
test('')

# Mimimal value
test('K')

# Maximum length
test('qwertyuiopasdfghjklzxcvbnmpoiu')

# More than maximum length
test('qwertyuiopasdfghjklzxcvbnmpoiui')
test(' ')
test('User 2')
test(u'юзверь')
test('user1 ')
test(' User')

# this does not result to a new type of test but should be tested
test1('User')

time.sleep(10)
web.close()