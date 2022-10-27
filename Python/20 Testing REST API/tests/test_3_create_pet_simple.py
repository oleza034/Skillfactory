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
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 200
    assert headers['Content-Type'] == 'application/json'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    # resp must contain all required fields and may only contain required or optional fields;
    # of specific type.
    assert chk_structure(resp) == ''
    # values in response must be equal to values we sent to server; also check timestamp
    assert check_pet(resp, name, animal_type, age) == ''
    assert t2 - t < timedelta(seconds=1)


def test_2_create_pet_unicode_values_multipart_encode(auth_key=auth_key, name=rnd_str(12, 'ru'),
                            animal_type=rnd_str(12, 'ru'), age=0, ct_type='multipart/form-data'):
    body = MultipartEncoder(fields={'name': name, 'animal_type': animal_type, 'age': str(age)}, encoding='utf-8')
    headers = {'Content-Type': body.content_type, 'auth_key': auth_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 200
    assert headers['Content-Type'] == 'application/json'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert chk_structure(resp) == ''
    assert check_pet(resp, name, animal_type, age) == ''
    assert t2 - t < timedelta(seconds=1)


def test_3_create_pet_str_255_and_json_ct_type(auth_key=auth_key, name=rnd_str(255), animal_type=rnd_str(255),
                                               age=rnd_str(3, 'd'), ct_type='application/json'):
    headers = {'Content-Type': ct_type, 'auth_key': auth_key}
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 200
    assert headers['Content-Type'] == 'aplication/json'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert chk_structure(resp) == ''
    assert check_pet(resp, name, animal_type, age) == ''
    assert t2 - t < timedelta(seconds=1)


def test_4_create_pet_symbols(auth_key=auth_key, name=rnd_str(12, 's'), animal_type=rnd_str(12, 's'),
                              age=rnd_str(5, 'd')):
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'auth_key': auth_key}
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 200
    assert headers['Content-Type'] == 'aplication/json'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert chk_structure(resp) == ''
    assert check_pet(resp, name, animal_type, age) == ''
    assert t2 - t < timedelta(seconds=1)


def test_5_create_pet_empty_name(auth_key=auth_key, name='', animal_type='dog', age=3):
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'auth_key': auth_key}
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 200
    assert headers['Content-Type'] == 'aplication/json'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert chk_structure(resp) == ''
    assert check_pet(resp, name, animal_type, age) == ''
    assert t2 - t < timedelta(seconds=1)


def test_6_create_pet_empty_animal_type(auth_key=auth_key, name='Kitty', animal_type='', age=3):
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'auth_key': auth_key}
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 200
    assert headers['Content-Type'] == 'aplication/json'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert chk_structure(resp) == ''
    assert check_pet(resp, name, animal_type, age) == ''
    assert t2 - t < timedelta(seconds=1)


def test_7_create_pet_empty_age(auth_key=auth_key, name='Doggie', animal_type='dog', age=''):
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'auth_key': auth_key}
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 200
    assert headers['Content-Type'] == 'aplication/json'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert chk_structure(resp) == ''
    assert check_pet(resp, name, animal_type, age) == ''
    assert t2 - t < timedelta(seconds=1)


def test_8_create_pet_empty_data_in_body(auth_key=auth_key, name='', animal_type='', age=''):
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'auth_key': auth_key}
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 200
    assert headers['Content-Type'] == 'aplication/json'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert chk_structure(resp) == ''
    assert check_pet(resp, name, animal_type, age) == ''
    assert t2 - t < timedelta(seconds=1)


def test_9_create_pet_no_name(auth_key=auth_key, animal_type='dog', age=3):
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'auth_key': auth_key}
    body = {'animal_type': animal_type, 'age': age}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_10_create_pet_no_animal_type(auth_key=auth_key, name='Doggie', age=3):
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'auth_key': auth_key}
    body = {'name': name, 'age': age}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_11_create_pet_no_age(auth_key=auth_key, name='Doggie', animal_type='dog'):
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'auth_key': auth_key}
    body = {'name': name, 'animal_type': animal_type}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_12_create_pet_numeric_data(auth_key=auth_key, name=123, animal_type=456, age=987):
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'auth_key': auth_key}
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_13_create_pet_no_ct_type(auth_key=auth_key, name='Doggie', animal_type='dog', age=''):
    headers = {'auth_key': auth_key}
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_14_create_pet_multiple_ct_type(auth_key=auth_key, name='Doggie', animal_type='dog', age=3,
                    ct_type='application/xml; application/x-www-form-urlencoded; application/form-data; text/plain'):
    headers = {'Content-Type': ct_type, 'auth_key': auth_key}
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 415
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_15_create_pet_ct_type_255(auth_key=auth_key, name='Doggie', animal_type='dog', age=3, ct_type=rnd_str(255)):
    headers = {'Content-Type': ct_type, 'auth_key': auth_key}
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 415
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_16_create_pet_multiple_ct_type(auth_key=auth_key, name='Doggie', animal_type='dog', age=3,
                    ct_type=rnd_str(1025)):
    headers = {'Content-Type': ct_type, 'auth_key': auth_key}
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 415
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_17_create_pet_ct_type_symbols(auth_key=auth_key, name='Doggie', animal_type='dog', age=3,
                    ct_type=rnd_str(15, 's')):
    headers = {'Content-Type': ct_type, 'auth_key': auth_key}
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 415
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_18_create_pet_non_ascii_ct_type(auth_key=auth_key, name='Doggie', animal_type='dog', age=3,
                    ct_type=rnd_str(15, 'ru')):
    headers = {'Content-Type': ct_type, 'auth_key': auth_key}
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    t = datetime.utcnow()
    t2 = datetime.utcnow()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    assert status == 415
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_19_create_pet_no_key(name='Doggie', animal_type='dog', age=3):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_20_create_pet_wrong_key(auth_key='asdf', name='Doggie', animal_type='dog', age=3):
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'auth_key': auth_key}
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_21_create_pet_auth_key_255(auth_key=rnd_str(255), name='Doggie', animal_type='dog', age=3):
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'auth_key': auth_key}
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_22_create_pet_auth_key_1025(auth_key=rnd_str(1025), name='Doggie', animal_type='dog', age=3):
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'auth_key': auth_key}
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_23_create_pet_auth_key_symbols(auth_key=rnd_str(15, 's'), name='Doggie', animal_type='dog', age=3):
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'auth_key': auth_key}
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_24_create_pet_auth_key_non_ascii(auth_key=rnd_str(15, 'ru'), name='Doggie', animal_type='dog', age=3):
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'auth_key': auth_key}
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_25_create_pet_auth_key(auth_key=234, name='Doggie', animal_type='dog', age=3):
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'auth_key': auth_key}
    body = {'name': name, 'animal_type': animal_type, 'age': age}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/create_pet_simple', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)
