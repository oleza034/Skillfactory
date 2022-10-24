import os.path

import requests
import random
import json
import urllib.parse
from requests_toolbelt import MultipartEncoder
from settings import base_url, valid_email, valid_password, email2, password2, correct_photo_path
from dateutil.parser import parse
from datetime import datetime


base_headers = {'accept': 'application/json'}


def request(method: str, path: str, ct_type=None, path_params=None, params=None, headers=None, body=None) -> tuple:
    """
    Prepares and sends a query to web server
    :param method: *Required*. Common values: 'GET', 'POST', etc.
    :param path: *Required*. Path to be added to base_url
    :param ct_type: *Optional*. Content-Type to be sent to server in headers. Can be 'application/json', \
        'application/x-www-form-urlencoded' or 'multipart/form-data'. Use with data parameter
    :param path_params: *Optional*. Parameter to add to path. For example pet_id will add /{pet_id}
    :param params: *Optional*. String parameters to add to request
    :param headers: *Optional*. Additional headers besides of base_headers to send with request
    :param body: *Optional*. Data to be sent. If data is dict and ct_type is specified, data will be transformed to \
                 content_type
    :return: response' status code, response headers and body
    """
    # compute URL
    url = base_url + path + (path_params if type(path_params) == str and path_params else '')
    if type(ct_type) == str:
        if '/' not in ct_type:
            # configure Content-Type to send. Also add first part before / if content-type is short
            # for example, 'json' will be transformed to 'application/json'
            content_type = ('multipart/' if ct_type == 'form-data' else ('application' if ct_type else '')) + ct_type
        else:
            content_type = ct_type
    # determine content-type
    elif type(headers) == dict and 'Content-Type' in headers.keys():
        content_type = '' + headers['Content-Type']
    else:
        content_type = ''
    # Transform body
    if type(body) in [dict, list]:
        if content_type == 'multipart/form_data':
            data = MultipartEncoder(fields=body)
            content_type = data.content_type
        elif content_type == 'application/json' or type(body) == list:
            data = json.dumps(body, ensure_ascii=False)
        else:
            data = body
    elif type(body) == MultipartEncoder:
        data = body
        content_type = data.content_type if content_type == 'multipart/form-data' else content_type
    else:
        data = None
    if type(headers) == dict:
        headers = base_headers | headers
    else:
        headers = base_headers
    # convert unicode headers
    for k in headers.keys():
        headers[k] = url_encode(headers[k])
    resp = requests.request(method, url, params=params, data=data, headers=headers)
    try:
        return resp.status_code, resp.headers, resp.json()
    except ValueError:
        return resp.status_code, resp.headers, resp.text


def get_photo(filename: str) -> tuple:
    """
    Tries to open a file and return it as byte stream; also checks for file MIME type
    :param filename: filename, for example, images/pet_photo.jpg
    :return: tuple of (file name, file as a byte stream, file MIME type)
    """
    if type(filename) != str or not filename:
        return '', 'filename is empty'
    extensions = {'.jpg': 'jpeg', '.jpeg': 'jpeg', '.png': 'png', '.gif': 'gif', '.txt': 'text/plain'}
    file_name = filename[filename.replace('\\', '/').rindex('/')+1:] if '/' in filename.replace('\\', '/') else filename
    ext = file_name[file_name.index('.'):] if '.' in file_name else ''
    f_type = extensions[ext] if ext in extensions.keys() else ''
    f_type = ('image/' if f_type and '/' not in f_type else '') + f_type
    try:
        f = open(filename, 'rb')
    except FileNotFoundError:
        try:
            f = open(os.path.join(os.path.dirname(__file__), filename), 'rb')
        except FileNotFoundError as e:
            try:
                f = open(os.path.join(os.path.dirname(__file__), correct_photo_path, filename), 'rb')
            except FileNotFoundError as e:
                return '', e, ''
    return file_name, f, f_type


def resp_headers(headers: dict, spaces: int = 0) -> str:
    """
    Transforms dict into readable str
    :param headers: dict to transform
    :param spaces: number of spaces in the left
    :return: str
    """
    s = ''
    for h in headers.items():
        if s:
            s += ',\n'
        s += (' ' * spaces) + f'- {h[0]}={h[1]}'
    return s


def url_encode(string: str) -> str:
    if not string or type(string) != str:
        return string
    new_string = ''
    for s in string:
        if ord(s) > 127:
            new_string += urllib.parse.quote_plus(s)
        else:
            new_string += s
    return new_string


def get_key(user_no: int = 1) -> str:
    if user_no == 1:
        email = valid_email
        pw = valid_password
    elif user_no == 2:
        email = email2
        pw = password2
    else:
        return ''
    status, _, resp = request('GET', 'api/key', headers={'email': email, 'password': pw})
    if status == 200 and type(resp) == dict and 'key' in resp.keys():
        return resp['key']
    else:
        return 'ERROR: ' + str(resp)


def rnd_str(length:int=15, symbols='ld'):
    """
    generates str of specified length
    :param length: length of generated string
    :param symbols: types of symbols. Default 'ld'.
        - 'l' - Latin letters,
        - 'd' - digits,
        - 's' - special symbols (ASCII)
        - 'r' - Russian letters
        - 'u' - some of non-ASCII letters(Thai, Hebrew)
    :return:
    """
    if type(length) != int or type(symbols) != str:
        return ''
    for s in symbols:
        if s not in 'ldsru':
            return ''.join(random.choices(symbols, k = length))
    l = 'qwertyuiopasdfghjklzxcvbnm' #letters
    d = '0123456789' # digits
    s = '~`!@#$%^&*()\\|/.,"\';:?[]{}' # special symbols
    r = 'йцукенгшщзхъфывапролджэячсмитьбю'
    u = 'ႠႡႢႣႤႥႦႧႨႩႪႫႬႭႯႰႱႲႳႴႵႶႷႸႹႺႻႼႽႾႿჀჁჂჃჄჅჇჍაბგდევზთიკლმნოპჟრსტუ฿ფ'
    string = l + l.upper() if 'l' in symbols else ''
    string += d if 'd' in symbols else ''
    string += s if 's' in symbols else ''
    string += r + r.upper() if 'r' in symbols else ''
    string += u + u.upper() if 'u' in symbols else ''
    return ''.join(random.choices(string, k = length))


def chk_structure(resp: any) -> str:
    required_headers = {'age': str, 'animal_type': str, 'created_at': 'datetime', 'id': 'uuid', 'name': str,
                        'pet_photo': str}
    optional_headers = {'user_id': 'uuid', '_id': any}
    all_headers = required_headers | optional_headers

    if type(resp) not in [dict, list]:
        return f'Wrong type: {type(resp)}'
    if type(resp) == dict:
        if 'pets' in resp.keys():
            pets = resp['pets']
            if type(pets) != list:
                return f'Wrong response: {resp}'
        pets = [resp]
    else:
        pets = resp
    for i in range(len(pets)):
        if type(pets[i]) != dict:
            return f'Type of {i} element is not dict: {pets[i]}'
        for k in pets[i].keys():
            if k not in all_headers.keys():
                return f'Wrong header in {i} element - {k}: {pets[i]}'
            if type(pets[i][k]) != all_headers[k] and all_headers[k] != any:
                if type(pets[i][k]) not in [str, int]:
                    return f'Wrong type of pets[{i}][{k}] element - {pets[i]}'
                elif all_headers[k] == int:
                    if not pets[i][k].replace('.', '').replace(',', '').replace(' ', '').isdigit():
                        return f'Wrong type of pets[{i}][{k}] element - {pets[i]}'
                elif all_headers[k] == 'uuid':
                    for s in pets[i][k]:
                        if s not in '0123456789abcdef-':
                            return f'Wrong type of pets[{i}][{k}]: {pets[i]}'
                elif all_headers[k] == 'datetime':
                    try:
                        _ = parse(pets[i][k], fuzzy=False)
                    except ValueError:
                        try:
                            _ = float(pets[i][k])
                        except ValueError:
                            return f'Type of pets[{i}][{k}] is not timestamp: {pets[i][k]}'

        for k in required_headers.keys():
            if k not in pets[i].keys():
                return f'Missing key \'{k}\' in [{i}] element: {pets[i]}'
    return ''


def check_pet(resp: dict, name: str = '', animal_type: str = '', age = '', pet_photo = '*'):
    if resp['name'] != str(name):
        return f'Wrong name: \'{name}\' expected but got {resp["name"]}'
    if resp['animal_type'] != str(animal_type):
        return f'Wrong animal_type: \'{animal_type}\' expected but got {resp["animal_type"]}'
    if resp['age'] != str(age):
        return f'Wrong age: \'{age}\' expected but got {resp["age"]}'
    if pet_photo != '*' and 'pet_photo' in resp.keys() and resp['pet_photo'] != pet_photo:
        f = resp['pet_photo'][:resp['pet_photo'].index(',')] if ',' in resp['pet_photo'] else resp['pet_photo'][:20]
        if '*' in pet_photo and pet_photo.index('*') < len(f):
            f, pet_photo = f[:pet_photo.index('*')], pet_photo[:pet_photo.index('*')]
        if pet_photo not in f:
            return f'Wrong pet_photo: \'{pet_photo}\' expected but got \'{f}\''
    if round(float(resp['created_at']), -1) != round(float(datetime.now().timestamp()), -1):
        return f'Wrong created_at: \'{datetime.now().timestamp()}\' expected but got\'' \
               f'{float(resp["created_at"])}\''
    return ''


# print(get_key())
print(get_key())