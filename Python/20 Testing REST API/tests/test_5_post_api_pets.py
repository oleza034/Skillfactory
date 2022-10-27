import base64

from api import *
from datetime import datetime, timedelta
from settings import valid_email, valid_password, expired_api_key, correct_photo_path, \
    correct_photo, large_photo, text_file, broken_photo
from requests_toolbelt import MultipartEncoder
from urllib.parse import quote_plus


auth_key = get_key()
if auth_key[:6] == 'ERROR:':
    auth_key = ''


def base64_encode(f) -> str:
    code_table = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
    i = 1
    s = ''
    try:
        char = f.read(1)
        c = [ord(char), None, None]
    except Exception:
        c = [None, None, None]
    while char := f.read(1):
        if not i:
            c = [ord(char), None, None]
        else:
            c[i] = ord(char)
            if i == 2:
                """
                decoded |         0         |         1         |         2         |
                        | 7 6 5 4 3 2   1 0 | 7 6 5 4   3 2 1 0 | 7 6   5 4 3 2 1 0 |
                        | 5 4 3 2 1 0 | 5 4   3 2 1 0 | 5 4 3 2 | 1 0 | 5 4 3 2 1 0 |
                encoded |      0      |       1       |       2       |      3      |
                """
                s += code_table[c[0] // 4] + code_table[16 * (c[0] % 4) + (c[1] // 16)] + \
                     code_table[4 * (c[1] % 16) + (c[2] // 64)] + code_table[c[2] % 64]
        i = (i + 1) if i < 2 else 0
    if c[0] != None and c[2] == None:
        s = code_table[c[0] // 4] + code_table[16 * (c[0] % 4) + ((c[1] // 16) if c[1] else 0)]
        if c[1] != None:
            s += code_table[4 * (c[1] % 16) + ((c[2] // 64) if c[2] else 0)]
            if c[2] != None:
                s += code_table[c[2] % 64]
            else:
                s += '='
        else:
            s += '=='
    return s


def test_1_positive(api_key=auth_key, name='Doggie', animal_type='dog', age='5', pet_photo=correct_photo):
    if pet_photo:
        try:
            f = get_photo(pet_photo)
        except Exception as e:
            assert str(e) == '' # read error message
    else:
        f = ''
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'name': name, 'animal_type': animal_type, 'age': str(age),
                                  'pet_photo': f if type(f) == tuple and f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 200
    assert headers['Content-Type'] == 'application/json'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert chk_structure(resp) == ''
    assert check_pet(resp, name, animal_type, age, 'data:' + f[2] + ';base64,*')
    assert t2 - t < timedelta(seconds=1)


def test_2_(api_key=auth_key, name='Барбос', animal_type='собака', age='пять', pet_photo=correct_photo):
    if pet_photo:
        try:
            f = get_photo(pet_photo)
        except Exception as e:
            assert str(e) == '' # read error message
    else:
        f = ''
    # prepare and send request to add photo
    body=MultipartEncoder({'name': name, 'animal_type': animal_type, 'age': str(age),
                           'pet_photo': f if type(f) == tuple and f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 200
    assert headers['Content-Type'] == 'application/json'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert chk_structure(resp) == ''
    assert check_pet(resp, name, animal_type, age, 'data:' + f[2] + ';base64,*')
    assert t2 - t < timedelta(seconds=1)


def test_3_empty_name(api_key=auth_key, name='', animal_type='dog', age='5', pet_photo=correct_photo):
    if pet_photo:
        try:
            f = get_photo(pet_photo)
        except Exception as e:
            assert str(e) == '' # read error message
    else:
        f = ''
    # prepare and send request to add photo
    body=MultipartEncoder({'name': name, 'animal_type': animal_type, 'age': str(age),
                           'pet_photo': f if type(f) == tuple and f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 200
    assert headers['Content-Type'] == 'application/json'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert chk_structure(resp) == ''
    assert check_pet(resp, name, animal_type, age, 'data:' + f[2] + ';base64,*')
    assert t2 - t < timedelta(seconds=1)


def test_4_empty_animal_type(api_key=auth_key, name='Doggie', animal_type='', age='5', pet_photo=correct_photo):
    if pet_photo:
        try:
            f = get_photo(pet_photo)
        except Exception as e:
            assert str(e) == '' # read error message
    else:
        f = ''
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'name': name, 'animal_type': animal_type, 'age': str(age),
                                  'pet_photo': f if type(f) == tuple and f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 200
    assert headers['Content-Type'] == 'application/json'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert chk_structure(resp) == ''
    assert check_pet(resp, name, animal_type, age, 'data:' + f[2] + ';base64,*')
    assert t2 - t < timedelta(seconds=1)


def test_5_empty_age(api_key=auth_key, name='Doggie', animal_type='dog', age='', pet_photo=correct_photo):
    if pet_photo:
        try:
            f = get_photo(pet_photo)
        except Exception as e:
            assert str(e) == '' # read error message
    else:
        f = ''
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'name': name, 'animal_type': animal_type, 'age': str(age),
                                  'pet_photo': f if type(f) == tuple and f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 200
    assert headers['Content-Type'] == 'application/json'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert chk_structure(resp) == ''
    assert check_pet(resp, name, animal_type, age, 'data:' + f[2] + ';base64,*')
    assert t2 - t < timedelta(seconds=1)


def test_6_empty_data(api_key=auth_key, name='', animal_type='', age='', pet_photo=correct_photo):
    if pet_photo:
        try:
            f = get_photo(pet_photo)
        except Exception as e:
            assert str(e) == '' # read error message
    else:
        f = ''
    # prepare and send request to add photo
    body=MultipartEncoder({'name': name, 'animal_type': animal_type, 'age': age,
                           'pet_photo': f if type(f) == tuple and f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 200
    assert headers['Content-Type'] == 'application/json'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert chk_structure(resp) == ''
    assert check_pet(resp, name, animal_type, age, 'data:' + f[2] + ';base64,*')
    assert t2 - t < timedelta(seconds=1)


def test_7_data_255(api_key=auth_key, name=rnd_str(255), animal_type=rnd_str(255), age=rnd_str(255),
                    pet_photo=correct_photo):
    if pet_photo:
        try:
            f = get_photo(pet_photo)
        except Exception as e:
            assert str(e) == '' # read error message
    else:
        f = ''
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'name': name, 'animal_type': animal_type, 'age': str(age),
                                  'pet_photo': f if type(f) == tuple and f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 200
    assert headers['Content-Type'] == 'application/json'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert chk_structure(resp) == ''
    assert check_pet(resp, name, animal_type, age, 'data:' + f[2] + ';base64,*')
    assert t2 - t < timedelta(seconds=1)


def test_8_data_1025(api_key=auth_key, name=rnd_str(1025), animal_type=rnd_str(1025), age=rnd_str(1025),
                     pet_photo=correct_photo):
    if pet_photo:
        try:
            f = get_photo(pet_photo)
        except Exception as e:
            assert str(e) == '' # read error message
    else:
        f = ''
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'name': name, 'animal_type': animal_type, 'age': str(age),
                                  'pet_photo': f if type(f) == tuple and f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 200
    assert headers['Content-Type'] == 'application/json'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert chk_structure(resp) == ''
    assert check_pet(resp, name, animal_type, age, 'data:' + f[2] + ';base64,*')
    assert t2 - t < timedelta(seconds=1)


def test_9_data_spec_symbols(api_key=auth_key, name=rnd_str(15, 's'), animal_type=rnd_str(15, 's'), age=rnd_str(15, 's'),
                             pet_photo=correct_photo):
    if pet_photo:
        try:
            f = get_photo(pet_photo)
        except Exception as e:
            assert str(e) == '' # read error message
    else:
        f = ''
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'name': name, 'animal_type': animal_type, 'age': str(age),
                                  'pet_photo': f if type(f) == tuple and f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 200
    assert headers['Content-Type'] == 'application/json'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert chk_structure(resp) == ''
    assert check_pet(resp, name, animal_type, age, 'data:' + f[2] + ';base64,*')
    assert t2 - t < timedelta(seconds=1)


def test_10_numeric_data(api_key=auth_key, name=123, animal_type=456, age=987, pet_photo=correct_photo):
    if pet_photo:
        try:
            f = get_photo(pet_photo)
        except Exception as e:
            assert str(e) == '' # read error message
    else:
        f = ''
    # prepare and send request to add photo
    body={'name': name, 'animal_type': animal_type, 'age': str(age), 'pet_photo': f if type(f) == tuple and f[0] else ''}
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 200
    assert headers['Content-Type'] == 'application/json'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert chk_structure(resp) == ''
    assert check_pet(resp, name, animal_type, age, 'data:' + f[2] + ';base64,*')
    assert t2 - t < timedelta(seconds=1)


def test_11_missing_name_animal_type(api_key=auth_key, age='тры', pet_photo=correct_photo):
    if pet_photo:
        try:
            f = get_photo(pet_photo)
        except Exception as e:
            assert str(e) == '' # read error message
    else:
        f = ''
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'age': str(age), 'pet_photo': f if f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_12_missing_age_pet_phoeo(api_key=auth_key, name='Kitty', animal_type='cat'):
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'name': name, 'animal_type': animal_type})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_13_missing_name_type_age(api_key=auth_key, pet_photo=correct_photo):
    if pet_photo:
        try:
            f = get_photo(pet_photo)
        except Exception as e:
            assert str(e) == '' # read error message
    else:
        f = ''
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'pet_photo': f if type(f) == tuple and f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_14_missing_body(api_key=auth_key):
    # prepare and send request to add photo
    headers = {'Content-Type': 'multipart/form-data', 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets', headers=headers)
    t2 = datetime.utcnow()
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_15_text_file(api_key=auth_key, name='Doggie', animal_type='dog', age='5', pet_photo=text_file):
    if pet_photo:
        try:
            f = get_photo(pet_photo)
        except Exception as e:
            assert str(e) == '' # read error message
    else:
        f = ''
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'name': name, 'animal_type': animal_type, 'age': str(age),
                                  'pet_photo': f if f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_16_large_photo(api_key=auth_key, name='Doggie', animal_type='dog', age='5', pet_photo=large_photo):
    if pet_photo:
        try:
            f = get_photo(pet_photo)
        except Exception as e:
            assert str(e) == '' # read error message
    else:
        f = ''
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'name': name, 'animal_type': animal_type, 'age': str(age),
                                  'pet_photo': f if f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_17_corrupted_base64_encoding(api_key=auth_key, name='Doggie', animal_type='dog', age='5',
                                      pet_photo=broken_photo()):
    body=MultipartEncoder(fields={'name': name, 'animal_type': animal_type, 'age': str(age),
                                  'pet_photo': ('broken_photo.jpg', pet_photo, 'image/jpg')})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_18_photo_spec_symbols(api_key=auth_key, name='Doggie', animal_type='dog', age='5', pet_photo=rnd_str(15, 's')):
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'name': name, 'animal_type': animal_type, 'age': str(age), 'pet_photo': pet_photo})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_19_non_ascii_photo(api_key=auth_key, name='Doggie', animal_type='dog', age='5', pet_photo=rnd_str('15', 'ru')):
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'name': name, 'animal_type': animal_type, 'age': str(age),
                                  'pet_photo': ('photo.jpg', pet_photo, 'image/jpg')})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_20_numeric_photo(api_key=auth_key, name='Doggie', animal_type='dog', age='5', pet_photo=234875621):
    # prepare and send request to add photo
    body=MultipartEncoder({'name': name, 'animal_type': animal_type, 'age': str(age),
                           'pet_photo': ('photo.jpg', pet_photo, 'image/jpg')})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_21_wrong_ct_type(api_key=auth_key, name='Doggie', animal_type='dog', age='5', pet_photo=correct_photo,
                             ct_type='application/json'):
    if pet_photo:
        try:
            f = get_photo(pet_photo)
        except Exception as e:
            assert str(e) == '' # read error message
    else:
        f = ''
    # prepare and send request to add photo
    body={'name': name, 'animal_type': animal_type, 'age': str(age),
          'pet_photo': (f[0], base64_encode(f[1]), f[2]) if f and f[0] else ''}
    headers = {'auth_key': api_key}
    if ct_type != None:
        headers['Content-Type'] = ct_type
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 415
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_22_missing_ct_type(api_key=auth_key, name='Doggie', animal_type='dog', age='5', pet_photo=correct_photo,
                            ct_type=None):
    if pet_photo:
        try:
            f = get_photo(pet_photo)
        except Exception as e:
            assert str(e) == '' # read error message
    else:
        f = ''
    # prepare and send request to add photo
    body={'name': name, 'animal_type': animal_type, 'age': str(age), 'pet_photo': f if f[0] else ''}
    headers = {'auth_key': api_key}
    if ct_type != None:
        headers['Content-Type'] = ct_type
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 415
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_23_multiple_ct_type(api_key=auth_key, name='Doggie', animal_type='dog', age='5', pet_photo=correct_photo,
                             ct_type='text/html; application/json; multipart/form-data'):
    if pet_photo:
        try:
            f = get_photo(pet_photo)
        except Exception as e:
            assert str(e) == '' # read error message
    else:
        f = ''
    # prepare and send request to add photo
    body={'name': name, 'animal_type': animal_type, 'age': str(age), 'pet_photo': f if f[0] else ''}
    headers = {'auth_key': api_key}
    if ct_type != None:
        headers['Content-Type'] = ct_type
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 415
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_24_ct_type_255(api_key=auth_key, name='Doggie', animal_type='dog', age='5', pet_photo=correct_photo,
                        ct_type=rnd_str(255)):
    if pet_photo:
        try:
            f = get_photo(pet_photo)
        except Exception as e:
            assert str(e) == '' # read error message
    else:
        f = ''
    # prepare and send request to add photo
    body={'name': name, 'animal_type': animal_type, 'age': str(age), 'pet_photo': f if f[0] else ''}
    headers = {'auth_key': api_key}
    if ct_type != None:
        headers['Content-Type'] = ct_type
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 415
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_25_ct_type_1025(api_key=auth_key, name='Doggie', animal_type='dog', age='5', pet_photo=correct_photo,
                         ct_type=rnd_str(1025)):
    if pet_photo:
        try:
            f = get_photo(pet_photo)
        except Exception as e:
            assert str(e) == '' # read error message
    else:
        f = ''
    # prepare and send request to add photo
    body={'name': name, 'animal_type': animal_type, 'age': str(age), 'pet_photo': f if f[0] else ''}
    headers = {'auth_key': api_key}
    if ct_type != None:
        headers['Content-Type'] = ct_type
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 415
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_26_ct_type_spec_symbols(api_key=auth_key, name='Doggie', animal_type='dog', age='5', pet_photo=correct_photo,
                                 ct_type=rnd_str(15, 's')):
    if pet_photo:
        try:
            f = get_photo(pet_photo)
        except Exception as e:
            assert str(e) == '' # read error message
    else:
        f = ''
    # prepare and send request to add photo
    body={'name': name, 'animal_type': animal_type, 'age': str(age), 'pet_photo': f if f[0] else ''}
    headers = {'auth_key': api_key}
    if ct_type != None:
        headers['Content-Type'] = ct_type
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 415
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_27_ct_type_non_ascii(api_key=auth_key, name='Doggie', animal_type='dog', age='5', pet_photo=correct_photo,
                              ct_type=rnd_str(15, 'ru')):
    if pet_photo:
        try:
            f = get_photo(pet_photo)
        except Exception as e:
            assert str(e) == '' # read error message
    else:
        f = ''
    # prepare and send request to add photo
    body={'name': name, 'animal_type': animal_type, 'age': str(age), 'pet_photo': f if f[0] else ''}
    headers = {'auth_key': api_key}
    if ct_type != None:
        headers['Content-Type'] = ct_type
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 415
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_28_expired_auth_key(api_key=expired_api_key, name='Doggie', animal_type='dog', age='5', pet_photo=correct_photo):
    if pet_photo:
        try:
            f = get_photo(pet_photo)
        except Exception as e:
            assert str(e) == '' # read error message
    else:
        f = ''
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'name': name, 'animal_type': animal_type, 'age': str(age),
                                  'pet_photo': f if f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_29_missing_auth_key(name='Doggie', animal_type='dog', age='5', pet_photo=correct_photo):
    if pet_photo:
        try:
            f = get_photo(pet_photo)
        except Exception as e:
            assert str(e) == '' # read error message
    else:
        f = ''
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'name': name, 'animal_type': animal_type, 'age': str(age),
                                  'pet_photo': f if f[0] else ''})
    headers = {'Content-Type': body.content_type}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_30_auth_key_255(api_key=rnd_str(255), name='Doggie', animal_type='dog', age='5', pet_photo=correct_photo):
    if pet_photo:
        try:
            f = get_photo(pet_photo)
        except Exception as e:
            assert str(e) == '' # read error message
    else:
        f = ''
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'name': name, 'animal_type': animal_type, 'age': str(age),
                                  'pet_photo': f if f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_31_auth_key_1025(api_key=rnd_str(1025), name='Doggie', animal_type='dog', age='5', pet_photo=correct_photo):
    if pet_photo:
        try:
            f = get_photo(pet_photo)
        except Exception as e:
            assert str(e) == '' # read error message
    else:
        f = ''
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'name': name, 'animal_type': animal_type, 'age': str(age),
                                  'pet_photo': f if f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_32_auth_key_symbols(api_key=rnd_str(15, 's'), name='Doggie', animal_type='dog', age='5', pet_photo=correct_photo):
    if pet_photo:
        try:
            f = get_photo(pet_photo)
        except Exception as e:
            assert str(e) == '' # read error message
    else:
        f = ''
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'name': name, 'animal_type': animal_type, 'age': str(age),
                                  'pet_photo': f if f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_33_auth_key_non_ascii(api_key=rnd_str(15, 'ru'), name='Doggie', animal_type='dog', age='5',
                               pet_photo=correct_photo):
    if pet_photo:
        try:
            f = get_photo(pet_photo)
        except Exception as e:
            assert str(e) == '' # read error message
    else:
        f = ''
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'name': name, 'animal_type': animal_type, 'age': str(age),
                                  'pet_photo': f if f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)


def test_34_numeric_auth_key(api_key=2357901, name='Doggie', animal_type='dog', age='5', pet_photo=correct_photo):
    if pet_photo:
        try:
            f = get_photo(pet_photo)
        except Exception as e:
            assert str(e) == '' # read error message
    else:
        f = ''
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'name': name, 'animal_type': animal_type, 'age': str(age),
                                  'pet_photo': f if f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.utcnow()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    t2 = datetime.utcnow()
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert t2 - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
    assert t2 - t < timedelta(seconds=1)
