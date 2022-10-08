import os.path
import requests
import json
from datetime import date, datetime
from requests_toolbelt.multipart.encoder import MultipartEncoder


class PetError(Exception):
    """
    internal exception that is raised in common use cases
    """
    pass


class PetStore:
    def __init__(self):
        self.base_url = 'https://petstore.swagger.io/v2/'
        self.base_headers = {'accept': 'application/json'}


    @staticmethod
    def check_user_array(array: list) -> tuple:
        """
        Internal method. Checks if user data is valid.
        :param array: array with user data
        :return: bool value that indicates the user data is valid. The 2nd value is an error message in case of invalid data
        """
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
        Internal method. Checks if file exists and determines its MIME type
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
        """
        Internal method. Gets an object and represents UTC datatime from it.
        If object is invalid, returns datatime in a 7 days from now
        :param date_obj: datetime object
        :return: datetime object
        """
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
        """
        Internal method. Sends a request and returns its result in fromat (status_code, body)
        :param method: method that should be used ['POST', 'GET', 'PUT', 'DELETE']
        :param url: path that should be added to base URL
        :param content_type: (optional) Content-Type header's value
        :param data: request's data (body)
        :param params: parameters that should be added to URL like, ?key1=value1&key2=value2, etc.
        :return: ttuple with status_code and response's body
        """
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
        """
        Sends user/createWithArray request
        :param array: array with new users' data
        :return: tuple with status_code and response's body
        """
        f = self.check_user_array(array)
        if not f[0]:
            raise PetError(f'Create users_array failed: {f[1]}')
        return self.request('POST', 'user/createWithArray', 'application/json', json.dumps(array, ensure_ascii=False))

    def user_create_list(self, array: list):
        """
        Sends user/createWithList request
        :param array: array with users' data
        :return: tuple with status_code and response's body
        """
        f = self.check_user_array(array)
        if not f[0]:
            raise PetError(f'Create users with list failed: {f[1]}')
        return self.request('POST', 'user/createWithList', 'application/json', json.dumps(array, ensure_ascii=False))

    def user_get(self, username: str):
        """
        Searches user by username
        :param username: str with username
        :return: tuple with status_code and response's body
        """
        if not username or type(username) != str:
            raise PetError('Parameter \'username\' must be non-empty string')
        return self.request('GET', 'user/' + username)

    def user_update(self, username: str, new_username: str = '', firstname: str = '', lastname: str = '',
                    email: str = '', password: str = '', phone: str = '') -> tuple:
        """
        Sends user update request.
        :param username: Required. Username that will be changed
        :param new_username: Optional. new username that replaces old username. If empty, data is not changed
        :param firstname: Optional. user's first name. if empty, data is not changed
        :param lastname: Optional. user's last name. if empty, data is not changed
        :param email: Optional. user's email address. if empty, data is not changed
        :param password: Optional. user's password. if empty, data is not changed
        :param phone: Optional. user's phone number. if empty, data is not changed
        :return: tuple with status_code and response's body
        """
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

    def user_delete(self, username: str):
        """
        Sends request to delete existing user
        :param username: Required. Str object with username
        :return: tuple with status_code and response's body
        """
        return self.request('DELETE', 'user/' + username)

    def user_login(self, username: str, password: str):
        """
        Sends user login request
        :param username: Required. Username
        :param password: Required. user's password
        :return: tuple with status_code and response's body
        """
        return self.request('GET', 'user/login', params={'username': username, 'password': password})

    def user_logout(self):
        """
        Sends logout request. No data required
        :return: tuple with status_code and response's body
        """
        return self.request('GET', 'user/logout')

    def user_create(self, username: str, firstname: str, lastname: str, email: str, password: str, phone: str):
        """
        Sends create user request with new user's data
        :param username: Required. username
        :param firstname: Required. first name
        :param lastname: Required. last name
        :param email: Required. user's email
        :param password: Required. user's password
        :param phone: Required. user's phone
        :return: tuple with status_code and response's body
        """
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
        """
        Sends upload image requests for existing pet
        :param pet_id: pet_id
        :param file_name: file name with new image. Must be either jpg, png or gif file type
        :return: tuple with status_code and response's body
        """
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
        """
        Sends pet add request with new pet's data
        :param name: Required. Pet's name
        :param category: Optional. dict object with 'id' and 'name' of category
        :param photo_urls: Optional. list with photo URLs
        :param tags: Optional. Pet's tags
        :param status: Optional. Status of new pet
        :return: tuple with status_code and response's body
        """
        pet = {'id': 0, 'category': category, 'name': name, 'photoUrls': photo_urls, 'tags': tags, 'status': status}
        return self.request('POST', 'pet', 'application/json', json.dumps(pet, ensure_ascii=False).encode('utf-8'))

    def pet_update(self,pet_id: int, name: str, category: dict = {'id': 0, 'name': 'string'},
                   photo_urls: list = ['string'], tags: list = [{'id': 0, 'name': 'string'}], status='available'):
        """
        Sends pet update request with new pet's data
        :param pet_id: pet_id of existing pet that should be updated
        :param name: new pet's name
        :param category: Optional. new pet's category
        :param photo_urls: Optional. new photo URLs
        :param tags: Optional. new tags
        :param status: Optional. new status
        :return: tuple with status_code and response's body
        """
        pet = {'id': pet_id, 'category': category, 'name': name, 'photoUrls': photo_urls, 'tags': tags, 'status': status}
        return self.request('POST', 'pet', 'application/json', json.dumps(pet, ensure_ascii=False).encode('utf-8'))

    def pet_find_by_status(self, status='available'):
        """
        Sends pet find by status request
        :param status: status to be searched. Must be one of following: ['available', 'pending', 'sold']
        :return: tuple with status_code and response's body
        """
        statuses = ['available', 'pending', 'sold']
        if status not in statuses:
            status = statuses[0]
        return self.request('GET', 'pet/' + status)

    def pet_find_by_id(self, pet_id: int):
        """
        Sends pet find by id request
        :param pet_id: pet_id to be searched
        :return: tuple with status_code and response's body
        """
        return(self.request('GET', 'pet/' + str(pet_id)))

    def pet_update_by_id(self, pet_id: int, name: str = '', status='available'):
        """
        Sends pet update by id request
        :param pet_id: pet_id
        :param name: new pet's name
        :param status: new status
        :return: tuple with status_code and response's body
        """
        if type(name) is not str:
            name = ''
        if type(status) is not str:
            status = 'available'
        body = {'name': name, 'status': status}
        return self.request('POST', 'pet/' + str(pet_id), 'application/x-www-form-urlencoded', body)

    def pet_delete(self, pet_id: int, api_key: str = ''):
        """
        Sends pet delete request. WARNING. User must be authorized with vaild api_key
        :param pet_id: pet_id that should be deleted
        :param api_key: authorization key
        :return: tuple with status_code and response's body
        """
        if not api_key:
            api_key = 'special-key'
        body = {'pet_id': pet_id}
        return self.request('DELETE', 'pet/' + str(pet_id), 'application/x-www-form-urlencoded', body)

    def store_create_order(self, pet_id: int, quantity: int = 0, ship_date: datetime = None, status: str = 'placed',
                           completed: bool = False):
        """
        Sends new order request
        :param pet_id: Required.
        :param quantity: Optional.
        :param ship_date: Optional.
        :param status: Optional.
        :param completed: Optional.
        :return: tuple with status_code and response's body
        """
        completed = True if not quantity or not pet_id else completed
        order = {'id': 0, 'petId': pet_id, 'quantity': quantity, 'shipDate': self.parse_datetime(ship_date),
                 'status': status, 'complete': completed}
        print(order)
        return self.request('POST', 'store/order', 'application/json', json.dumps(order, ensure_ascii=False))

    def store_find_order(self, order_id: int):
        """
        Sends find order by id request
        :param order_id:
        :return: tuple with status_code and response's body
        """
        return self.request('GET', 'store/order/' + str(order_id))

    def store_delete_order(self, order_id: int):
        """
        Sends delete order request
        :param order_id:
        :return: tuple with status_code and response's body
        """
        return self.request('DELETE', 'store/order/' + str(order_id))

    def store_inventory(self):
        """
        Sends store inventory request
        :return: tuple with status_code and response's body
        """
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
