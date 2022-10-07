import os.path

import settings
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from datetime import datetime


class PetFriendsException(Exception):
    pass


class PetFriends:
    """
    API Help: https://petfriends.skillfactory.ru/apidocs/

    Class contains methods to use that API
    """
    def __init__(self):
        self.base_url = 'https://petfriends.skillfactory.ru/'
        self.requests = {
            'get_api_key': {'url': self.base_url + 'api/key', 'method': 'GET'},
            'get_pets': {'url': self.base_url + 'api/pets', 'method': 'GET', 'params': {'filter': 'my_pets'}},
            'create_pet': {'url': self.base_url + 'api/pets', 'method': 'POST'},
            'delete_pet': {'url': self.base_url + 'api/pets/', 'method': 'DELETE'},
            'update_pet': {'url': self.base_url + 'api/pets/', 'method': 'PUT'},
            'create_pet_simple': {'url': self.base_url + 'api/create_pet_simple', 'method': 'POST'},
            'set_photo': {'url': self.base_url + 'api/pets/set_photo/', 'method': 'POST'}
        }
        self.headers = {'Accept': 'application/json'}
        self.my_pets = []
        self.sess = requests.Session()
        try:
            if self.get_api_key():  # get api_key and save it in self.headers
                self.my_pets = self.get_pets()
            else:
                raise PetFriendsException('Unknown login error in __init__')
        except PetFriendsException as e:
            print(e)

    def send_request(self, method: str, url: str, headers: dict = {}, data = None, params = None) -> requests.Response:
        """
        Send a request with authentication data (if exists) and returns the resuts
        :param method: request's method. Can be either 'GET', 'POST', 'PUT' or 'DELETE'
        :param url: URL to send request to
        :param headers: request's headers
        :param data: request's body. Use MultipartEncoder() in case you need to send formData.
        :param params: params to add to requests - usually GET's params added to url: ?param1=value1&param2=value2&...
        :return: Response object with results of request
        """
        methods = ['GET', 'POST', 'PUT', 'DELETE']
        if not url:
            raise PetFriendsException('Request URL is empty')
        if method.upper() not in methods:
            raise PetFriendsException('Unclear request method:', method)
        if type(headers) != dict:
            headers = self.headers
        else:
            headers = headers | self.headers
        if type(data) == MultipartEncoder:
            headers = {'content-type': data.content_type} | headers
        if not data:
            data = None
        if not params:
            params = None
        resp = self.sess.request(method, url, params=params, data=data, headers=headers)
        return resp

    def get_api_key(self, force=False):
        """
        gets valid_email and valid_password from settings module and authorizes user on server
        :param force: forces request to send a request instead of getting stored key
        :return:
        """
        if not force and 'auth_key' in self.headers: # Cached credinals
            return 200, self.headers['auth_key']
        req = self.requests['get_api_key']
        req['headers'] = {'email': settings.valid_email, 'password': settings.valid_password}
        resp = self.send_request(**req)
        if resp.status_code == 200 and resp.headers['content-type'] == 'application/json':
            j = resp.json()
            if type(j) == dict and 'key' in j.keys():
                self.headers['auth_key'] = j['key']
                print('logged in as', req['headers']['email'])
                return resp.status_code, j['key']
            else:
                raise PetFriendsException('logon error: \'key\' is not found in response keys:\n' + str(j))
        elif resp.status_code == 200:
            raise PetFriendsException('logon error: wrong content-type: ' + resp.headers['content-type']
                  + (resp.text if len(resp.text) < 255 else resp.text[:253] + '...'))
        else:
            raise PetFriendsException(f'logon error: wrong status {resp.status_code}: \''
                  + f'{(resp.text[:253] + "...") if len(resp.text) > 255 else resp.text}\'')

    def get_pets(self, pet_id=None) -> list:
        """
        get user's pets from server
        :param pet_id: gets specific pet's data, if set. Otherwise gets all pets
        :return: list object with found pets
        """
        if 'auth_key' not in self.headers:
            raise PetFriendsException('Get pets error: need a new key')
        req = self.requests['get_pets']
        resp = self.send_request(**req)
        if resp.status_code == 403:
            del self.headers['auth_key']
            raise PetFriendsException('Get pets error: logon expired. Get a new api_key')
            # self.get_api_key()
        elif resp.status_code != 200:
            raise PetFriendsException(f'Get pets error {resp.status_code}: ' +
                  (resp.text if len(resp.text) < 255 else (resp.text[:253] + '...')))
        elif resp.headers['content-type'] != 'application/json':
            raise PetFriendsException('Get pets: wrong response format:', resp.headers['content-type'] + ', ' +
                  resp.text if len(resp.text) < 255 else resp.text[:253] + '...')
        else:
            j = resp.json()
            if type(j) == dict and 'pets' in j.keys() and type(j['pets']) == list:
                self.my_pets = j['pets']
                if pet_id:
                    pets = [p for p in j['pets'] if type(p) == dict and 'id' in p.keys() and p['id'] == pet_id]
                    return pets
                else:
                    return j['pets']
            else:
                raise PetFriendsException('Get pets: Unsupported json response type:\n' + str(j))

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
            raise PetFriendsException('Create pet failed: user not authorized')
        elif not name:
            raise PetFriendsException('Create pet failed: name is empty')
        elif type(age) == int and (age < 0 or age > 20) or type(age) == str and (int(age) < 0 or int(age) > 20):
            raise PetFriendsException('Create pet failed: wrong age')
        elif not animal_type:
            raise PetFriendsException('Create pet failed: animal_type is empty')
        elif not pet_photo:
            raise PetFriendsException('Create pet failed: empty photo URL')

        # determine photo file MIME type
        if pet_photo[-4:] == '.jpg' or pet_photo[-5:] == '.jpeg':
            photo_type = 'image/jpeg'
        elif pet_photo[-4:] == '.png':
            photo_type = 'image/x-png'
        elif pet_photo[-4:] == '.gif':
            photo_type = 'image/gif'
        else:
            photo_type = ''
        if not photo_type:
            raise PetFriendsException('photo file extension not supported:', pet_photo)

        # ready to send a request
        req = self.requests['create_pet']
        try:
            f = open(pet_photo, 'rb')
        except FileNotFoundError:
            try:
                f = open(os.path.join(os.path.dirname(__file__), pet_photo), 'rb')
            except FileNotFoundError as e:
                raise PetFriendsException('create pet error: photo file not found: ' + pet_photo)
        data = MultipartEncoder(
            fields={
                'name': name,
                'animal_type': animal_type,
                'age': str(age),
                'pet_photo': (pet_photo, f, photo_type)
            }
        )
        req['data'] = data
        resp = self.send_request(**req)
        if resp.status_code == 200 and resp.headers['content-type'] == 'application/json':
            j = resp.json()
            if type(j) == list:
                self.my_pets += j
                return [p['id'] for p in j]

            if type(j) == dict:
                if 'id' in j.keys() and 'created_at in j.keys()':
                    self.my_pets.append(j)
                    return [j]
            else:
                raise PetFriendsException('Unsupported json response type', j)
        elif resp.status_code == 403:
            del self.headers['auth_key']
            raise PetFriendsException('create pet error: auth_key expired: ' + resp.text)
        elif resp.status_code != 200:
            raise PetFriendsException(f'Error create pet: {resp.status_code}: ' +
                  (resp.text if len(resp.text) < 255 else (resp.text[:253] + '...')))
        else: # status code = 200 but content-type is not 'application/json'
            raise PetFriendsException('wrong response format:', resp.headers['content-type'] + ', ' +
                  resp.text if len(resp.text) < 255 else resp.text[:253] + '...')

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
            raise PetFriendsException('Update pet error: unauthorized. Missing auth_key')
        if not self.my_pets or pet_id not in [p['id'] for p in self.my_pets]: # check if pet exists
            raise PetFriendsException('Update pet error: pet not found. Pet_id = ' + str(pet_id))
        if not name and not animal_type and not age: # check if at least one parameter is given
            raise PetFriendsException('Update pet error: nothing to update. Missing parameters')
        req = self.requests['update_pet']
        pet_index = [p['id'] for p in self.my_pets].index(pet_id)
        req['url'] += pet_id
        fields = {
            'name': name if name else self.my_pets[pet_index]['name'],
            'animal_type': animal_type if animal_type else self.my_pets[pet_index]['animal_type'],
            'age': str(age) if age else self.my_pets[pet_index]['age']
        } # prepare fields for request's formData
        data = MultipartEncoder(fields=fields)
        req['data'] = data
        # print(f'\nold pet\'s data:\n{self.my_pets[pet_index]}\nreq = {req}')
        resp = self.send_request(**req)

        if resp.status_code == 200 and resp.headers['content-type'] == 'application/json':
            j = resp.json()
            pet_index = [p['id'] for p in self.my_pets].index(pet_id)
            self.my_pets[pet_index] = j
            ex_text = 'Update pet error: wrong received data:'
            if name and j['name'] != name:
                ex_text += f'\n - wrong name: \'{name}\' --> \'{j["name"]}\''
            if animal_type and j['animal_type'] != animal_type:
                ex_text += f'\n - wrong animal type: \'{animal_type}\' --> \'{j["animal_type"]}\''
            if age and j['age'] != str(age):
                ex_text += f'\n - wrong age: {age} --> {j["age"]}'
            if pet_id != j['id']:
                ex_text += f'\n - wrong ID: {pet_id} --> {j["id"]}'
            if len(ex_text) > 40:
                raise PetFriendsException(ex_text)
            return 200, j
        elif resp.status_code == 403:
            del self.headers['auth_key']
            return 403, resp.text
        else:
            raise PetFriendsException ('Update pet error ' + str(resp.status_code) + ': ' + resp.text)

    def delete_pet(self, pet_id=None) -> None:
        """
        deletes pet from system
        :param pet_id: pet_id to delete
        :return:
        """
        if not pet_id:
            pet_id = self.my_pets.pop()['id']
        else:
            self.my_pets.pop([i['id'] for i in self.my_pets].index(pet_id))
        if pet_id:
            req = self.requests['delete_pet']
            req['url']  += str(pet_id)
            resp = self.send_request(**req)
            if resp.status_code == 200:
                print(f'pet (id={pet_id}) deleted successfully')
                print(resp.text)
            else:
                raise PetFriendsException('Pet deletion failed: wrong reply from server: ' 
                                          f'{resp.status_code}: {resp.text}')
        else:
            raise PetFriendsException('Pet deletion failed: cannot find pet_id to delete. '
                                      'Probably pet\'s already deleted from the shop')

    def create_pet_simple(self, name: str, animal_type: str, age: str):
        """
        Creates a new pet without photo
        :param name: pet's name
        :param animal_type: pet's type (dog, cat, etc.)
        :param age: pet's age
        :return: response's status_code and data
        """
        if not name or not animal_type or not age:
            raise PetFriendsException('create_pet_simple error: values may not be empty:\n'
                                      f' - name: {name}, animal_type: {animal_type}, age: {age}')
        req = self.requests['create_pet_simple']
        data = MultipartEncoder(
            fields={
                'name': name,
                'animal_type': animal_type,
                'age': str(age)
            }
        )
        req['data'] = data
        resp = self.send_request(**req)
        if resp.status_code == 200 and resp.headers['content-type'] == 'application/json':
            return resp.status_code, resp.json()
        else:
            return resp.status_code, resp.text()

    def add_photo(self, pet_id: str, pet_photo: str):
        """
        Adds / changes photo of pet
        :param pet_id: pet_id to add photo to
        :param pet_photo: photo file name
        :return: response's status_code and data
        """
        if not pet_id or pet_id not in [lambda p: p['id'] for p in self.my_pets]:
            raise PetFriendsException(f'cannot update photo: pet {pet_id} is not found')
        try:
            f = open(pet_photo, 'rb')
        except FileNotFoundError:
            try:
                f = open(os.path.join(os.path.dirname(__file__), pet_photo))
            except FileNotFoundError as e:
                raise PetFriendsException('cannot update pet photo: file not found:' + str(e))
        req = self.requests['set_photo']
        req['url'] += pet_id
        req['data'] = MultipartEncoder(fields={'pet_photo': f})
        resp = self.send_request(**req)
        if resp.status_code == 200 and resp.headers['content-type'] == 'application/json':
            return resp.status_code, resp.json()
        else:
            return resp.status_code, resp.text

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
        else:
            for p in self.my_pets:
                if pets:
                    pets += '\n'
                if p and type(p) == dict:
                    pets += '{'
                    for k in pet.items():
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
print('\nAdded new pet:\n', pet_friends.print_pets(pet_friends.create_pet('Кусака', 'собака', 3, 'images/kusaka.jpg')))
pet_friends.update_pet(pet_friends.my_pets[0]['id'],name='Весельчак')
pet_friends.get_pets()
print('\nUpdated pet:\n', pet_friends.print_pets(pet_friends.my_pets[0]))
while pet_friends.my_pets:
    pet_friends.delete_pet()
