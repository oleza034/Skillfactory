import settings
import requests
import datetime
from requests_toolbelt.multipart.encoder import MultipartEncoder


class PetFriendsException(Exception):
    pass


class PetFriends:
    """
    API Help: https://petfriends.skillfactory.ru/apidocs/
    """
    def __init__(self):
        self.base_url = 'https://petfriends.skillfactory.ru/'
        self.paths = {
            'get_api_key': 'api/key',
            'get_pets': 'api/pets',
            'create_pet': 'api/pets',
            'delete_pet': 'api/pets/'
        }
        self.headers = {'Accept': 'application/json'}
        self.my_pets = []
        try:
            self.get_api_key()  # get api_key and save it in self.headers
            self.my_pets = self.get_pets()
        except PetFriendsException as e:
            print(e)

    def get_api_key(self):
        url = self.base_url + self.paths['get_api_key']
        headers = self.headers | {'email': settings.valid_email, 'password': settings.valid_password}
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200 and resp.headers['content-type'] == 'application/json':
            j = resp.json()
            if type(j) == dict and 'key' in j.keys():
                self.headers['auth_key'] = j['key']
                return j['key']
            else:
                raise PetFriendsException('logon error: \'key\' is not found in response keys:\n' + str(j))
        elif resp.status_code == 200:
            raise PetFriendsException('logon error: wrong content-type: ' + resp.headers['content-type']
                  + (resp.text if len(resp.text) < 255 else resp.text[:253] + '...'))
        else:
            raise PetFriendsException(f'logon error: wrong status {resp.status_code}: \''
                  + f'{(resp.text[:253] + "...") if len(resp.text) > 255 else resp.text}\'')

    def get_pets(self, pet_id=None) -> list:
        if 'api_key' not in self.headers:
            raise PetFriendsException('List pets error: need a new key')
        url = self.base_url + self.paths['get_pets']
        params = {'filter': 'my_pets'}
        resp = requests.get(url, params=params, headers=self.headers)
        if resp.status_code == 403:
            raise PetFriendsException('logon expired. Get a new api_key')
            # self.get_api_key()
        elif resp.status_code != 200:
            raise PetFriendsException(f'List pets error {resp.status_code}: ' +
                  (resp.text if len(resp.text) < 255 else (resp.text[:253] + '...')))
        elif resp.headers['content-type'] != 'application/json':
            raise PetFriendsException('List pets: wrong response format:', resp.headers['content-type'] + ', ' +
                  resp.text if len(resp.text) < 255 else resp.text[:253] + '...')
        else:
            j = resp.json()
            if type(j) == dict and 'pets' in j.keys() and type(j['pets']) == list:
                if pet_id:
                    pets = [p for p in j['pets'] if type(p) == dict and 'id' in p.keys() and p['id'] == pet_id]
                    for i in range(len(pets)):
                        pets[i]['created_at'] = str(datetime.datetime.utcfromtimestamp(float(pets[i]['created_at'])))
                    return pets
                else:
                    return j['pets']
            else:
                raise PetFriendsException('List pets: Unsupported json response type:\n' + str(j))

    def create_pet(self, name: str, animal_type: str, age: int, pet_photo: str) -> list:
        if not name:
            raise PetFriendsException('Create pet failed: name is empty')
        elif age < 0 or age > 20:
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
        url = self.base_url + self.paths['create_pet']
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
            print('Cannot find pet\'s photo file:', pet_photo)
            return []

        headers = {'content-type': data.content_type, 'accept': '*/*'} | self.headers
        resp = requests.post(url, data=data, headers=headers)
        if resp.status_code != 200:
            raise PetFriendsException(f'Error create pet: {resp.status_code}: ' +
                  (resp.text if len(resp.text) < 255 else (resp.text[:253] + '...')))
        elif resp.headers['content-type'] != 'application/json':
            raise PetFriendsException('wrong response format:', resp.headers['content-type'] + ', ' +
                  resp.text if len(resp.text) < 255 else resp.text[:253] + '...')
        else:
            j = resp.json()
            if type(j) == list:
                self.my_pets += j
                return [p['id'] for p in j]

            if type(j) == dict:
                if 'id' in j.keys() and 'created_at in j.keys()':
                    j['created_at'] = str(datetime.datetime.utcfromtimestamp(float(j['created_at'])))
                    self.my_pets.append(j)
                    return [j]
            else:
                raise PetFriendsException('Unsupported json response type', j)

    def delete_pet(self, pet_id=None):
        if not pet_id:
            pet_id = self.my_pets.pop()['id']
        else:
            self.my_pets.pop([i['id'] for i in self.my_pets].index(pet_id))
        if pet_id:
            url = self.base_url + self.paths['delete_pet'] + str(pet_id)
            resp = requests.delete(url, headers=self.headers)
            if resp.status_code == 200:
                print(f'pet (id={pet_id}) deleted successfully')
                print(resp.text)
            else:
                print('Pet deletion failed: wrong reply from server:', f'{resp.status_code}: {resp.text}')
        else:
            print('Pet deletion failed: cannot find pet_id to delete. Probably pet\'s already deleted from the shop')


pet_friends = PetFriends()
if pet_friends.my_pets:
    print('There are already pets:', *pet_friends.my_pets, sep='\n')
else:
    print('There are no pets yet.')
print('Added new pet:', pet_friends.create_pet('Кусака', 'собака', 3, 'images/kusaka.jpg'))
while pet_friends.my_pets:
    pet_friends.delete_pet()
