from api import *
from datetime import datetime, timedelta
from settings import expired_api_key, base_url

def get_valid_key():
    key = get_key()
    if key[:6] == 'ERROR:':
        return ''
    else:
        return key


auth_key = get_valid_key()


def test_1_create_pet_positive(auth_key=auth_key, name='Doggie', animal_type='dog', age=3):
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'auth_key': auth_key}
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    t = datetime.now()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    assert status == 200
    # resp must contain all required fields and may only contain required or optional fields;
    # of specific type.
    assert chk_structure(resp) == ''
    # values in response must be equal to values we sent to server; also check timestamp
    assert check_pet(resp, name, animal_type, age) == ''
    assert datetime.now() - t < timedelta(seconds=1)


def test_2_create_pet_unicode(auth_key=auth_key, name=rnd_str(12, 'ru'), animal_type=rnd_str(12, 'ru'), age=0):
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'auth_key': auth_key}
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    t = datetime.now()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    assert status == 200
    assert chk_structure(resp) == ''
    assert check_pet(resp, name, animal_type, age) == ''
    assert datetime.now() - t < timedelta(seconds=1)


def test_3_create_pet_str_255(auth_key=auth_key, name=rnd_str(255), animal_type=rnd_str(255), age=rnd_str(3, 'd')):
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'auth_key': auth_key}
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    t = datetime.now()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    assert status == 200
    assert chk_structure(resp) == ''
    assert check_pet(resp, name, animal_type, age) == ''
    assert datetime.now() - t < timedelta(seconds=1)


def test_4_create_pet_symbols(auth_key=auth_key, name=rnd_str(12, 's'), animal_type=rnd_str(12, 's'), age=rnd_str(5, 'd')):
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'auth_key': auth_key}
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    t = datetime.now()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    assert status == 200
    assert chk_structure(resp) == ''
    assert check_pet(resp, name, animal_type, age) == ''
    assert datetime.now() - t < timedelta(seconds=1)


def test_5_create_pet_no_key(name='Doggie', animal_type='dog', age=3):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    t = datetime.now()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_6_create_pet_wrong_key(auth_key='asdf', name='Doggie', animal_type='dog', age=3):
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'auth_key': auth_key}
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    t = datetime.now()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_7_create_pet_no_name(auth_key=auth_key, animal_type='dog', age=3):
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'auth_key': auth_key}
    body = {'animal_type': animal_type, 'age': age}
    t = datetime.now()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_8_create_pet_no_animal_type(auth_key=auth_key, name='Doggie', age=3):
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'auth_key': auth_key}
    body = {'name': name, 'age': age}
    t = datetime.now()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_9_create_pet_no_age(auth_key=auth_key, name='Doggie', animal_type='dog'):
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'auth_key': auth_key}
    body = {'name': name, 'animal_type': animal_type}
    t = datetime.now()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_10_create_pet_wrong_ct_type(auth_key=auth_key, name='Doggie', animal_type='dog', age=3,
                                    ct_type='application/xml; application/x-www-form-urlencoded, multipart/form-data'):
    headers = {'Content-Type': ct_type, 'auth_key': auth_key}
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    t = datetime.now()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    assert status == 415
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_11_create_pet_wrong_ct(auth_key=auth_key, name='Doggie', animal_type='dog', age=3, ct_type='application/json'):
    headers = {'Content-Type': ct_type, 'auth_key': auth_key}
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    t = datetime.now()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    assert status == 415
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_12_create_pet_str_4097(auth_key=auth_key, name=rnd_str(4097), animal_type=rnd_str(4097), age=rnd_str(4097)):
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'auth_key': auth_key}
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    t = datetime.now()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_13_create_pet_numeric(auth_key=auth_key, name=1, animal_type=23, age=456):
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'auth_key': auth_key}
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    t = datetime.now()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)
