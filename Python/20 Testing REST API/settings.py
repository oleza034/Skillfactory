from dotenv import load_dotenv
import os
from requests import get

def exp_key(email: str, password: str, key1: str, key2: str) -> str:
    """
    determine which of 2 keys is expired and returns it. IMPORTANT: both keys must belong to email registered in system
    :param email: registered in PetFriends email address
    :param password: correct password for email
    :param key1: auth_key 1
    :param key2: auth_key 2
    :return: either key1 or key2 in case one is expired, or '' in case keys are wrong or authenication went wrong
    """
    # get correct API key to know which one of 2 keys return as invalid
    resp = get(base_url + 'api/key', headers={'email': email, 'password': password, 'accept': 'application/json'})
    if resp.status_code == 200 and resp.headers['Content-Type'] == 'application/json':
        j = resp.json()
        if type(j) == dict and 'key' in j.keys():
            key = j['key']
        else:
            key = ''
        if key and key1 and key != key1:
            return key1
        if key and key2 and key != key2:
            return key2
    return ''

def broken_photo(name='images/good_file.txt'):
    file_name = os.path.join(os.path.dirname(__file__), name)
    try:
        with open(file_name) as f:
            broken_file = f.read()
            broken_file = broken_file[:-1]
            f.close()
    except Exception:
        broken_file = ''
    return broken_file


load_dotenv()

# variables from .env file
valid_email = os.getenv('valid_email')
valid_password = os.getenv('valid_password')
email2 = os.getenv('email2')
password2 = os.getenv('password2')
base_url = 'https://petfriends.skillfactory.ru/'

# other variables
api_key1 = 'd8b2ab76e42f5370ca3a8ea8265117a42d71b48a62d29766d34784e2' # key expired long ago
api_key2 = ''
expired_api_key = exp_key(valid_email, valid_password, api_key1, api_key2)
correct_photo_path = 'images'
correct_photo = 'correct_photo.jpg'
large_photo = 'large_photo.jpg'
text_file = 'text.txt'
