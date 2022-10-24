from api import *
from datetime import datetime, timedelta
from settings import valid_email, valid_password, expired_api_key, correct_photo_path, \
    correct_photo, large_photo, text_file, broken_photo
from requests_toolbelt import MultipartEncoder
from urllib.parse import quote_plus


auth_key = get_key()
if auth_key[:6] == 'ERROR:':
    auth_key = ''


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
                                  'pet_photo': f if f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.now()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    assert status == 200
    assert chk_structure(resp) == ''
    assert check_pet(resp, name, animal_type, age, 'data:' + f[2] + ';base64,*')
    assert datetime.now() - t < timedelta(seconds=1)


def test_2_wrong_auth_key(api_key='asdf', name='Doggie', animal_type='dog', age='5', pet_photo=correct_photo):
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
    t = datetime.now()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_3_missing_auth_key(name='Doggie', animal_type='dog', age='5', pet_photo=correct_photo):
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
    t = datetime.now()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_4_utf8_data_positive(api_key=auth_key, name='Барбос', animal_type='пёс', age='4', pet_photo=correct_photo):
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
    t = datetime.now()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    assert status == 200
    assert chk_structure(resp) == ''
    assert check_pet(resp, name, animal_type, age, 'data:' + f[2] + ';base64,*')
    assert datetime.now() - t < timedelta(seconds=1)


def test_5_missing_name_wrong_age(api_key=auth_key, age='тры', pet_photo=correct_photo):
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
    t = datetime.now()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_6_missing_name_type_age(api_key=auth_key, pet_photo=correct_photo):
    if pet_photo:
        try:
            f = get_photo(pet_photo)
        except Exception as e:
            assert str(e) == '' # read error message
    else:
        f = ''
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'pet_photo': f if f[0] else ''})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.now()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_7_all_data_str_255(api_key=auth_key, name=rnd_str(255), animal_type=rnd_str(255), age=rnd_str(255),
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
    t = datetime.now()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_8_data_str_1025(api_key=auth_key, name=rnd_str(1025), animal_type=rnd_str(1025), age=rnd_str(1025),
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
    t = datetime.now()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_9_spec_symbols(api_key=auth_key, name=rnd_str(15, 's'), animal_type=rnd_str(15, 's'), age=rnd_str(15, 's'),
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
    t = datetime.now()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_10_numeric_data(api_key=auth_key, name=4, animal_type=234, age=-33, pet_photo=correct_photo):
    if pet_photo:
        try:
            f = get_photo(pet_photo)
        except Exception as e:
            assert str(e) == '' # read error message
    else:
        f = ''
    # prepare and send request to add photo
    body={'name': name, 'animal_type': animal_type, 'age': str(age), 'pet_photo': f if f[0] else ''}
    headers = {'Content-Type': 'x-www-form-urlencoded', 'auth_key': api_key}
    t = datetime.now()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_11_empty_photo(api_key=auth_key, name='Doggie', animal_type='dog', age='5', pet_photo=''):
    f = ''
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'name': name, 'animal_type': animal_type, 'age': str(age), 'pet_photo': f})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.now()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_12_missing_photo(api_key=auth_key, name='Doggie', animal_type='dog', age='5'):
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'name': name, 'animal_type': animal_type, 'age': str(age)})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.now()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_13_text_file(api_key=auth_key, name='Doggie', animal_type='dog', age='5', pet_photo=text_file):
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
    t = datetime.now()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_14_large_photo(api_key=auth_key, name='Doggie', animal_type='dog', age='5', pet_photo=large_photo):
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
    t = datetime.now()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_15_corrupted_base64_encoding(api_key=auth_key, name='Doggie', animal_type='dog', age='5',
                                      pet_photo=broken_photo()):
    body=MultipartEncoder(fields={'name': name, 'animal_type': animal_type, 'age': str(age),
                                  'pet_photo': ('broken_photo.jpg', pet_photo, 'image/jpg')})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.now()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_16_photo_spec_symbols(api_key=auth_key, name='Doggie', animal_type='dog', age='5', pet_photo=rnd_str(15, 's')):
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'name': name, 'animal_type': animal_type, 'age': str(age), 'pet_photo': pet_photo})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.now()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_17_non_ascii_photo(api_key=auth_key, name='Doggie', animal_type='dog', age='5', pet_photo=rnd_str('15', 'ru')):
    # prepare and send request to add photo
    body=MultipartEncoder(fields={'name': name, 'animal_type': animal_type, 'age': str(age),
                                  'pet_photo': ('photo.jpg', pet_photo, 'image/jpg')})
    headers = {'Content-Type': body.content_type, 'auth_key': api_key}
    t = datetime.now()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)


def test_18_incorrect_content_type(api_key=auth_key, name='Doggie', animal_type='dog', age='5', pet_photo=correct_photo):
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
    headers = {'Content-Type': f'application/json; text/html; {body.content_type}', 'auth_key': api_key}
    t = datetime.now()
    status, headers, resp = request('post', 'api/pets', headers=headers, body=body)
    assert status == 415
    assert headers['Content-Type'] == 'text/html; charset=utf-8'
    assert datetime.now() - t < timedelta(seconds=1)
