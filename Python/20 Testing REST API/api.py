import os.path

import requests
import random
import json
import urllib.parse
from requests_toolbelt import MultipartEncoder
from settings import *

base_url = 'https://petfriends.skillfactory.ru/'
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
    :return:
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
    resp = requests.request(method, url, params=params, data=data, headers=headers)
    try:
        return resp.status_code, resp.json()
    except ValueError:
        return resp.status_code, resp.text


def get_photo(filename: str) -> tuple:
    """
    Tries to open a file and return it as byte stream; also checks for file MIME type
    :param filename: filename, for example, images/pet_photo.jpg
    :return: tuple of: \
            1. file name (excluding path / directory)
            2. file MIME type or empty string and error message if something went wrong \
            3. file as a byte stream
    """
    if type(filename) != str or not filename:
        return '', 'filename is empty'
    extensions = {'.jpg': 'jpeg', '.jpeg': 'jpeg', '.png': 'png', 'gif': 'gif'}
    file_name = filename[filename.replace('\\', '/').rindex('/')+1:] if '/' in filename.replace('\\', '/') else filename
    ext = file_name[file_name.index('.'):] if '.' in file_name else ''
    f_type = extensions[ext] if ext in extensions else ''
    try:
        f = open(filename, 'rb')
    except FileNotFoundError:
        try:
            f = open(os.path.join(os.path.dirname(__file__, filename)))
        except FileNotFoundError as e:
            return 'file_name', '', e
    return file_name, f_type, f


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
    if not string:
        return string
    new_string = ''
    for s in string:
        if ord(s) < 128:
            new_string += s
        else:
            new_string += urllib.parse.quote_plus(s)
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
    resp = request('GET', base_url + '/api/key', headers={'email': email, 'password': pw})
    if resp[0] == 200 and type(resp[1]) == dict and 'key' in resp[1].keys():
        return resp[1]['key']
    else:
        return 'ERROR: ' + resp[1]