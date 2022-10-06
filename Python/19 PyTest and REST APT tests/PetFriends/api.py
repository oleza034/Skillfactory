import settings
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder


class PetFriendsException(Exception):
    pass


class PetFriends:
    """
    API Help: https://petfriends.skillfactory.ru/apidocs/
    """
    def __init__(self):
        self.base_url = 'https://petfriends.skillfactory.ru/'
        self.requests = {
            'get_api_key': {'url': self.base_url + 'api/key', 'method': 'GET'},
            'get_pets': {'url': self.base_url + 'api/pets', 'method': 'GET', 'params': {'filter': 'my_pets'}},
            'create_pet': {'url': self.base_url + 'api/pets', 'method': 'POST'},
            'delete_pet': {'url': self.base_url + 'api/pets/', 'method': 'DELETE'},
            'update_pet': {'url': self.base_url + 'api/pets/', 'method': 'PUT'}
        }
        self.headers = {'Accept': 'application/json'}
        self.my_pets = []
        self.cookies = {}
        self.sess = requests.Session()
        try:
            if self.get_api_key():  # get api_key and save it in self.headers
                self.my_pets = self.get_pets()
            else:
                raise PetFriendsException('Unknown login error in __init__')
        except PetFriendsException as e:
            print(e)

    def send_request(self, method: str, url: str, headers: dict = {}, data = None, params = None) -> requests.Response:
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
            data = MultipartEncoder(
                fields={
                    'name': name,
                    'animal_type': animal_type,
                    'age': str(age),
                    'pet_photo': (pet_photo, open(pet_photo, 'rb'), photo_type)
                }
            )
        except FileNotFoundError:
            raise PetFriendsException('Cannot find pet\'s photo file: ' + pet_photo)

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
        if 'auth_key' not in self.headers:
            raise PetFriendsException('Update pet error: unauthorized. Missing auth_key')
        if not self.my_pets or pet_id not in [p['id'] for p in self.my_pets]: # check if pet exists
            raise PetFriendsException('Update pet error: pet not found. Pet_id = ' + str(pet_id))
        if not name and not animal_type and not age: # check if at least one parameter is given
            raise PetFriendsException('Update pet error: nothing to update. Missing parameters')
        req = self.requests['update_pet']
        req['url'] += pet_id
        fields = {} # prepare fields for request's formData
        if name:
            fields['name'] = str(name)
        if animal_type:
            fields['animal_type'] = str(animal_type)
        if age:
            fields['age'] = str(age)
        data = MultipartEncoder(fields=fields)
        req['data'] = data
        resp = self.send_request(**req)

        if resp.status_code == 200 and resp.headers['content-type'] == 'application/json':
            j = resp.json()
            pet_index = [p['id'] for p in self.my_pets].index(pet_id)
            self.my_pets[pet_index] = j
            return 200, j
        elif resp.status_code == 403:
            del self.headers['auth_key']
            return 403, resp.text
        else:
            raise PetFriendsException ('Update pet error ' + str(resp.status_code) + ': ' + resp.text)

    def delete_pet(self, pet_id=None):
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


pet_friends = PetFriends()
if pet_friends.my_pets:
    print('There are already pets:', *pet_friends.my_pets, sep='\n')
else:
    print('There are no pets yet.')
print('Added new pet:', pet_friends.create_pet('Кусака', 'собака', 3, 'images/kusaka.jpg'))
pet_friends.update_pet(pet_friends.my_pets[0]['id'],name='Весельчак')
pet_friends.get_pets()
print('updated pet:', pet_friends.my_pets[0])
while pet_friends.my_pets:
    pet_friends.delete_pet()
