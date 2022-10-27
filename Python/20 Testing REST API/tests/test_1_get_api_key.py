from api import *
from datetime import datetime, timedelta
from settings import valid_email, valid_password

def test_1_1_get_api_key_positive(email=valid_email, password=valid_password):
    headers = {'Content-Type': 'x-www-form-urlencoded', 'email': email, 'password': password}
    t = datetime.now()
    status, headers, resp = request('GET', 'api/key', headers=headers)
    assert status == 200
    assert headers['Content-Type'] == 'application/json' and 'date' in headers.keys()
    assert type(resp) == dict and 'key' in resp.keys() and 50 < len(resp['key']) < 100
    assert datetime.now() - t < timedelta(seconds=1)


def test_1_2_get_api_key_empty_data(email='', password=''):
    headers = {'Content-Type': 'x-www-form-urlencoded', 'email': email, 'password': password}
    t = datetime.now()
    status, headers, resp = request('GET', 'api/key', headers=headers)
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8' and 'date' in headers.keys()
    assert datetime.now() - t < timedelta(seconds=1)


def test_1_3_get_api_key_empty_pw(email=valid_email, password=''):
    headers = {'Content-Type': 'x-www-form-urlencoded', 'email': email, 'password': password}
    t = datetime.now()
    status, headers, resp = request('GET', 'api/key', headers=headers)
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8' and 'date' in headers.keys()
    assert datetime.now() - t < timedelta(seconds=1)


def test_1_4_get_api_key_wrong_pw(email=valid_email, password=rnd_str()):
    headers = {'Content-Type': 'x-www-form-urlencoded', 'email': email, 'password': password}
    t = datetime.now()
    status, headers, resp = request('GET', 'api/key', headers=headers)
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8' and 'date' in headers.keys()
    assert datetime.now() - t < timedelta(seconds=1)


def test_1_5_get_api_key_wrong_email_pw(email=rnd_str(), password=rnd_str(15, 'lds')):
    headers = {'Content-Type': 'x-www-form-urlencoded', 'email': email, 'password': password}
    t = datetime.now()
    status, headers, resp = request('GET', 'api/key', headers=headers)
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8' and 'date' in headers.keys()
    assert datetime.now() - t < timedelta(seconds=1)


def test_1_6_get_api_key_no_email_pw():
    t = datetime.now()
    status, headers, resp = request('GET', 'api/key')
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8' and 'date' in headers.keys()
    assert datetime.now() - t < timedelta(seconds=1)


def test_1_7_get_api_key_wrong_ct_type(email=valid_email, password=valid_password, content_type='text/html; applica' \
                                      'tion/json; multipart/form-data; application/x-www-form-urlencoded'):
    headers = {'Content-Type': content_type, 'email': email, 'password': password}
    t = datetime.now()
    status, headers, resp = request('GET', 'api/key', headers=headers)
    assert status == 415
    assert headers['Content-Type'] == 'text/html; charset=utf-8' and 'date' in headers.keys()
    assert datetime.now() - t < timedelta(seconds=1)


def test_1_8_get_api_key_post(email=valid_email, password=valid_password, method='POST'):
    headers = {'Content-Type': 'x-www-form-urlencoded', 'email': email, 'password': password}
    status, headers, resp = request(method, 'api/key', headers=headers)
    t = datetime.now()
    assert status == 405
    assert headers['Content-Type'] == 'text/html; charset=utf-8' and 'date' in headers.keys()
    assert datetime.now() - t < timedelta(seconds=1)


def test_1_9_get_api_key_str_255(email=rnd_str(255), password=rnd_str(255)):
    headers = {'Content-Type': 'x-www-form-urlencoded', 'email': email, 'password': password}
    t = datetime.now()
    status, headers, resp = request('GET', 'api/key', headers=headers)
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8' and 'date' in headers.keys()
    assert datetime.now() - t < timedelta(seconds=1)


def test_1_10_get_api_key_str_1025(email=rnd_str(1025), password=rnd_str(1025)):
    headers = {'Content-Type': 'x-www-form-urlencoded', 'email': email, 'password': password}
    t = datetime.now()
    status, headers, resp = request('GET', 'api/key', headers=headers)
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8' and 'date' in headers.keys()

def test_1_11_get_api_key_special_symbols(email=rnd_str(symbols='s'), password=rnd_str(symbols='s')):
    headers = {'Content-Type': 'x-www-form-urlencoded', 'email': email, 'password': password}
    assert datetime.now() - t < timedelta(seconds=1)
    t = datetime.now()
    status, headers, resp = request('GET', 'api/key', headers=headers)
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8' and 'date' in headers.keys()
    assert datetime.now() - t < timedelta(seconds=1)


def test_1_12_get_api_key_unicode(email=rnd_str(symbols='ru'), password=rnd_str(symbols='ru')):
    headers = {'Content-Type': 'x-www-form-urlencoded', 'email': email, 'password': password}
    t = datetime.now()
    status, headers, resp = request('GET', 'api/key', headers=headers)
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8' and 'date' in headers.keys()
    assert datetime.now() - t < timedelta(seconds=1)


def test_1_13_get_api_key_numeric(email=3, password=4):
    headers = {'Content-Type': 'application/json'}
    body = {'email': email, 'password': password}
    t = datetime.now()
    status, headers, resp = request('GET', 'api/key', headers=headers, body=body)
    assert status == 403
    assert headers['Content-Type'] == 'text/html; charset=utf-8' and 'date' in headers.keys()
    assert datetime.now() - t < timedelta(seconds=1)
