from api import *
from datetime import datetime, timedelta
from settings import valid_email, valid_password, expired_api_key, correct_photo_path, \
    correct_photo, large_photo, text_file, broken_photo
from requests_toolbelt import MultipartEncoder
from urllib.parse import quote_plus


auth_key = get_key()
if auth_key[:6] == 'ERROR:':
    auth_key = ''


def get_pet_id(pet_id='correct_id') -> tuple:
    global auth_key
    """
    determine id of the 1st pet without photo
    :param id: API response with pets
    :return: pet_id or an empty str and pet's data in dict
    """
    pet = {'id': pet_id}
    if not pet_id:
        # empty or None pet_id meand we don't need real pet. Just pass it out
        return pet_id, pet
    # try to get valid auth_key
    if not auth_key:
        auth_key = get_key()
    if not auth_key:
        return '', 'Unable to get auth_key'
    # create request to get my_pets
    headers = {'accept': 'application/json', 'auth_key': auth_key,
               'Content-Type': 'application/x-www-form-urlencoded'}
    params = {'filter': 'my_pets'}
    status, _, resp = request('get', 'api/pets', headers=headers, params=params)
    pet = {'id': pet_id}
    if status == 200 and type(resp) == dict and 'pets' in resp.keys() and type(resp['pets']) == list:
        # get through all (my) pets and get the pet
        for p in resp['pets']: # loop through pets in response
            if type(p) == dict and 'id' in p.keys() and p['id']: # if pet is a real pet
                # and we can pick it up
                if pet_id == p['id'] or pet_id == 'correct_id' and ('pet_photo' not in p.keys() or not p['pet_photo']):
                    return p['id'], p
        # if pet is not found and we need just any valid key of user's pets:
        if pet_id == 'correct_id':
            # create a pet without image
            body = {'name': 'Kitty', 'animal_type': 'cat', 'age': '1'}
            status, _, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
            # and return that pet
            if status == 200 and type(resp) == dict and 'id' in resp.keys():
                return resp['id'], resp
            else:
                # we didn't create a pet and cannot provide correct pet
                return '', pet
        else:
            # if we need a specific pet: get all pets (not just current user's)
            status, _, resp = request('get', 'api/pets', headers=headers)
            if status == 200 and type(resp) == dict and 'pets' in resp.keys() and type(resp['pets']) == list:
                for p in resp['pets']:
                    if type(p) == dict and 'id' in p.keys() and p['id'] == pet_id:
                        # return pet if it is found
                        return pet_id, p
    # something went really wrong and we cannot provide valid data:
    return pet_id, pet


def test_1_positive(api_key=auth_key, filename=correct_photo, pet_id='correct_id'):
    pet_id, pet = get_pet_id(pet_id) # get real pet's data
    #check pet we're about to change
    assert pet_id and type(pet) == dict and 'id' in pet.keys() and pet['id'] == pet_id
    # try to load photo
    try:
        f = get_photo(filename)
    except Exception as e:
        assert str(e) == '' # read error message
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'pet_photo': f if f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets/set_photo/' + pet_id, headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 200
    assert headers['Content-Type'] == 'application/json'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert chk_structure(resp) == ''
    assert check_pet(resp, pet['name'], pet['animal_type'], pet['age'], 'data:' + f[2] + ';base64,*')
    assert t2 - t < timedelta(seconds=1)


def test_2_expired_auth_key(api_key=expired_api_key, filename=correct_photo, pet_id='correct_id'):
    assert expired_api_key
    pet_id, pet = get_pet_id(pet_id) # get real pet's data
    #check pet we're about to change
    assert pet_id and type(pet) == dict and 'id' in pet.keys() and pet['id'] == pet_id
    # try to load photo
    try:
        f = get_photo(filename)
    except Exception as e:
        assert str(e) == '' # read error message
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'pet_photo': f if f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets/set_photo/' + pet_id, headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_3_empty_auth_key(api_key='', filename=correct_photo, pet_id='correct_id'):
    pet_id, pet = get_pet_id(pet_id) # get real pet's data
    #check pet we're about to change
    assert pet_id and type(pet) == dict and 'id' in pet.keys() and pet['id'] == pet_id
    # try to load photo
    try:
        f = get_photo(filename)
    except Exception as e:
        assert str(e) == '' # read error message
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'pet_photo': f if f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets/set_photo/' + pet_id, headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_4_missing_auth_key(filename=correct_photo, pet_id='correct_id'):
    pet_id, pet = get_pet_id(pet_id) # get real pet's data
    #check pet we're about to change
    assert pet_id and type(pet) == dict and 'id' in pet.keys() and pet['id'] == pet_id
    # try to load photo
    try:
        f = get_photo(filename)
    except Exception as e:
        assert str(e) == '' # read error message
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'pet_photo': f if f[0] else ''})
    headers = {'Content-Type': body.content_type}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets/set_photo/' + pet_id, headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_5_wrong_auth_key(api_key='asdf', filename=correct_photo, pet_id='correct_id'):
    pet_id, pet = get_pet_id(pet_id) # get real pet's data
    #check pet we're about to change
    assert pet_id and type(pet) == dict and 'id' in pet.keys() and pet['id'] == pet_id
    # try to load photo
    try:
        f = get_photo(filename)
    except Exception as e:
        assert str(e) == '' # read error message
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'pet_photo': f if f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets/set_photo/' + pet_id, headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_6_auth_key_255(api_key=rnd_str(255), filename=correct_photo, pet_id='correct_id'):
    pet_id, pet = get_pet_id(pet_id) # get real pet's data
    #check pet we're about to change
    assert pet_id and type(pet) == dict and 'id' in pet.keys() and pet['id'] == pet_id
    # try to load photo
    try:
        f = get_photo(filename)
    except Exception as e:
        assert str(e) == '' # read error message
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'pet_photo': f if f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets/set_photo/' + pet_id, headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_7_auth_key_1025(api_key=rnd_str(1025), filename=correct_photo, pet_id='correct_id'):
    pet_id, pet = get_pet_id(pet_id) # get real pet's data
    #check pet we're about to change
    assert pet_id and type(pet) == dict and 'id' in pet.keys() and pet['id'] == pet_id
    # try to load photo
    try:
        f = get_photo(filename)
    except Exception as e:
        assert str(e) == '' # read error message
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'pet_photo': f if f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets/set_photo/' + pet_id, headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_8_auth_key_symbols(api_key=rnd_str(15, 's'), filename=correct_photo, pet_id='correct_id'):
    pet_id, pet = get_pet_id(pet_id) # get real pet's data
    #check pet we're about to change
    assert pet_id and type(pet) == dict and 'id' in pet.keys() and pet['id'] == pet_id
    # try to load photo
    try:
        f = get_photo(filename)
    except Exception as e:
        assert str(e) == '' # read error message
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'pet_photo': f if f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets/set_photo/' + pet_id, headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_9_auth_key_non_ascii(api_key=rnd_str(15, 'ru'), filename=correct_photo, pet_id='correct_id'):
    pet_id, pet = get_pet_id(pet_id) # get real pet's data
    #check pet we're about to change
    assert pet_id and type(pet) == dict and 'id' in pet.keys() and pet['id'] == pet_id
    # try to load photo
    try:
        f = get_photo(filename)
    except Exception as e:
        assert str(e) == '' # read error message
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'pet_photo': f if f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets/set_photo/' + pet_id, headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_10_numeric_auth_key(api_key=12345678, filename=correct_photo, pet_id='correct_id'):
    pet_id, pet = get_pet_id(pet_id) # get real pet's data
    #check pet we're about to change
    assert pet_id and type(pet) == dict and 'id' in pet.keys() and pet['id'] == pet_id
    # try to load photo
    try:
        f = get_photo(filename)
    except Exception as e:
        assert str(e) == '' # read error message
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'pet_photo': f if f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets/set_photo/' + pet_id, headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_11_no_photo(api_key=auth_key, pet_id='correct_id'):
    pet_id, pet = get_pet_id(pet_id) # get real pet's data
    #check pet we're about to change
    assert pet_id and type(pet) == dict and 'id' in pet.keys() and pet['id'] == pet_id
    # prepare and send request to add photo
    headers = {'Content-Type': 'multipart/form-data', 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets/set_photo/' + pet_id, headers=headers)
    t2 = datetime.utcnow()
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_12_empty_photo(api_key=auth_key, pet_id='correct_id', pet_photo=''):
    pet_id, pet = get_pet_id(pet_id) # get real pet's data
    #check pet we're about to change
    assert pet_id and type(pet) == dict and 'id' in pet.keys() and pet['id'] == pet_id
    # prepare and send request to add photo
    body = MultipartEncoder({'pet_photo': pet_photo})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets/set_photo/' + pet_id, headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_13_large_photo(api_key=auth_key, pet_id='correct_id', filename=large_photo):
    pet_id, pet = get_pet_id(pet_id) # get real pet's data
    #check pet we're about to change
    assert pet_id and type(pet) == dict and 'id' in pet.keys() and pet['id'] == pet_id
    # try to load photo
    try:
        f = get_photo(filename)
    except Exception as e:
        assert str(e) == '' # read error message
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'pet_photo': f if f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets/set_photo/' + pet_id, headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_14_text_file(api_key=auth_key, pet_id='correct_id', filename=text_file):
    pet_id, pet = get_pet_id(pet_id) # get real pet's data
    #check pet we're about to change
    assert pet_id and type(pet) == dict and 'id' in pet.keys() and pet['id'] == pet_id
    # try to load photo
    try:
        f = get_photo(filename)
    except Exception as e:
        assert str(e) == '' # read error message
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'pet_photo': f if f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets/set_photo/' + pet_id, headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_15_broken_file(api_key=auth_key, pet_id='correct_id', broken_file=broken_photo()):
    pet_id, pet = get_pet_id(pet_id) # get real pet's data
    #check pet we're about to change
    assert pet_id and type(pet) == dict and 'id' in pet.keys() and pet['id'] == pet_id
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'pet_photo': ('pet_photo.jpg', broken_file, 'image/jpg')})
    print(body)
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets/set_photo/' + pet_id, headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_16_text_instead_of_file(api_key=auth_key, pet_id='correct_id', filename=rnd_str(255)):
    pet_id, pet = get_pet_id(pet_id) # get real pet's data
    #check pet we're about to change
    assert pet_id and type(pet) == dict and 'id' in pet.keys() and pet['id'] == pet_id
    # try to load photo
    try:
        f = get_photo(filename)
    except Exception as e:
        assert str(e) == '' # read error message
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'pet_photo': filename})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets/set_photo/' + pet_id, headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_17_special_symbols_instead_photo(api_key=auth_key, pet_id='correct_id', filename=rnd_str(15, 's')):
    pet_id, pet = get_pet_id(pet_id) # get real pet's data
    #check pet we're about to change
    assert pet_id and type(pet) == dict and 'id' in pet.keys() and pet['id'] == pet_id
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'pet_photo': filename})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets/set_photo/' + pet_id, headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_18_non_ascii_symbols_instead_photo(api_key=auth_key, pet_id='correct_id', filename=rnd_str(255, 'ru')):
    pet_id, pet = get_pet_id(pet_id) # get real pet's data
    #check pet we're about to change
    assert pet_id and type(pet) == dict and 'id' in pet.keys() and pet['id'] == pet_id
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'pet_photo': filename})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets/set_photo/' + pet_id, headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_19_number_instead_photo(api_key=auth_key, pet_id='correct_id', filename=123868):
    pet_id, pet = get_pet_id(pet_id) # get real pet's data
    #check pet we're about to change
    assert pet_id and type(pet) == dict and 'id' in pet.keys() and pet['id'] == pet_id
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'pet_photo': str(filename)})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets/set_photo/' + pet_id, headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_20_wrong_method(method='put', api_key=auth_key, pet_id='correct_id', filename=correct_photo):
    pet_id, pet = get_pet_id(pet_id) # get real pet's data
    #check pet we're about to change
    assert pet_id and type(pet) == dict and 'id' in pet.keys() and pet['id'] == pet_id
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'pet_photo': filename})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request(method, 'api/pets/set_photo/' + pet_id, headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 405
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_21_missing_ct_type(api_key=auth_key, filename=correct_photo, pet_id='correct_id', ct_type='application/json'):
    pet_id, pet = get_pet_id(pet_id) # get real pet's data
    #check pet we're about to change
    assert pet_id and type(pet) == dict and 'id' in pet.keys() and pet['id'] == pet_id
    # try to load photo
    try:
        f = get_photo(filename)
    except Exception as e:
        assert str(e) == '' # read error message
    # prepare and send request to add photo
    body={'pet_photo': f if f[0] else ''}
    headers = {'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets/set_photo/' + pet_id, headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_22_multiple_ct_type_values(api_key=auth_key, pet_id='correct_id', filename=correct_photo,
                                    ct_type='text/plain; application/x-www-form-urlencoded; application/json'):
    pet_id, pet = get_pet_id(pet_id) # get real pet's data
    #check pet we're about to change
    assert pet_id and type(pet) == dict and 'id' in pet.keys() and pet['id'] == pet_id
    # try to load photo
    try:
        f = get_photo(filename)
    except Exception as e:
        assert str(e) == '' # read error message
    # prepare and send request to add photo
    body={'pet_photo': f if f[0] else ''}
    headers = {'Content-Type': ct_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets/set_photo/' + pet_id, headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 415
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_23_wrong_ct_type(api_key=auth_key, pet_id='correct_id', filename=correct_photo,
                          ct_type='application/x-www-form-urlencoded'):
    pet_id, pet = get_pet_id(pet_id) # get real pet's data
    #check pet we're about to change
    assert pet_id and type(pet) == dict and 'id' in pet.keys() and pet['id'] == pet_id
    # try to load photo
    try:
        f = get_photo(filename)
    except Exception as e:
        assert str(e) == '' # read error message
    # prepare and send request to add photo
    body={'pet_photo': f if f[0] else ''}
    headers = {'Content-Type': ct_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets/set_photo/' + pet_id, headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_24_different_ct_type(api_key=auth_key, filename=correct_photo, pet_id='correct_id',
                                       ct_type='application/x-www-form-urlencoded'):
    pet_id, pet = get_pet_id(pet_id) # get real pet's data
    #check pet we're about to change
    assert pet_id and type(pet) == dict and 'id' in pet.keys() and pet['id'] == pet_id
    # try to load photo
    try:
        f = get_photo(filename)
    except Exception as e:
        assert str(e) == '' # read error message
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'pet_photo': f if f[0] else ''})
    headers = {'Content-Type': ct_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets/set_photo/' + pet_id, headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_25_different_ct_type(api_key=auth_key, filename=correct_photo, pet_id='correct_id', ct_type='application/json'):
    pet_id, pet = get_pet_id(pet_id) # get real pet's data
    #check pet we're about to change
    assert pet_id and type(pet) == dict and 'id' in pet.keys() and pet['id'] == pet_id
    # try to load photo
    try:
        f = get_photo(filename)
    except Exception as e:
        assert str(e) == '' # read error message
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'pet_photo': f if f[0] else ''})
    headers = {'Content-Type': ct_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets/set_photo/' + pet_id, headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_26_ct_type_255(api_key=auth_key, pet_id='correct_id', filename=correct_photo, ct_type=rnd_str(255)):
    pet_id, pet = get_pet_id(pet_id) # get real pet's data
    #check pet we're about to change
    assert pet_id and type(pet) == dict and 'id' in pet.keys() and pet['id'] == pet_id
    # try to load photo
    try:
        f = get_photo(filename)
    except Exception as e:
        assert str(e) == '' # read error message
    # prepare and send request to add photo
    body={'pet_photo': f if f[0] else ''}
    headers = {'Content-Type': ct_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets/set_photo/' + pet_id, headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 415
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_27_ct_type_1025(api_key=auth_key, pet_id='correct_id', filename=correct_photo, ct_type=rnd_str(1025)):
    pet_id, pet = get_pet_id(pet_id) # get real pet's data
    #check pet we're about to change
    assert pet_id and type(pet) == dict and 'id' in pet.keys() and pet['id'] == pet_id
    # try to load photo
    try:
        f = get_photo(filename)
    except Exception as e:
        assert str(e) == '' # read error message
    # prepare and send request to add photo
    body={'pet_photo': f if f[0] else ''}
    headers = {'Content-Type': ct_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets/set_photo/' + pet_id, headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 415
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_28_ct_type_symbols(api_key=auth_key, pet_id='correct_id', filename=correct_photo, ct_type=rnd_str(15, 's')):
    pet_id, pet = get_pet_id(pet_id) # get real pet's data
    #check pet we're about to change
    assert pet_id and type(pet) == dict and 'id' in pet.keys() and pet['id'] == pet_id
    # try to load photo
    try:
        f = get_photo(filename)
    except Exception as e:
        assert str(e) == '' # read error message
    # prepare and send request to add photo
    body={'pet_photo': f if f[0] else ''}
    headers = {'Content-Type': ct_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets/set_photo/' + pet_id, headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 415
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_29_ct_type_non_ascii(api_key=auth_key, pet_id='correct_id', filename=correct_photo, ct_type=rnd_str(15, 'ru')):
    pet_id, pet = get_pet_id(pet_id) # get real pet's data
    #check pet we're about to change
    assert pet_id and type(pet) == dict and 'id' in pet.keys() and pet['id'] == pet_id
    # try to load photo
    try:
        f = get_photo(filename)
    except Exception as e:
        assert str(e) == '' # read error message
    # prepare and send request to add photo
    body={'pet_photo': f if f[0] else ''}
    headers = {'Content-Type': ct_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets/set_photo/' + pet_id, headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 415
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_30_numberic_ct_type(api_key=auth_key, pet_id='correct_id', filename=correct_photo, ct_type=1657328):
    pet_id, pet = get_pet_id(pet_id) # get real pet's data
    #check pet we're about to change
    assert pet_id and type(pet) == dict and 'id' in pet.keys() and pet['id'] == pet_id
    # try to load photo
    try:
        f = get_photo(filename)
    except Exception as e:
        assert str(e) == '' # read error message
    # prepare and send request to add photo
    body={'pet_photo': f if f[0] else ''}
    headers = {'Content-Type': ct_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets/set_photo/' + pet_id, headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 415
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_31_pet_of_different_user(api_key=get_key(2), pet_id='correct_id', filename=correct_photo):
    pet_id, pet = get_pet_id(pet_id) # get real pet's data
    #check pet we're about to change
    assert pet_id and type(pet) == dict and 'id' in pet.keys() and pet['id'] == pet_id
    # try to load photo
    try:
        f = get_photo(filename)
    except Exception as e:
        assert str(e) == '' # read error message
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'pet_photo': f if f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets/set_photo/' + pet_id, headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_32_no_pet_id(api_key=auth_key, filename=correct_photo):
    # try to load photo
    try:
        f = get_photo(filename)
    except Exception as e:
        assert str(e) == '' # read error message
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'pet_photo': f if f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets/set_photo/', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_33_incorrect_pet_id(api_key=auth_key, pet_id='asdf', filename=correct_photo):
    # try to load photo
    try:
        f = get_photo(filename)
    except Exception as e:
        assert str(e) == '' # read error message
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'pet_photo': f if f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets/set_photo/' + pet_id, headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 404
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_34_pet_id_255_symbols(api_key=auth_key, pet_id=rnd_str(255), filename=correct_photo):
    pet_id, pet = get_pet_id(pet_id) # get real pet's data
    #check pet we're about to change
    assert pet_id and type(pet) == dict and 'id' in pet.keys() and pet['id'] == pet_id
    # try to load photo
    try:
        f = get_photo(filename)
    except Exception as e:
        assert str(e) == '' # read error message
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'pet_photo': f if f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets/set_photo/' + pet_id, headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 404
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_35_pet_id_1025_symbols(api_key=auth_key, pet_id=rnd_str(1025), filename=correct_photo):
    # try to load photo
    try:
        f = get_photo(filename)
    except Exception as e:
        assert str(e) == '' # read error message
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'pet_photo': f if f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets/set_photo/' + pet_id, headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 404
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_36_pet_id_special_symbols(api_key=auth_key, pet_id=rnd_str(15, 's'), filename=correct_photo):
    # try to load photo
    try:
        f = get_photo(filename)
    except Exception as e:
        assert str(e) == '' # read error message
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'pet_photo': f if f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets/set_photo/' + quote_plus(pet_id), headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 404
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_37_non_ascii_pet_id(api_key=auth_key, pet_id=rnd_str(15, 'ru'), filename=correct_photo):
    # try to load photo
    try:
        f = get_photo(filename)
    except Exception as e:
        assert str(e) == '' # read error message
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'pet_photo': f if f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets/set_photo/' + quote_plus(pet_id), headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 404
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)
