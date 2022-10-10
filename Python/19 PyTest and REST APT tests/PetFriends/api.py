import os.path

import settings
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from datetime import datetime


class PetFriends:
    """
    API Help: https://petfriends.skillfactory.ru/apidocs/

    Class contains methods to use that API
    """
    def __init__(self):
        self.base_url = 'https://petfriends.skillfactory.ru/'
        self.headers = {'Accept': 'application/json'}
        self.my_pets = []
        self.sess = requests.Session()
        try:
            if self.get_api_key():  # get api_key and save it in self.headers
                status_code, data = self.get_pets()
                if status_code == 200 and type(data) == list:
                    self.my_pets = data
                elif status_code == 200 and type(data) == dict:
                    self.my_pets.append(data)
                else:
                    print('error getting pets:', status_code, data)
            else:
                print(0, 'Unknown login error in __init__')
        except PetFriendsException as e:
            print(e)

    def request(self, method: str, path: str, headers: str = '', data = None, params = None) -> tuple:
        """
        Send a request with authentication data (if exists) and returns the resuts
        :param method: Required. request's method. Can be either 'GET', 'POST', 'PUT' or 'DELETE'
        :param path: Required. path in addition to base_url to send request to
        :param headers: Optional. custom headers (dict) or just 'Content-Type' field in headers (str).
        :param data: Optional. request's body. Use MultipartEncoder() in case you need to send formData.
        :param params: Optional. params to add to requests - usually GET's params added to url: ?param1=value1&param2=value2&...
        :return: Response status code and response data
        """
        # allowed methods in REST API:
        methods = ['GET', 'POST', 'PUT', 'DELETE']
        # add base URL
        url = self.base_url + path if type(path) == str else ''
        if method.upper() not in methods:
            return (0, f'Unclear request method: {method}')
        if headers and type(headers) == str:
            headers = {'Content-Type': headers} | self.headers
        elif type(headers) == dict:
            headers = headers | self.headers
        else:
            headers = self.headers
        if type(data) == MultipartEncoder:
            headers = {'Content-Type': data.content_type} | headers
        if not data:
            data = None
        if not params or type(params) != dict:
            params = None
        # print(f'DEBUG: Request: {method} to {url}:\nparams={params}\nheaders={headers}\ndata={data}')
        resp = self.sess.request(method, url, params=params, data=data, headers=headers)
        if resp.headers['content-type'] == 'application/json':
            return resp.status_code, resp.json()
        else:
            return resp.status_code, resp.text

    def open_file(self, pet_photo: str):
        if not pet_photo:
            raise PetFriendsException('Create pet failed: empty photo URL')

            # determine photo file MIME type
        if '/' in pet_photo.replace('\\', '/'):
            file_name = pet_photo[pet_photo.replace('\\', '/').rindex('/')+1:]
        else:
            file_name = pet_photo
        ext = file_name[file_name.rindex('.') + 1:]
        if ext in ['jpg', 'jpeg']:
            photo_type = 'image/jpeg'
        elif ext == '.png':
            photo_type = 'image/x-png'
        elif ext == '.gif':
            photo_type = 'image/gif'
        else:
            raise PetFriendsException('photo file extension not supported:', pet_photo)

        # ready to send a request
        try:
            f = open(pet_photo, 'rb')
        except FileNotFoundError:
            try:
                f = open(os.path.join(os.path.dirname(__file__), pet_photo), 'rb')
            except FileNotFoundError as e:
                raise PetFriendsException('create pet error: photo file not found: ' + pet_photo)
        return file_name, f, photo_type

    @staticmethod
    def print_dict(data: dict) -> str:
        if type(data) == dict:
            for k in data.keys():
                if type(data[k]) == str and len(data[k]) > 127:
                    data[k] = data[k][:124] + '...'
                elif type(data[k]) == list:
                    data[k] = PetFriends.print_list(data[k])
        return str(data)

    @staticmethod
    def print_list(data: list) -> str:
        if type(data) == list:
            for i in range(len(data)):
                if type(data[i]) == dict:
                    data[i] = PetFriends.print_dict(data[i])
                elif type(data[i]) == str and len(data[i]) > 127:
                    data[i] = data[i][:124] + '...'
        return str(data)

    @staticmethod
    def print_resp(request_type: str, status_code: int, data: any) -> None:
        if status_code == 0:
            print(request_type, 'error:', data)
        else:
            if type(data) == dict:
                data = PetFriends.print_dict(data)
            elif type(data) == list:
                data = PetFriends.print_list(data)
            elif type(data) == str and len(data) > 127:
                data = data[:124] + '...'
        print(request_type, 'status code:', status_code)
        print(f'result = {data}')

    def get_api_key(self, force=False):
        """
        gets valid_email and valid_password from settings module and authorizes user on server
        :param force: forces request to send a request instead of getting stored key
        :return:
        """
        if not force and 'auth_key' in self.headers: # Cached credinals
            return 200, self.headers['auth_key']
        try:
            headers = {'email': settings.valid_email, 'password': settings.valid_password}
            if not headers['email'] or not headers['password']:
                raise ValueError('Email or password may not be empty')
            if '@' not in headers['email'] or '.' not in headers['email'] or \
                headers['email'].index('@') > headers['email'].rindex('.') - 2:
                raise ValueError('Incorrect email')
        except ValueError as e:
            return (0, str(e))

        resp = self.request('GET', 'api/key', headers)
        if resp[0] == 200:
            if type(resp[1]) == dict and 'key' in resp[1].keys():
                self.headers['auth_key'] = resp[1]['key']
                print('logged in as', headers['email'])
                return resp[0], resp[1]['key']
            else:
                return (0, 'logon error: \'key\' is not found in response keys:\n' + str(resp[1]))
        else:
            return (0, f'logon error: wrong response {resp[0]}: \'{resp[1]}\'')

    def get_pets(self, pet_id=None) -> list:
        """
        get user's pets from server
        :param pet_id: gets specific pet's data, if set. Otherwise gets all pets
        :return: list object with found pets
        """
        if 'auth_key' not in self.headers:
            return 0, 'Get pets error: need a new key'
        resp = self.request('GET', 'api/pets', params={'filter': 'my_pets'})
        if resp[0] == 403:
            del self.headers['auth_key']
            return 0, 'Get pets error: logon expired. Get a new api_key'
            # self.get_api_key()
        elif resp[0] != 200:
            return 0, f'Get pets error {resp[0]}: {rest[1]}'
        else:
            if type(resp[1]) == dict and 'pets' in resp[1].keys() and type(resp[1]['pets']) == list:
                self.my_pets = resp[1]['pets']
                if pet_id:
                    pets = list(p for p in resp[1]['pets'] if type(p) == dict and 'id' in p.keys() and p['id'] == pet_id)
                    return status_code, pets
                else:
                    return resp[0], resp[1]['pets']
            else:
                return 0, 'Get pets: Unsupported json response type:\n' + str(resp[1])

    def create_pet(self, name: str, animal_type: str, age: int, pet_photo: str) -> list:
        """
        creates a new pet
        :param name: pet's name
        :param animal_type: animal type (for ex. dog, cat, etc.)
        :param age: pet's age in years
        :param pet_photo: pet's photo file name
        :return: returns new pet's data
        """
        if 'auth_key' not in self.headers:
            return 0, 'Create pet failed: user not authorized'
        elif not name:
            return 0, 'Create pet failed: name is empty'
        elif type(age) == int and (age < 0 or age > 20) or type(age) == str and (int(age) < 0 or int(age) > 30):
            return 0, 'Create pet failed: wrong age'
        elif not animal_type:
            return 0, 'Create pet failed: animal_type is empty'

        # check pet_photo variable and get: [0] real file_name, [1] binary file, [2] MIME type
        pet_file = self.open_file(pet_photo)
        data = MultipartEncoder(
            fields={
                'name': name,
                'animal_type': animal_type,
                'age': str(age),
                'pet_photo': (pet_file[0], pet_file[1], pet_file[2])
            }
        )
        resp = self.request('POST', 'api/pets', data=data)
        if resp[0] == 200:
            if type(resp[1]) == list:
                self.my_pets.append(resp[1])
                return [p['id'] for p in resp[1]]

            if type(resp[1]) == dict:
                if 'id' in resp[1].keys() and 'created_at in resp[1].keys()':
                    self.my_pets.append(resp[1])
                    return [resp[1]]
            else:
                return 0, 'Unsupported json response type', resp[1]
        elif resp[0] == 403:
            del self.headers['auth_key']
            return 0, 'create pet error: auth_key expired: ' + resp[1]
        elif resp[0] != 200:
            return 0, f'Error create pet: {resp[0]}: {resp[1]}'
        else: # status code = 200 but content-type is not 'application/json'
            return 0, 'wrong response format:', resp[1]

    def update_pet(self, pet_id, name = None, animal_type = None, age = None):
        """
        Updates existing pet. At least, one of parameters (name, animal_type, or age) should be set
        :param pet_id: existing pet_id, required
        :param name: new name
        :param animal_type: new animal_type
        :param age: new age
        :return: returns updated pet's data
        """
        if 'auth_key' not in self.headers:
            return (0, 'Update pet error: unauthorized. Missing auth_key')
        if not self.my_pets or pet_id not in [p['id'] for p in self.my_pets]: # check if pet exists
            return (0, 'Update pet error: pet not found. Pet_id = ' + str(pet_id))
        if not name and not animal_type and not age: # check if at least one parameter is given
            return (0, 'Update pet error: nothing to update. Missing parameters')
        pet_index = [p['id'] for p in self.my_pets].index(pet_id)
        fields = {
            'name': name if name else self.my_pets[pet_index]['name'],
            'animal_type': animal_type if animal_type else self.my_pets[pet_index]['animal_type'],
            'age': str(age) if age else self.my_pets[pet_index]['age']
        } # prepare fields for request's formData
        data = MultipartEncoder(fields=fields)
        # print(f'\nold pet\'s data:\n{self.my_pets[pet_index]}\nreq = {req}')
        resp = self.request('PUT', 'api/pets/' + str(pet_id), data=data)

        if resp[0] == 200 and type(resp[1]) in [dict, list]:
            pet_index = [p['id'] for p in self.my_pets].index(pet_id)
            self.my_pets[pet_index] = resp[1]
            ex_text = 'Update pet error: wrong received data:'
            if name and resp[1]['name'] != name:
                ex_text += f'\n - wrong name: \'{name}\' --> \'{resp[1]["name"]}\''
            if animal_type and resp[1]['animal_type'] != animal_type:
                ex_text += f'\n - wrong animal type: \'{animal_type}\' --> \'{resp[1]["animal_type"]}\''
            if age and resp[1]['age'] != str(age):
                ex_text += f'\n - wrong age: {age} --> {resp[1]["age"]}'
            if pet_id != resp[1]['id']:
                ex_text += f'\n - wrong ID: {pet_id} --> {resp[1]["id"]}'
            if len(ex_text) > 40:
                return (0, ex_text)
            return resp
        elif resp.status_code == 403:
            del self.headers['auth_key']
            return resp
        else:
            return (0, 'Update pet error ' + str(resp[0]) + ': ' + str(resp[1]))

    def delete_pet(self, pet_id=None) -> None:
        """
        deletes pet from system
        :param pet_id: pet_id to delete
        :return:
        """
        if not pet_id and len(self.my_pets) > 0:
            print(f'my_pets[0] = ({type(self.my_pets[0])}) {self.my_pets[0]}')
            pet_id = self.my_pets[0]['id']
        elif not pet_id:
            return (0, 'Pet deletion failed: cannot find pet_id to delete. '
                                      'Probably pet\'s already deleted from the shop')
        elif pet_id and pet_id not in self.my_pets:
            print(f'WARNING: cannot find pet with ID: {pet_id}. Request will be sent')

        resp = self.request('DELETE', 'api/pets/' + str(pet_id))
        if resp[0] == 200:
            print(f'pet (id={pet_id}) deleted successfully')
            print(resp[1])
            # find pet and delete it
            self.my_pets.pop(list(map(lambda x: x['id'], self.my_pets)).index(pet_id))
            return resp
        else:
            return (0, f'Pet deletion failed: wrong reply from server: {resp[0]}: {resp[1]}')

    def create_pet_simple(self, name: str, animal_type: str, age: str):
        """
        Creates a new pet without photo
        :param name: pet's name
        :param animal_type: pet's type (dog, cat, etc.)
        :param age: pet's age
        :return: response's status_code and data
        """
        if not name or not animal_type or not age:
            return (0, f'values may not be empty:\n - name: {name}, animal_type: {animal_type}, age: {age}')
        data = MultipartEncoder(
            fields={
                'name': name,
                'animal_type': animal_type,
                'age': str(age)
            }
        )
        resp = self.request('POST', 'api/create_pet_simple', data=data)
        if resp[0] == 200 and type(resp[1]) == dict and 'id' in resp[1].keys():
            self.my_pets.append(resp[1])
        return resp

    def add_photo(self, pet_id: str, pet_photo: str):
        """
        Adds / changes photo of pet
        :param pet_id: pet_id to add photo to
        :param pet_photo: photo file name
        :return: response's status_code and data
        """
        f = self.open_file(pet_photo)
        data = MultipartEncoder(fields={'pet_photo': f})
        return self.request('POST', 'api/pets/set_photo/' + str(pet_id), data=data)

    def print_pets(self, pet=None) -> str:
        """
        Creates a string with pet's data
        :param pet: specific pets to print. If empty, method prints all pets' data
        :return: formatted string with pet's data.
        """
        pets = ''
        if pet and type(pet) == list:
            for p in pet:
                if pets:
                    pets += '\n'
                pets = self.print_pets(p)
        elif pet and type(pet) == dict:
            pets = '{'
            for k in pet.items():
                if k[0] in ['id', 'age', 'animal_type', 'name']:
                    pets += '\n    \'' + k[0] + '\': \'' + k[1] + '\''
                elif k[0] == 'created_at':
                    pets += '\n    \'' + k[0] + '\': \'' + str(datetime.fromtimestamp(float(k[1]))) + '\''
                else:
                    pets += '\n    \'' + k[0] + '\': \'' + (k[1] if len(k[1]) < 128 else k[1][:125] + '...') + '\''
            pets += '\n}' if len(pets) > 3 else '}'
        elif len(self.my_pets) > 0:
            for p in self.my_pets:
                if pets:
                    pets += '\n'
                if p and type(p) == dict:
                    pets += '{'
                    for k in p.items():
                        if k[0] in ['id', 'age', 'animal_type', 'name']:
                            pets += '\n    \'' + k[0] + '\': \'' + k[1] + '\''
                        elif k[0] == 'created_at':
                            pets += '\n    \'' + k[0] + '\': \'' + str(datetime.fromtimestamp(float(k[1]))) + '\''
                        else:
                            pets += '\n    \'' + k[0] + '\': \'' + (k[1] if len(k[1]) < 128 else k[1][:125]+'...') + '\''
                    pets += '\n}'
        return pets


# simple script to get through basic requests
pet_friends = PetFriends()
if pet_friends.my_pets:
    print('There are already pets:', pet_friends.print_pets(), sep='\n')
else:
    print('There are no pets yet.')
print('\nAdded pet:\n', pet_friends.print_pets(pet_friends.create_pet('Кусака', 'собака', 3, 'images/pet_photo.jpg')))
PetFriends.print_resp('\ncreate pet simple', *pet_friends.create_pet_simple('Бобик', 'собака', 2))
PetFriends.print_resp('\nadded pet photo', *pet_friends.add_photo(pet_friends.my_pets[0]['id'],'images/pet_photo.jpg'))
PetFriends.print_resp('\npet updated', *pet_friends.update_pet(pet_friends.my_pets[0]['id'],name='Весельчак'))
status_code, pets = pet_friends.get_pets()
pet_friends.print_resp('\nget pets', status_code, list(pets))
while pet_friends.my_pets:
    PetFriends.print_resp('\ndelete_pet', *pet_friends.delete_pet())
