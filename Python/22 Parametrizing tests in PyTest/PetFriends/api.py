import os
import pytest
import random
import requests
import json
from requests_toolbelt import MultipartEncoder
from datetime import datetime
from time import sleep
from settings import valid_email, valid_password, expired_auth_key, base_url, log_path, log_file
expired_key = None


def empty_log_folder() -> bool:
    """
    deletes all old log files in log path
    :return: True in case when everything was fine, else assertion error
    """
    try:
        for f in os.listdir(log_path):
            if '/' in f.replace('\\', '/'):
                f = f[f.replace('\\', '/').rindex('/') + 1:]
            if f[:4] == 'log_' and f[-4:] == '.txt' and f[4:12] != datetime.utcnow().strftime('%Y%m%d'):
                try:
                    os.remove(os.path.join(log_path, f))
                except Exception as e:
                    assert 'Error removing file: ' + str(e) == ''
        return True
    except Exception as e:
        assert 'Error cleaning logs folder: ' + str(e) == ''


def log_request(response: requests.Response, time: float) -> bool:
    """
    opens log_file in log_path and appends request log
    :param response: Response object
    :param time: request execution time
    :return: bool that indicates that log has been successful or not
    """
    f = None
    # check if path exists and create it if not
    if not os.path.exists(log_path):
        try:
            os.mkdir(log_path)
        except Exception:
            pass
    # if path have been created, try to open log file
    if os.path.exists(log_path):
        try:
            f = open(os.path.join(log_path, log_file), 'a', encoding='utf-8')
            # write file headers
            f.write('\n' + ('=' * 16) + '\n=== ' + datetime.utcnow().strftime('%H:%M:%S'))
            f.write(' ===\n' + ('=' * 16) + '\n\n')
            # remove logs with date different from today
            try:
                empty_log_folder()
            except Exception:
                # if we cannot delete an older file, just skip it
                pass
        except Exception:
            # in case we couldn't open a file, just make it None to skip the next section
            f = None
    if f:
        # log started.
        # write request in way: GET https://site.domain.com/path/{params} <time with milliseconds>
        f.write(f'{response.request.method} {response.request.url} ({datetime.utcnow().strftime("%H:%M:%S.%f")})\n')
        # write request headers if those exist
        if response.request.headers:
            f.write(f' - headers: {response.request.headers}\n')
        # write request's body if it is not empty
        if response.request.body:
            f.write(f' - body: {response.request.body}\n')
        # execution time
        f.write(f' - execution time: {time} sec.\n')
        # status code
        f.write(f' - Status: {response.status_code}\n')
        # response headers
        if response.headers:
            f.write(f' - response headers: {response.headers}\n')
        # response cookies if those exist
        try:
            f.write(f' - response cookies: {dict(response.cookies)}\n')
        except ValueError:
            pass
        try:
            # get response as json format
            j = response.json()
            # log type of response data
            f.write(f' - response data: {type(j)}')
            if type(j) == list:
                # if response is a list, then log the 1st item in the list
                l = len(j)
                f.write(f' of {l} items')
                if l:
                    j = j[0]
                    f.write('  - first item:\n')
            if type(j) == dict:
                # if body is a dict, then write its {key: value} pairs
                f.write('\n  {\n')
                for i in j.items():
                    if type(i[1]) == dict:
                        # if value is also a dictionary, write its contents
                        f.write('    {' + (', '.join('\'' + k[0] + '\': '
                                                     + (k[1] if type(k[1]) == int else ('\'' + k[1] + '\''))
                                                     for k in i[1].items())) + '}')
                    elif type(i[1]) == list:
                        # if a value is a list, write the 1st value
                        l = len(i[1])
                        if l:
                            s = f'    [\n'
                            if type(i[1][0]) == dict:
                                # write dict if it is a dict
                                s += '   {\n     ' \
                                     + (',\n     '.join('\'' + k[0] + '\': '
                                                        + (k[1] if type(k[1]) == int else '\'' + str(k[1])[:32] + '\'')
                                                        for k in i[1][0].items())) + '}'
                            elif type(i[1][0]) in [int, float]:
                                # if it's a number, write without quotes
                                s += i[1][0]
                            else:
                                # write value in quotes
                                s += '\'' + i[1][0] + '\''
                            s += ']\n' if len(s) < 2 else f', ... (total {l} items)]\n'
                            f.write(s)
                        else:
                            # write an empty list if it is empty
                            f.write('    []\n')
                    else:
                        # value is neither dict, nor list. write its type and first 64 letters of its str() value
                        f.write(f'    \'{i[0]}\': ({type(i[1])}) \'{str(i[1])[:64]}')
                        if len(str(i[1])) > 64:
                            f.write('...')
                        f.write('\'\n')
                # close dict bracket
                f.write('  }\n')
            else:
                # body is not list or dict. Just convert it to str() and write 1st 128 characters
                f.write(str(j)[:128] + '\n')
            # end log with new line
            f.write('\n')
            return True
        except ValueError:
            # response body cannot be converted from json. Just write its 1st 128 characters or the 1st line
            s = response.text[:128]
            if '\n' in s:
                s = s[:s.index('\n')]
            f.write(f' - response data (1st line): {s}\n\n')
            return True
    return False


@pytest.fixture(scope='session')
def get_key():
    global expired_key
    # sent request to get api key
    status, _, data, _ = request('get', 'api/key', headers={'email': valid_email, 'password': valid_password})
    # check it is successful, and we have a key, then return the key
    assert status == 200
    assert type(data) == dict and 'key' in data.keys()
    if expired_key and data['key'] == expired_key or data['key'] == expired_auth_key:
        expired_key = None
    elif data['key'] != expired_auth_key and expired_auth_key:
        expired_key = expired_auth_key
    return data['key']


@pytest.fixture(scope='function', autouse=True)
def sleep_between_tests():
    sleep(0.5)


def request(method: str, path: str, ct_type:str=None, headers:dict=None, params:dict=None, body=None):
    """
    Sends http request to server
    :param method: request method
    :param path: request path regarding {base_url}
    :param ct_type: Content-Type if it should be added to headers
    :param headers: request heaaders
    :param params: dict with path parameters like, filter=my_pets
    :param body: dict or MultipartEncoder / json str with body
    :return: tuple of 4 items: (status_code: int, headers: dict, response_body: (dict, list, str), exec_time: float)
    """
    url = base_url + path
    if params and type(params) == dict:
        url += '?' + '&'.join(str(p[0]) + '=' + str(p[1]) for p in params.items())
    if ct_type:
        if type(headers) == dict:
            headers['Content-Type'] = ct_type
        else:
            headers = {'Content-Type': str(ct_type)}
    if type(headers) == dict and 'Content-Type' in headers.keys():
        if headers['Content-Type'] in ['application/json', 'json']:
            headers['Content-Type'] = 'application/json'
            if body and type(body) == dict:
                for k in body.keys():
                    if type(body[k]) != str:
                        body[k] = str(body[k])
                body = json.dumps(body, ensure_ascii=False)
        elif body and headers['Content-Type'] in ['form-data', 'multipart/form-data', 'multipart']:
            headers['Content-Type'] = 'multipart/form-data'
            if type(body) == dict:
                body = MultipartEncoder(body)
            if type(body) == MultipartEncoder:
                headers['Content-Type'] = body.content_type
            else:
                body = None
    if not body:
        body = None
    if not params:
        params = None
    if not headers:
        headers = None
    t = datetime.utcnow()
    resp = requests.request(method.upper(), base_url + path, headers=headers, params=params, data=body)
    exec_time = (datetime.utcnow() - t).total_seconds()
    assert log_request(resp, exec_time)
    try:
        return resp.status_code, resp.headers, resp.json(), exec_time
    except ValueError:
        return resp.status_code, resp.headers, resp.text, exec_time


def rnd_str(length:int=15, symbols='ld'):
    """
    generates str of specified length
    :param length: length of generated string
    :param symbols: types of symbols. Default 'ld'.
        - 'l' - Latin letters,
        - 'd' - digits,
        - 's' - special symbols (ASCII)
        - 'a' - Arabian symbols
        - 'g' - Greek symbols
        - 'r' - Russian letters
        - 'u' - some of non-ASCII letters(Thai, Hebrew)
    :return:
    """
    if type(length) != int or type(symbols) != str:
        return ''
    for s in symbols:
        if s not in 'ldsrag':
            return ''.join(random.choices(symbols, k = length))
    l = 'qwertyuiopasdfghjklzxcvbnm' #letters
    d = '0123456789' # digits
    s = '~`!@#$%^&*()\\|/.,"\';:?[]{}' # special symbols
    r = 'йцукенгшщзхъфывапролджэячсмитьбю' # Russian letters
    a = '؆؇؈؉؊؋،؍؎؏ؠءآأؤإئابةتثجحخدذرزسشصضطظعغػؼؽؾؿـفقكلمنهوىي' # Arabic letters
    g = 'αβγδεζηθικλμνξοπρςστυφχψω' # Greek letters
    string = l + l.upper() if 'l' in symbols else ''
    string += d if 'd' in symbols else ''
    string += s if 's' in symbols else ''
    string += r + r.upper() if 'r' in symbols else ''
    string += u + u.upper() if 'u' in symbols else ''
    return ''.join(random.choices(string, k = length))
