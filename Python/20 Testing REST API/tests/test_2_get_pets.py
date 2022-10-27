from api import *
from settings import valid_email, valid_password, expired_api_key
from datetime import datetime, timedelta

def get_valid_key():
    key = get_key()
    if key[:6] == 'ERROR:':
        return ''
    else:
        return key


valid_key = get_valid_key()
pet_headers = ['age', 'animal_type', 'created_at', 'id', 'name', 'pet_photo']
opt_headers = ['user_id', '_id']


def test_1_get_pets_positive_nofilter(auth_key=valid_key, filter=None):
    assert 50 < len(auth_key) < 65
    headers = {'auth_key': auth_key}
    params = {'filter': filter} if filter != None else None
    t = datetime.now()
    status, headers, resp = request('get', 'api/pets', headers=headers, params=params)
    assert status == 200
    assert headers['Content-Type'] == 'application/json' and 'date' in headers.keys()
    assert type(resp) == dict and 'pets' in resp.keys()
    assert chk_structure(resp['pets']) == ''
    assert datetime.now() - t < timedelta(seconds=1)


def test_2_get_pets_positive_w_filter(auth_key=valid_key, filter='my_pets'):
    assert 50 < len(auth_key) < 65
    headers = {'auth_key': auth_key}
    params = {'filter': filter} if filter != None else None
    t = datetime.now()
    status, headers, resp = request('get', 'api/pets', headers=headers, params=params)
    assert status == 200
    assert headers['Content-Type'] == 'application/json' and 'date' in headers.keys()
    assert type(resp) == dict and 'pets' in resp.keys()
    assert chk_structure(resp['pets']) == ''
    assert datetime.now() - t < timedelta(seconds=1)


def test_3_get_pets_empty_filter(auth_key=valid_key, filter=''):
    headers = {'auth_key': auth_key}
    params = {'filter': filter} if filter != None else None
    t = datetime.now()
    status, headers, resp = request('get', 'api/pets', headers=headers, params=params)
    assert status == 200
    assert headers['Content-Type'] == 'application/json' and 'date' in headers.keys()
    assert type(resp) == dict and 'pets' in resp.keys()
    assert chk_structure(resp['pets']) == ''
    assert datetime.now() - t < timedelta(seconds=1)


def test_4_get_pets_expired_key(auth_key=expired_api_key, filter='my_pets'):
    print(valid_key, expired_api_key)
    assert auth_key and auth_key != valid_key
    headers = {'auth_key': auth_key}
    params = {'filter': filter} if filter != None else None
    t = datetime.now()
    status, headers, resp = request('get', 'api/pets', headers=headers, params=params)
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8' and 'date' in headers.keys()
    assert datetime.now() - t < timedelta(seconds=1)


def test_5_get_pets_missing_key(filter=None):
    params = {'filter': filter} if filter != None else None
    t = datetime.now()
    status, headers, resp = request('get', 'api/pets', params=params)
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8' and 'date' in headers.keys()
    assert datetime.now() - t < timedelta(seconds=1)


def test_6_get_pets_empty_key(auth_key='', filter='my_pets'):
    assert auth_key != valid_key
    headers = {'auth_key': auth_key}
    params = {'filter': filter} if filter != None else None
    t = datetime.now()
    status, headers, resp = request('get', 'api/pets', headers=headers, params=params)
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8' and 'date' in headers.keys()
    assert datetime.now() - t < timedelta(seconds=1)

def test_7_get_pets_wrong_key(auth_key='abc', filter='my_pets'):
    headers = {'auth_key': auth_key}
    params = {'filter': filter} if filter != None else None
    t = datetime.now()
    status, headers, resp = request('get', 'api/pets', headers=headers, params=params)
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8' and 'date' in headers.keys()
    assert datetime.now() - t < timedelta(seconds=1)


def test_8_get_pets_auth_key_255_symbols(auth_key=rnd_str(255), filter='my_pets'):
    headers = {'auth_key': auth_key}
    params = {'filter': filter} if filter != None else None
    t = datetime.now()
    status, headers, resp = request('get', 'api/pets', headers=headers, params=params)
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8' and 'date' in headers.keys()
    assert datetime.now() - t < timedelta(seconds=1)


def test_9_get_pets_auth_key_1025_symbols(auth_key=rnd_str(1025), filter='my_pets'):
    headers = {'auth_key': auth_key}
    params = {'filter': filter} if filter != None else None
    t = datetime.now()
    status, headers, resp = request('get', 'api/pets', headers=headers, params=params)
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8' and 'date' in headers.keys()
    assert datetime.now() - t < timedelta(seconds=1)


def test_10_get_pets_auth_key_special_symbols(auth_key=rnd_str(15, 's'), filter='my_pets'):
    headers = {'auth_key': auth_key}
    params = {'filter': filter} if filter != None else None
    t = datetime.now()
    status, headers, resp = request('get', 'api/pets', headers=headers, params=params)
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8' and 'date' in headers.keys()
    assert datetime.now() - t < timedelta(seconds=1)


def test_11_get_pets_auth_key_non_ascii(auth_key=rnd_str(15, 'ru'), filter='my_pets'):
    headers = {'auth_key': auth_key}
    params = {'filter': filter} if filter != None else None
    t = datetime.now()
    status, headers, resp = request('get', 'api/pets', headers=headers, params=params)
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8' and 'date' in headers.keys()
    assert datetime.now() - t < timedelta(seconds=1)


# cannot send request with a number in headers
def test_12_get_pets_auth_key_number(auth_key=1354, filter='my_pets'):
    assert auth_key != valid_key
    headers = {'auth_key': auth_key}
    params = {'filter': filter} if filter != None else None
    t = datetime.now()
    status, headers, resp = request('get', 'api/pets', headers=headers, params=params)
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8' and 'date' in headers.keys()
    assert datetime.now() - t < timedelta(seconds=1)


def test_13_get_pets_wrong_method(method='patch', auth_key=valid_key, filter='my_pets'):
    headers = {'auth_key': auth_key}
    params = {'filter': filter} if filter != None else None
    t = datetime.now()
    status, headers, resp = request(method, 'api/pets', headers=headers, params=params)
    assert status == 405
    assert headers['Content-Type'] == 'text/html; charset=utf-8' and 'date' in headers.keys()
    assert datetime.now() - t < timedelta(seconds=1)


def test_14_get_pets_wrong_ct_type(auth_key=valid_key, filter='pets', content_type='application/xml; '
                                    'application/x-www-form-urlencoded; multipart/form-data; text/plain'):
    assert 50 < len(auth_key) < 65
    headers = {'auth_key': auth_key}
    if content_type: headers['Content-Type'] = content_type
    params = {'filter': filter} if filter != None else None
    t = datetime.now()
    status, headers, resp = request('get', 'api/pets', headers=headers, params=params)
    assert status == 415
    assert headers['Content-Type'] == 'text/html; charset=utf-8' and 'date' in headers.keys()
    assert datetime.now() - t < timedelta(seconds=1)


def test_15_get_pets_wrong_filter(auth_key=valid_key, filter='pets'):
    assert 50 < len(auth_key) < 65
    headers = {'auth_key': auth_key}
    params = {'filter': filter} if filter != None else None
    t = datetime.now()
    status, headers, resp = request('get', 'api/pets', headers=headers, params=params)
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8' and 'date' in headers.keys()
    assert datetime.now() - t < timedelta(seconds=1)


def test_16_get_pets_filter_255(auth_key=valid_key, filter=rnd_str(255)):
    assert 50 < len(auth_key) < 65
    headers = {'auth_key': auth_key}
    params = {'filter': filter} if filter != None else None
    t = datetime.now()
    status, headers, resp = request('get', 'api/pets', headers=headers, params=params)
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8' and 'date' in headers.keys()
    assert datetime.now() - t < timedelta(seconds=1)


def test_17_get_pets_filter_1025(auth_key=valid_key, filter=rnd_str(1025)):
    assert 50 < len(auth_key) < 65
    headers = {'auth_key': auth_key}
    params = {'filter': filter} if filter != None else None
    t = datetime.now()
    status, headers, resp = request('get', 'api/pets', headers=headers, params=params)
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8' and 'date' in headers.keys()
    assert datetime.now() - t < timedelta(seconds=1)


def test_18_get_pets_filter_spec_symbols(auth_key=valid_key, filter=rnd_str(symbols='s')):
    assert 50 < len(auth_key) < 65
    headers = {'auth_key': auth_key}
    params = {'filter': filter} if filter != None else None
    t = datetime.now()
    status, headers, resp = request('get', 'api/pets', headers=headers, params=params)
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8' and 'date' in headers.keys()
    assert datetime.now() - t < timedelta(seconds=1)


def test_19_get_pets_non_ascii_filter(auth_key=valid_key, filter=rnd_str(symbols='ru')):
    assert 50 < len(auth_key) < 65
    headers = {'auth_key': auth_key}
    params = {'filter': filter} if filter != None else None
    t = datetime.now()
    status, headers, resp = request('get', 'api/pets', headers=headers, params=params)
    assert status == 400
    assert headers['Content-Type'] == 'text/html; charset=utf-8' and 'date' in headers.keys()
    assert datetime.now() - t < timedelta(seconds=1)
