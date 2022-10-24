from api import *
from datetime import datetime, timedelta
from settings import valid_email, valid_password, expired_api_key
from requests_toolbelt import MultipartEncoder
from urllib.parse import quote_plus


path = 'api/pets/'
global_headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
auth_key = get_key()
if auth_key[:6] == 'ERROR:':
    auth_key = ''


def get_pet(api_key: str = auth_key, index: int = 0) -> dict:
    """
    Returns the 1st pet
    :param api_key: API key to authorize
    :param id: API response with pets
    :return: pet's data as dict. If pet's not found, returns dict with 'id' key which is equal to pet_id
    """
    # prepare and send request to get my_pets
    headers = {'accept': 'application/json', 'auth_key': api_key,
               'Content-Type': 'application/x-www-form-urlencoded'}
    params = {'filter': 'my_pets'}
    status, _, resp = request('get', 'api/pets', headers=headers, params=params)
    if status == 200 and type(resp) == dict and 'pets' in resp.keys() and type(resp['pets']) == list:
        pets = resp['pets']
        if len(pets):
            return pets[index if 0 >= index > len(pets) else 0]
        else:
            body = {'name': 'Kitty', 'animal_type': 'cat', 'age': 2}
            status, _, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
            if status == 200 and type(resp) == dict:
                return resp
    return {'error': 'something went wrong'}


def test_1_positive(api_key=auth_key):
    pet = get_pet()
    #check we've got correct pet. Otherwise display error message
    if 'id' not in pet.keys() or 'name' not in pet.keys() or 'animal_type' not in pet.keys() or 'age' not in pet.keys():
        assert pet == {'id': '*', 'name': '*', 'animal_type': '*', 'age': '*'}
    assert pet['id']
    # get new pet's data
    headers = global_headers | {'auth_key': api_key}
    t = datetime.now()
    status, headers, resp = request('delete', path + pet['id'], headers=headers)
    assert status == 200
    assert datetime.now() - t < timedelta(seconds=1)


def test_2_pet_id_of_different_user(api_key=auth_key):
    pet = get_pet()
    #check we've got correct pet. Otherwise display error message
    if 'id' not in pet.keys() or 'name' not in pet.keys() or 'animal_type' not in pet.keys() or 'age' not in pet.keys():
        assert pet == {'id': '*', 'name': '*', 'animal_type': '*', 'age': '*'}
    assert pet['id']
    # get new pet's data
    headers = global_headers | {'auth_key': get_key(2)}
    t = datetime.now()
    status, headers, resp = request('delete', path + pet['id'], headers=headers)
    assert status == 403
    assert 'Content-Type' in headers.keys() and headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_3_missing_pet_id(api_key=auth_key):
    pet = get_pet()
    #check we've got correct pet. Otherwise display error message
    if 'id' not in pet.keys() or 'name' not in pet.keys() or 'animal_type' not in pet.keys() or 'age' not in pet.keys():
        assert pet == {'id': '*', 'name': '*', 'animal_type': '*', 'age': '*'}
    assert pet['id']
    # get new pet's data
    headers = global_headers | {'auth_key': api_key}
    t = datetime.now()
    status, headers, resp = request('delete', path + pet['id'], headers=headers)
    assert status == 400
    assert 'Content-Type' in headers.keys() and headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_4_invalid_pet_id(api_key=auth_key, pet_id='asdf'):
    headers = global_headers | {'auth_key': api_key}
    t = datetime.now()
    status, headers, resp = request('delete', path + pet_id, headers=headers)
    assert status == 400
    assert 'Content-Type' in headers.keys() and headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_5_pet_id_255_symbols(api_key=auth_key, pet_id=rnd_str(255)):
    headers = global_headers | {'auth_key': api_key}
    t = datetime.now()
    status, headers, resp = request('delete', path + pet_id, headers=headers)
    assert status == 400
    assert 'Content-Type' in headers.keys() and headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_6_pet_id_of_1025_symbols(api_key=auth_key, pet_id=rnd_str(1025)):
    headers = global_headers | {'auth_key': api_key}
    t = datetime.now()
    status, headers, resp = request('delete', path + pet_id, headers=headers)
    assert status == 400
    assert 'Content-Type' in headers.keys() and headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_7_pet_id_special_symbols(api_key=auth_key, pet_id=rnd_str(15, 's')):
    headers = global_headers | {'auth_key': api_key}
    t = datetime.now()
    status, headers, resp = request('delete', path + pet_id, headers=headers)
    assert status == 400
    assert 'Content-Type' in headers.keys() and headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_8_expired_auth_key(api_key=expired_api_key):
    pet = get_pet()
    if not api_key:
        assert api_key == 'expired_api_key'
    #check we've got correct pet. Otherwise display error message
    if 'id' not in pet.keys() or 'name' not in pet.keys() or 'animal_type' not in pet.keys() or 'age' not in pet.keys():
        assert pet == {'id': '*', 'name': '*', 'animal_type': '*', 'age': '*'}
    assert pet['id']
    # get new pet's data
    headers = global_headers | {'auth_key': api_key}
    t = datetime.now()
    status, headers, resp = request('put', path + pet['id'], headers=headers)
    assert status == 403
    assert 'Content-Type' in headers.keys() and headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_9_missing_auth_key():
    pet = get_pet()
    #check we've got correct pet. Otherwise display error message
    if 'id' not in pet.keys() or 'name' not in pet.keys() or 'animal_type' not in pet.keys() or 'age' not in pet.keys():
        assert pet == {'id': '*', 'name': '*', 'animal_type': '*', 'age': '*'}
    assert pet['id']
    # get new pet's data
    headers = global_headers | {}
    if 'auth_key' in headers.keys():
        headers.pop('auth_key')
    t = datetime.now()
    status, headers, resp = request('put', path + pet['id'], headers=headers)
    assert status == 403
    assert 'Content-Type' in headers.keys() and headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_10_empty_auth_key(api_key=''):
    pet = get_pet()
    #check we've got correct pet. Otherwise display error message
    if 'id' not in pet.keys() or 'name' not in pet.keys() or 'animal_type' not in pet.keys() or 'age' not in pet.keys():
        assert pet == {'id': '*', 'name': '*', 'animal_type': '*', 'age': '*'}
    assert pet['id']
    # get new pet's data
    headers = global_headers | {'auth_key': api_key}
    t = datetime.now()
    status, headers, resp = request('put', path + pet['id'], headers=headers)
    assert status == 403
    assert 'Content-Type' in headers.keys() and headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_11_auth_key_255_symbols(api_key=rnd_str(255)):
    pet = get_pet()
    #check we've got correct pet. Otherwise display error message
    if 'id' not in pet.keys() or 'name' not in pet.keys() or 'animal_type' not in pet.keys() or 'age' not in pet.keys():
        assert pet == {'id': '*', 'name': '*', 'animal_type': '*', 'age': '*'}
    assert pet['id']
    # get new pet's data
    headers = global_headers | {'auth_key': api_key}
    t = datetime.now()
    status, headers, resp = request('put', path + pet['id'], headers=headers)
    assert status == 403
    assert 'Content-Type' in headers.keys() and headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_12_auth_key_1025_symbols(api_key=rnd_str(1025)):
    pet = get_pet()
    #check we've got correct pet. Otherwise display error message
    if 'id' not in pet.keys() or 'name' not in pet.keys() or 'animal_type' not in pet.keys() or 'age' not in pet.keys():
        assert pet == {'id': '*', 'name': '*', 'animal_type': '*', 'age': '*'}
    assert pet['id']
    # get new pet's data
    headers = global_headers | {'auth_key': api_key}
    t = datetime.now()
    status, headers, resp = request('put', path + pet['id'], headers=headers)
    assert status == 403
    assert 'Content-Type' in headers.keys() and headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_13_numeric_auth_key(api_key=1234):
    pet = get_pet()
    #check we've got correct pet. Otherwise display error message
    if 'id' not in pet.keys() or 'name' not in pet.keys() or 'animal_type' not in pet.keys() or 'age' not in pet.keys():
        assert pet == {'id': '*', 'name': '*', 'animal_type': '*', 'age': '*'}
    assert pet['id']
    # get new pet's data
    headers = global_headers | {'auth_key': api_key}
    t = datetime.now()
    try:
        status, headers, resp = request('put', path + pet['id'], headers=headers)
        assert status == 403
        assert 'Content-Type' in headers.keys() and headers['Content-Type'] == 'text/html; charset=utf-8'
        assert datetime.now() - t < timedelta(seconds=1)
    except Exception as e:
        assert str(e) == ''