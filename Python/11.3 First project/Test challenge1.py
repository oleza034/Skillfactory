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

# space
test(' ')

# Space in the middle
test('User 2')

# Space in the end
test('user1 ')

# Space in the beginning
test(' User')

# Non-ASCII value
test(u'юзверь')

# HTML tags
test('<i>Mighty user</i>')

# Basic SQL injection
test('test\'test;')

# Basic XSS
test('<script></script>')

# Missing CSS link
test('detailsoverviewnow.css')

# Looked at the page source
test('dfjwGGe82H43g3uRiy53h')

# Test the cookie
test('oi32jnxd42390slk345')

# Test admin rights
adm = web.find_element(By.XPATH, '//*[@name=\'user_right_as_admin\']')
web.execute_script('''
    var elem = arguments[0];
    var value = arguments[1];
    elem.value = value;
''', adm, '1')
test('admin')

time.sleep(10)
web.close()