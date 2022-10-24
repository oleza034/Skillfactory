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


def new_name(name: str, animal_type: str, age: int, lang: str = None) -> tuple:
    """
    Gets a different pet's name, animal_type and age depending on current values
    :param name: old pet's name
    :param animal_type: old animal_type
    :param age: old age
    :param lang: Optional. Language that should be used on output. By default, it is language of name or animal_type
    :return: new name, animal_type and age
    """
    names = {'name': {'en': ['Doggie', 'Kitty'], 'ru': ['Шарик', 'Мурка']},
             'animal_type': {'en': ['dog', 'cat'], 'ru': ['собака', 'кошка']},
             'age': [1, 5, 20, 0]}
    if lang not in names.keys():
        lang = 'ru' if ord((str(name) + str(animal_type) + 'a')[0]) > 127 else 'en'
    pet = (names['name'][lang][0] if name == names['name'][lang][1] else names['name'][lang][1],
           names['animal_type'][lang][0] if animal_type == names['animal_type'][lang][1] \
                 else names['animal_type'][lang][1],
           names['age'][0] if age not in names['age'][:-1] else names['age'][names['age'].index(age) + 1])
    return pet


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


def test_1_positive(api_key = auth_key):
    pet = get_pet()
    #check we've got correct pet. Otherwise display error message
    if 'id' not in pet.keys() or 'name' not in pet.keys() or 'animal_type' not in pet.keys() or 'age' not in pet.keys():
        assert pet == {'id': '*', 'name': '*', 'animal_type': '*', 'age': '*'}
    assert pet['id']
    # get new pet's data
    name, animal_type, age = new_name(pet['name'], pet['animal_type'], pet['age'])
    assert name != pet['name'] and animal_type != pet['animal_type'] and age != pet['age']
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    headers = global_headers | {'auth_key': api_key}
    t = datetime.now()
    status, headers, resp = request('put', path + pet['id'], headers=headers, body=body)
    assert status == 200
    assert 'Content-Type' in headers.keys() and headers['Content-Type'] == 'application/json'
    assert 'id' in resp.keys() and resp['id'] == pet['id']
    assert 'name' in resp.keys() and resp['name'] == name
    assert 'animal_type' in resp.keys() and resp['animal_type'] == animal_type
    assert 'age' in resp.keys() and resp['age'] == str(age)
    assert datetime.now() - t < timedelta(seconds=1)


def test_2_positive_unicode(api_key = auth_key):
    pet = get_pet(index=1)
    #check we've got correct pet. Otherwise display error message
    if 'id' not in pet.keys() or 'name' not in pet.keys() or 'animal_type' not in pet.keys() or 'age' not in pet.keys():
        assert pet == {'id': '*', 'name': '*', 'animal_type': '*', 'age': '*'}
    assert pet['id']
    # get new pet's data
    name, animal_type, age = new_name(pet['name'], pet['animal_type'], pet['age'], lang='ru')
    assert name != pet['name'] and animal_type != pet['animal_type'] and age != pet['age']
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    headers = global_headers | {'auth_key': api_key}
    t = datetime.now()
    status, headers, resp = request('put', path + pet['id'], headers=headers, body=body)
    assert status == 200
    assert 'Content-Type' in headers.keys() and headers['Content-Type'] == 'application/json'
    assert 'id' in resp.keys() and resp['id'] == pet['id']
    assert 'name' in resp.keys() and resp['name'] == name
    assert 'animal_type' in resp.keys() and resp['animal_type'] == animal_type
    assert 'age' in resp.keys() and resp['age'] == str(age)
    assert datetime.now() - t < timedelta(seconds=1)


def test_3_pet_id_of_another_user(api_key = auth_key):
    # get 1st pet
    pet = get_pet()
    #check we've got correct pet. Otherwise display error message
    if 'id' not in pet.keys() or 'name' not in pet.keys() or 'animal_type' not in pet.keys() or 'age' not in pet.keys():
        assert pet == {'id': '*', 'name': '*', 'animal_type': '*', 'age': '*'}
    assert pet['id']
    # get new pet's data
    name, animal_type, age = new_name(pet['name'], pet['animal_type'], pet['age'])
    assert name != pet['name'] and animal_type != pet['animal_type'] and age != pet['age']
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    # authorize as another user
    headers = global_headers | {'auth_key': get_key(2)}
    t = datetime.now()
    status, headers, _ = request('put', path + pet['id'], headers=headers, body=body)
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_4_missing_pet_id(api_key = auth_key):
    name, animal_type, age = new_name('', '', None)
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    headers = global_headers | {'auth_key': api_key}
    t = datetime.now()
    status, headers, _ = request('put', path[:-1], headers=headers, body=body)
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_5_empty_pet_id(api_key = auth_key):
    name, animal_type, age = new_name('', '', None)
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    headers = global_headers | {'auth_key': api_key}
    t = datetime.now()
    status, headers, _ = request('put', path, headers=headers, body=body)
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_6_wrong_auth_key(api_key = rnd_str(255)):
    pet = get_pet()
    #check we've got correct pet. Otherwise display error message
    if 'id' not in pet.keys() or 'name' not in pet.keys() or 'animal_type' not in pet.keys() or 'age' not in pet.keys():
        assert pet == {'id': '*', 'name': '*', 'animal_type': '*', 'age': '*'}
    assert pet['id']
    # get new pet's data
    name, animal_type, age = new_name(pet['name'], pet['animal_type'], pet['age'])
    assert name != pet['name'] and animal_type != pet['animal_type'] and age != pet['age']
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    headers = global_headers | {'auth_key': api_key}
    t = datetime.now()
    status, headers, _ = request('put', path + pet['id'], headers=headers, body=body)
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_7_auth_key_1025_symbols(api_key = rnd_str(1025)):
    pet = get_pet()
    #check we've got correct pet. Otherwise display error message
    if 'id' not in pet.keys() or 'name' not in pet.keys() or 'animal_type' not in pet.keys() or 'age' not in pet.keys():
        assert pet == {'id': '*', 'name': '*', 'animal_type': '*', 'age': '*'}
    assert pet['id']
    # get new pet's data
    name, animal_type, age = new_name(pet['name'], pet['animal_type'], pet['age'])
    assert name != pet['name'] and animal_type != pet['animal_type'] and age != pet['age']
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    headers = global_headers | {'auth_key': api_key}
    t = datetime.now()
    status, headers, _ = request('put', path + pet['id'], headers=headers, body=body)
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_8_auth_key_special_symbols(api_key = rnd_str(15, 's')):
    pet = get_pet()
    #check we've got correct pet. Otherwise display error message
    if 'id' not in pet.keys() or 'name' not in pet.keys() or 'animal_type' not in pet.keys() or 'age' not in pet.keys():
        assert pet == {'id': '*', 'name': '*', 'animal_type': '*', 'age': '*'}
    assert pet['id']
    # get new pet's data
    name, animal_type, age = new_name(pet['name'], pet['animal_type'], pet['age'])
    assert name != pet['name'] and animal_type != pet['animal_type'] and age != pet['age']
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    headers = global_headers | {'auth_key': api_key}
    t = datetime.now()
    status, headers, _ = request('put', path + pet['id'], headers=headers, body=body)
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_9_auth_key_non_ascii(api_key = rnd_str(54, 'ru')):
    pet = get_pet()
    #check we've got correct pet. Otherwise display error message
    if 'id' not in pet.keys() or 'name' not in pet.keys() or 'animal_type' not in pet.keys() or 'age' not in pet.keys():
        assert pet == {'id': '*', 'name': '*', 'animal_type': '*', 'age': '*'}
    assert pet['id']
    # get new pet's data
    name, animal_type, age = new_name(pet['name'], pet['animal_type'], pet['age'])
    assert name != pet['name'] and animal_type != pet['animal_type'] and age != pet['age']
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    headers = global_headers | {'auth_key': api_key}
    t = datetime.now()
    status, headers, _ = request('put', path + pet['id'], headers=headers, body=body)
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_10_expired_auth_key(api_key = expired_api_key):
    if not api_key:
        assert api_key == 'expired_auth_key'
    pet = get_pet()
    #check we've got correct pet. Otherwise display error message
    if 'id' not in pet.keys() or 'name' not in pet.keys() or 'animal_type' not in pet.keys() or 'age' not in pet.keys():
        assert pet == {'id': '*', 'name': '*', 'animal_type': '*', 'age': '*'}
    assert pet['id']
    # get new pet's data
    name, animal_type, age = new_name(pet['name'], pet['animal_type'], pet['age'])
    assert name != pet['name'] and animal_type != pet['animal_type'] and age != pet['age']
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    t = datetime.now()
    headers = global_headers | {'auth_key': api_key}
    status, headers, _ = request('put', path + pet['id'], headers=headers, body=body)
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_11_missing_auth_key():
    pet = get_pet()
    #check we've got correct pet. Otherwise display error message
    if 'id' not in pet.keys() or 'name' not in pet.keys() or 'animal_type' not in pet.keys() or 'age' not in pet.keys():
        assert pet == {'id': '*', 'name': '*', 'animal_type': '*', 'age': '*'}
    assert pet['id']
    # get new pet's data
    name, animal_type, age = new_name(pet['name'], pet['animal_type'], pet['age'])
    assert name != pet['name'] and animal_type != pet['animal_type'] and age != pet['age']
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    headers = global_headers | {}
    if 'auth_key' in headers.keys():
        headers.pop('auth_key')
    t = datetime.now()
    status, headers, _ = request('put', path + pet['id'], headers=headers, body=body)
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_12_missing_name(api_key = auth_key):
    pet = get_pet()
    #check we've got correct pet. Otherwise display error message
    if 'id' not in pet.keys() or 'name' not in pet.keys() or 'animal_type' not in pet.keys() or 'age' not in pet.keys():
        assert pet == {'id': '*', 'name': '*', 'animal_type': '*', 'age': '*'}
    assert pet['id']
    # get new pet's data
    name, animal_type, age = new_name(pet['name'], pet['animal_type'], pet['age'])
    assert name != pet['name'] and animal_type != pet['animal_type'] and age != pet['age']
    body = {'animal_type': animal_type, 'age': age}
    headers = global_headers | {'auth_key': api_key}
    t = datetime.now()
    status, headers, resp = request('put', path + pet['id'], headers=headers, body=body)
    assert status == 200
    assert headers['Content-Type'] == 'application/json'
    assert 'id' in resp.keys() and resp['id'] == pet['id']
    assert 'name' in resp.keys() and resp['name'] == pet['name']
    assert 'animal_type' in resp.keys() and resp['animal_type'] == animal_type
    assert 'age' in resp.keys() and resp['age'] == str(age)
    assert datetime.now() - t < timedelta(seconds=1)


def test_13_missing_animal_type(api_key = auth_key):
    pet = get_pet()
    #check we've got correct pet. Otherwise display error message
    if 'id' not in pet.keys() or 'name' not in pet.keys() or 'animal_type' not in pet.keys() or 'age' not in pet.keys():
        assert pet == {'id': '*', 'name': '*', 'animal_type': '*', 'age': '*'}
    assert pet['id']
    # get new pet's data
    name, animal_type, age = new_name(pet['name'], pet['animal_type'], pet['age'])
    assert name != pet['name'] and animal_type != pet['animal_type'] and age != pet['age']
    body = {'name': name, 'age': age}
    headers = global_headers | {'auth_key': api_key}
    t = datetime.now()
    status, headers, resp = request('put', path + pet['id'], headers=headers, body=body)
    assert status == 200
    assert headers['Content-Type'] == 'application/json'
    assert 'id' in resp.keys() and resp['id'] == pet['id']
    assert 'name' in resp.keys() and resp['name'] == name
    assert 'animal_type' in resp.keys() and resp['animal_type'] == pet['animal_type']
    assert 'age' in resp.keys() and resp['age'] == str(age)
    assert datetime.now() - t < timedelta(seconds=1)


def test_14_missing_age(api_key = auth_key):
    pet = get_pet()
    #check we've got correct pet. Otherwise display error message
    if 'id' not in pet.keys() or 'name' not in pet.keys() or 'animal_type' not in pet.keys() or 'age' not in pet.keys():
        assert pet == {'id': '*', 'name': '*', 'animal_type': '*', 'age': '*'}
    assert pet['id']
    # get new pet's data
    name, animal_type, age = new_name(pet['name'], pet['animal_type'], pet['age'])
    assert name != pet['name'] and animal_type != pet['animal_type'] and age != pet['age']
    body = {'name': name, 'animal_type': animal_type}
    headers = global_headers | {'auth_key': api_key}
    t = datetime.now()
    status, headers, resp = request('put', path + pet['id'], headers=headers, body=body)
    assert status == 200
    assert headers['Content-Type'] == 'application/json'
    assert 'id' in resp.keys() and resp['id'] == pet['id']
    assert 'name' in resp.keys() and resp['name'] == name
    assert 'animal_type' in resp.keys() and resp['animal_type'] == animal_type
    assert 'age' in resp.keys() and resp['age'] == str(pet['age'])
    assert datetime.now() - t < timedelta(seconds=1)


def test_15_missing_body(api_key = auth_key):
    pet = get_pet()
    #check we've got correct pet. Otherwise display error message
    if 'id' not in pet.keys() or 'name' not in pet.keys() or 'animal_type' not in pet.keys() or 'age' not in pet.keys():
        assert pet == {'id': '*', 'name': '*', 'animal_type': '*', 'age': '*'}
    assert pet['id']
    # get new pet's data
    headers = global_headers | {'auth_key': api_key}
    t = datetime.now()
    status, headers, resp = request('put', path + pet['id'], headers=headers)
    assert status == 200
    assert headers['Content-Type'] == 'application/json'
    assert 'id' in resp.keys() and resp['id'] == pet['id']
    assert 'name' in resp.keys() and resp['name'] == pet['name']
    assert 'animal_type' in resp.keys() and resp['animal_type'] == pet['animal_type']
    assert 'age' in resp.keys() and resp['age'] == str(pet['age'])
    assert datetime.now() - t < timedelta(seconds=1)


def test_16_parameters_str_of_255(api_key = auth_key):
    pet = get_pet()
    #check we've got correct pet. Otherwise display error message
    if 'id' not in pet.keys() or 'name' not in pet.keys() or 'animal_type' not in pet.keys() or 'age' not in pet.keys():
        assert pet == {'id': '*', 'name': '*', 'animal_type': '*', 'age': '*'}
    assert pet['id']
    # get new pet's data
    body = {'name': rnd_str(255), 'animal_type': rnd_str(255), 'age': rnd_str(255)}
    headers = global_headers | {'auth_key': api_key}
    t = datetime.now()
    status, headers, resp = request('put', path + pet['id'], headers=headers, body=body)
    assert status == 200
    assert headers['Content-Type'] == 'application/json'
    assert 'id' in resp.keys() and resp['id'] == pet['id']
    assert 'name' in resp.keys() and resp['name'] == body['name']
    assert 'animal_type' in resp.keys() and resp['animal_type'] == body['animal_type']
    assert 'age' in resp.keys() and resp['age'] == body['age']
    assert datetime.now() - t < timedelta(seconds=1)


def test_17_parameters_str_1025(api_key = auth_key):
    pet = get_pet()
    #check we've got correct pet. Otherwise display error message
    if 'id' not in pet.keys() or 'name' not in pet.keys() or 'animal_type' not in pet.keys() or 'age' not in pet.keys():
        assert pet == {'id': '*', 'name': '*', 'animal_type': '*', 'age': '*'}
    assert pet['id']
    # get new pet's data
    name, animal_type, age = rnd_str(1025), rnd_str(1025), rnd_str(1025)
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    headers = global_headers | {'auth_key': api_key}
    t = datetime.now()
    status, headers, resp = request('put', path + pet['id'], headers=headers, body=body)
    assert status == 200
    assert headers['Content-Type'] == 'application/json' and type(resp) == dict
    assert 'id' in resp.keys() and resp['id'] == pet['id']
    assert 'name' in resp.keys() and resp['name'] == body['name']
    assert 'animal_type' in resp.keys() and resp['animal_type'] == body['animal_type']
    assert 'age' in resp.keys() and resp['age'] == body['age']
    assert datetime.now() - t < timedelta(seconds=1)


def test_18_parameters_spec_symbols(api_key = auth_key):
    pet = get_pet()
    #check we've got correct pet. Otherwise display error message
    if 'id' not in pet.keys() or 'name' not in pet.keys() or 'animal_type' not in pet.keys() or 'age' not in pet.keys():
        assert pet == {'id': '*', 'name': '*', 'animal_type': '*', 'age': '*'}
    assert pet['id']
    # get new pet's data
    name, animal_type, age = rnd_str(15, 's'), rnd_str(15, 's'), rnd_str(15, 's')
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    headers = global_headers | {'auth_key': api_key}
    t = datetime.now()
    status, headers, resp = request('put', path + pet['id'], headers=headers, body=body)
    assert status == 200
    assert headers['Content-Type'] == 'application/json' and type(resp) == dict
    assert 'id' in resp.keys() and resp['id'] == pet['id']
    assert 'name' in resp.keys() and resp['name'] == body['name']
    assert 'animal_type' in resp.keys() and resp['animal_type'] == body['animal_type']
    assert 'age' in resp.keys() and resp['age'] == body['age']
    assert datetime.now() - t < timedelta(seconds=1)


def test_19_parameters_numbers(api_key = auth_key):
    pet = get_pet()
    #check we've got correct pet. Otherwise display error message
    if 'id' not in pet.keys() or 'name' not in pet.keys() or 'animal_type' not in pet.keys() or 'age' not in pet.keys():
        assert pet == {'id': '*', 'name': '*', 'animal_type': '*', 'age': '*'}
    assert pet['id']
    # get new pet's data
    name, animal_type, age = 123, 456, 987
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    headers = global_headers | {'auth_key': api_key}
    t = datetime.now()
    status, headers, resp = request('put', path + pet['id'], headers=headers, body=body)
    assert status == 200
    assert headers['Content-Type'] == 'application/json' and type(resp) == dict
    assert 'id' in resp.keys() and resp['id'] == pet['id']
    assert 'name' in resp.keys() and resp['name'] == str(name)
    assert 'animal_type' in resp.keys() and resp['animal_type'] == str(animal_type)
    assert 'age' in resp.keys() and resp['age'] == str(age)
    assert datetime.now() - t < timedelta(seconds=1)
