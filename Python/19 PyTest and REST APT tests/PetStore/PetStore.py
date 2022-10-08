import os.path
import requests
import json
from datetime import date, datetime
from requests_toolbelt.multipart.encoder import MultipartEncoder


class PetError(Exception):
    pass


class PetStore:
    def __init__(self):
        self.base_url = 'https://petstore.swagger.io/v2/'
        self.base_headers = {'accept': 'application/json'}

        # add_req('get_user', 'GET', base_url + 'user/', base_headers)

    @staticmethod
    def check_user_array(array: list) -> tuple:
        correct_keys = {'id': int, 'username': str, 'firstName': str, 'lastName': str,
                        'email': str, 'password': str, 'phone': str, 'userStatus': int}
        f = True # assume that array is correct
        s = 'user_array check failed: ' # Error message if check failes
        if not array or type(array) != list: # check that array is a list and is not empty
            s += 'array is empty or not a list'
            f = False
        if f:
            for i in array: # check each array item
                if f and type(i) != dict: # assume it is a dict
                    s += f'array item {i} is not a dict'
                    f = False
                else:
                    ii = {}
                    for j in i.items(): # make also sure that array has ONLY keys that are correct
                        ii[j[0]] = type(j[1])
                        if f and (j[0], type(j[1])) not in correct_keys.items():
                            s += f'element {j} is incorrect'
                            f = False
                    for j in correct_keys.items(): # make sure that array have all correct keys
                        # make sure the key is valid and type of its value is also valid
                        if f and j not in ii.items():
                            s += f'element {j} missing in {ii}'
                            f = False
        if f:
            s = ''
        return f, s

    def check_file(self, file_name: str) -> tuple:
        """
        checks if file exists and determines its MIME type
        :param file_name: file_name
        :return: mime_type, full name and file_name (without directories).
        """
        # determine real file_name and check if file exists
        real_name = os.path.join(os.path.dirname(__file__), file_name)
        if not os.path.isfile(real_name):
            real_name = os.path.join(file_name)
            if not os.path.isfile(real_name):
                return '', '', ''
        # determine MIME type
        if file_name.index('.') < 0:
            return '', '', ''
        real_path = real_name[:real_name.replace('\\', '/').rfind('/')]
        file_name = real_name[len(real_path)+1:]
        file_ext = file_name[len(file_name)-file_name[::-1].index('.'):].lower()
        if file_ext in ['jpg', 'jpeg']:
            mime_type = 'image/jpeg'
        elif file_ext == 'png':
            mime_type = 'image/x-png'
        elif file_ext == 'gif':
            mime_type = 'image/gif'
        else:
            mime_type = ''
        return mime_type, real_name, file_name

    def parse_datetime(self, date_obj: datetime) -> datetime:
        if type(date_obj) == str:
            try:
                date_obj = datetime.fromisoformat(date_obj)
            except ValueError:
                date_obj = None
        if date_obj not in (date, datetime, int, float):
            date_obj = datetime.now()
        elif type(date_obj) in (int, float):
            date_obj = datetime.utcfromtimestamp(date_obj)
        elif type(date_obj) == date:
            date_obj = datetime.combine(date_obj, datetime.min.time())
        return datetime.isoformat(date_obj)

    def request(self, method: str, url: str, content_type: str = None, data = None, params = None):
        req = {'method': method, 'url': self.base_url + url, 'headers': self.base_headers}
        if content_type is not None:
            req['headers']['Content-Type'] = content_type
        if data:
            req['data'] = data
        if params:
            req['params'] = params
        resp = requests.request(**req)
        if 'Content-Type' in resp.headers and resp.headers['Content-Type'] == 'application/json':
            return resp.status_code, json.dumps(resp.json(), ensure_ascii=False, indent=2)
        else:
            return resp.status_code, resp.text

    def users_create_array(self, array: list):
        f = self.check_user_array(array)
        if not f[0]:
            raise PetError(f'Create users_array failed: {f[1]}')
        return self.request('POST', 'user/createWithArray', 'application/json', json.dumps(array, ensure_ascii=False))

    def user_create_list(self, array: list):
        f = self.check_user_array(array)
        if not f[0]:
            raise PetError(f'Create users with list failed: {f[1]}')
        return self.request('POST', 'user/createWithList', 'application/json', json.dumps(array, ensure_ascii=False))

    def user_get(self, username: str):
        if not username or type(username) != str:
            raise PetError('Parameter \'username\' must be non-empty string')
        return self.request('GET', 'user/' + username)

    def user_update(self, username: str, new_username: str = '', firstname: str = '', lastname: str = '',
                    email: str = '', password: str = '', phone: str = '') -> tuple:
        # check that username is given correctly
        if not username or type(username) != str:
            raise PetError('Parameter \'username\' must be non-empty string')
        user = self.get_user(username)
        if user[0] == 200 and type(user[1]) == dict:
            if type(new_username) == str and new_username:
                user[1]['username'] = new_username
            if type(firstname) == str and firstname:
                user[1]['firstName'] = firstname
            if type(lastname) and lastname:
                user[1]['lastName'] = lastname
            if type(email) == str and 0 < email.index('@') < email.index('.', email.index('@')) < len(email):
                user[1]['email'] = email
            if type(password) == str and password:
                user[1]['password'] = password
            if type(phone) in (str, int) and phone:
                user[1]['phone'] = str(phone)
        else:
            user = (user[0], {
                'id': 0,
                'username': new_username if new_username else username,
                'firstName': firstname,
                'lastName': lastname,
                'email': email,
                'password': password,
                'phone': str(phone),
                'userStatus': 0
            })
        return self.request('PUT', 'user/' + username, 'application/json', json.dumps(user[1], ensure_ascii=False))

    def user_delete(self, username):
        return self.request('DELETE', 'user/' + username)

    def user_login(self, username: str, password: str):
        return self.request('GET', 'user/login', params={'username': username, 'password': password})

    def user_logout(self):
        return self.request('GET', 'user/logout')

    def user_create(self, username: str, firstname: str, lastname: str, email: str, password: str, phone: str):
        body = json.dumps({
            'id': 0,
            'username': username if type(username) == str else '',
            'firstName': firstname if type(firstname) == str else '',
            'lastName': lastname if type(lastname) == str else '',
            'email': email if type(email) == str else '',
            'password': password if type(password) == str else '',
            'phone': phone if type(phone) == str else (str(phone) if phone else ''),
            'userstatus': 0
        })
        return self.resp_results('POST', 'user', 'application/json', body)

    def pet_upload_image(self, pet_id: str, file_name: str):
        mime_type, file_name, real_name = self.check_file(file_name)
        # check if file exists and open file
        if not file_name:
            raise PetError(f'cannot find file: {file_name}')
        if not mime_type:
            raise PetError(f'cannot determine file MIME type:')
        data = MultipartEncoder({'file': (real_name, open(file_name, 'rb'), mime_type)})
        return self.request('POST', f'pet/{pet_id}/uploadImage', data.content_type, data)

    def pet_add(self, name: str, category: dict = {'id': 0, 'name': 'string'}, photo_urls: list = ['string'],
                tags: list = [{'id': 0, 'name': 'string'}], status='available'):
        pet = {'id': 0, 'category': category, 'name': name, 'photoUrls': photo_urls, 'tags': tags, 'status': status}
        return self.request('POST', 'pet', 'application/json', json.dumps(pet, ensure_ascii=False).encode('utf-8'))

    def pet_update(self,pet_id: int, name: str, category: dict = {'id': 0, 'name': 'string'},
                   photo_urls: list = ['string'], tags: list = [{'id': 0, 'name': 'string'}], status='available'):
        pet = {'id': pet_id, 'category': category, 'name': name, 'photoUrls': photo_urls, 'tags': tags, 'status': status}
        return self.request('POST', 'pet', 'application/json', json.dumps(pet, ensure_ascii=False).encode('utf-8'))

    def pet_find_by_status(self, status='available'):
        statuses = ['available', 'pending', 'sold']
        if status not in statuses:
            status = statuses[0]
        return self.request('GET', 'pet/' + status)

    def pet_find_by_id(self, pet_id: int):
        return(self.request('GET', 'pet/' + str(pet_id)))

    def pet_update_by_id(self, pet_id: int, name: str = '', status='available'):
        if type(name) is not str:
            name = ''
        if type(status) is not str:
            status = 'available'
        body = {'name': name, 'status': status}
        return self.request('POST', 'pet/' + str(pet_id), 'application/x-www-form-urlencoded', body)

    def pet_delete(self, pet_id: int, api_key: str = ''):
        if not api_key:
            api_key = 'special-key'
        body = {'pet_id': pet_id}
        return self.request('DELETE', 'pet/' + str(pet_id), 'application/x-www-form-urlencoded', body)

    def store_create_order(self, pet_id: int, quantity: int = 0, ship_date: datetime = None, status: str = 'placed',
                           completed: bool = False):
        completed = True if not quantity or not pet_id else completed
        order = {'id': 0, 'petId': pet_id, 'quantity': quantity, 'shipDate': self.parse_datetime(ship_date),
                 'status': status, 'complete': completed}
        print(order)
        return self.request('POST', 'store/order', 'application/json', json.dumps(order, ensure_ascii=False))

    def store_find_order(self, order_id: int):
        return self.request('GET', 'store/order/' + str(order_id))

    def store_delete_order(self, order_id: int):
        return self.request('DELETE', 'store/order/' + str(order_id))

    def store_inventory(self):
        return self.request('GET', 'store/inventory')


pet_store = PetStore()
### PETS BLOCK ###
# print(*pet_store.pet_add("Kuzya"))
# print(*pet_store.pet_upload_image('9223372036854251348', 'images/pet_photo.jpg'))
# print(*pet_store.pet_update(9223372036854251348, 'Polkan'))
# print(*pet_store.pet_find_by_status())
# print(*pet_store.pet_find_by_id(9223372036854018119))
# print(*pet_store.pet_update_by_id(9223372036854018119, name='Козьма', status='sold'))
# print(*pet_store.pet_delete(pet_id=9223372036854018119))

### STORE BLOCK ###
# print(*pet_store.store_create_order(0))
# print(*pet_store.store_find_order(56764568663))
# print(*pet_store.store_delete_order(56764568663))
# print(*pet_store.store_inventory())

### USERS BLOCK ###
# print(*pet_store.user_create('Ouser_oleg', 'Oleg', 'Tester', 'user@mail.com', '$up3rUs3r', 749512345))
# print(*pet_store.user_get('Ouser_oleg'))
# print(*pet_store.user_update('Ouser_oleg', new_username='oleza034_test', password='Z@kazn0v'))
# print(*pet_store.user_login('oleza034_test', 'Z@kazn0v'))
# print(pet_store.user_logout())
# array1 = [{'id': 0, 'username': 'oleza_test1', 'password': '123456', 'firstName': 'Oleg', 'lastName': 'Z.',
#           'email': 'user4@mail.ru', 'phone': '123456789', 'userStatus': 0},
#          {'id': 0, 'username': 'oleza_test2', 'password': '654321', 'firstName': 'Oleg', 'lastName': 'Z.',
#           'email': 'user5@mail.ru', 'phone': '987654312', 'userStatus': 0}]
# array2 = [{'id': 0, 'username': 'oleza_test3', 'password': '1234e56', 'firstName': 'Oleg', 'lastName': 'Z.',
#           'email': 'userwe3@mail.ru', 'phone': '123456789', 'userStatus': 0},
#          {'id': 0, 'username': 'oleza_test4', 'password': '654321', 'firstName': 'Oleg', 'lastName': 'Z.',
#           'email': 'user5345@mail.ru', 'phone': '987654312', 'userStatus': 0}]
# print(*pet_store.user_create_array(array1))
# print(*pet_store.user_create_list(array2))
# for i in (list(map(lambda x: x['username'], array1 + array2)) + ['oleza034_test']):
#     print(*pet_store.user_delete(i))
