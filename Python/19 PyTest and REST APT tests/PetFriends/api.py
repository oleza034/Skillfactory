import settings
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder


class PetFriends:
    '''
    API Help: https://petfriends.skillfactory.ru/apidocs/
    '''
    def __init__(self):
        self.base_url = 'https://petfriends.skillfactory.ru/'
        self.paths = {
            'get_api_key': 'api/key',
            'list_pets': 'api/pets',
            'create_pet': 'api/pets',
            'delete_pet': 'api/pets/'
        }
        self.headers = {'Accept': 'application/json'}
        self.my_pets = []
        self.get_api_key() # get api_key and save it in self.headers

    def get_api_key(self):
        url = self.base_url + self.paths['get_api_key']
        headers = self.headers | {'email': settings.valid_email, 'password': settings.valid_password}
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200 and resp.headers['content-type'] == 'application/json':
            j = resp.json()
            if type(j) == dict and 'key' in j.keys():
                self.headers['auth_key'] = j['key']
                print('Logon successful. api_key:', j['key'])
            else:
                print('logon error: \'key\' is not found in response keys:')
                print(j)
        elif resp.status_code == 200:
            print('logon error: wrong content-type:', resp.headers['content-type'])
            print(resp.text if len(resp.text) < 255 else resp.text[:253] + '...')
        else:
            print(f'logon error: wrong status {resp.status_code}: \'' \
                  + f'{(resp.text[:253] + "...") if len(resp.text) > 255 else resp.text}\'')

    def list_pets(self, pet_id=None):
        url = self.base_url + self.paths['list_pets']
        params = {'filter': 'my_pets'}
        resp = requests.get(url, params=params, headers=self.headers)
        if resp.status_code == 403:
            print('logon expired. Getting new api_key')
            # self.get_api_key()
        elif resp.status_code != 200:
            print(f'List pets error {resp.status_code}:',
                  (resp.text if len(resp.text) < 255 else (resp.text[:253] + '...')))
        elif resp.headers['content-type'] != 'application/json':
            print('List pets: wrong response format:', resp.headers['content-type'] + ',',
                  resp.text if len(resp.text) < 255 else resp.text[:253] + '...')
        else:
            j = resp.json()
            if type(j) == dict and 'pets' in j.keys():
                j = j['pets']
                # get list of my pets
                self.my_pets = list(i['id'] for i in j if type(i) == dict and 'id' in i.keys())
                if self.my_pets:
                    if len(j) == 1:
                        print('Found pet:', (j[0]['name'] if type(j[0]) == dict and 'name' in j[0].keys()
                              and len(j[0]['name']) > 0 else ('(no name)'
                              if type(j[0]) == dict and 'name' in j[0].keys() else 'No pets found')))
                    elif len(j) > 1:
                        print('Found pets:', end=' ')
                        print(list((i['name'] if len(i['name']) > 0 else '(no name)')
                              for i in j if type(i) == dict and 'name' in i.keys()), sep=', ')
            else:
                print('List pets: Unsupported json response type:\n', j)

    def create_pet(self, name: str, animal_type: str, age: int, pet_photo: str):
        if not name:
            print('Create pet failed: name is empty')
        elif age < 0 or age > 20:
            print('Create pet failed: wrong age')
        elif not animal_type:
            print('Create pet failed: animal_type is empty')
        elif not pet_photo:
            print('Create pet failed: empty photo URL')
        else:
            if pet_photo[-4:] == '.jpg' or pet_photo[-5:] == '.jpeg':
                photo_type = 'image/jpeg'
            elif pet_photo[-4:] == '.png':
                photo_type = 'image/x-png'
            elif pet_photo[-4:] == '.gif':
                photo_type = 'image/gif'
            else:
                photo_type = ''
            if not photo_type:
                print('photo file extension not supported:', pet_photo)
            else:
                url = self.base_url + self.paths['create_pet']
                data = MultipartEncoder(
                    fields={
                        'name': name,
                        'animal_type': animal_type,
                        'age': str(age),
                        'pet_photo': (pet_photo, open(pet_photo, 'rb'), photo_type)
                    }
                )
                # print('data =', data)
                headers = {'content-type': data.content_type, 'accept': '*/*'} | self.headers
                # print('create pet headers:', headers)
                resp = requests.post(url, data=data, headers=headers)
                if resp.status_code != 200:
                    print(f'Error create pet: {resp.status_code}:',
                          (resp.text if len(resp.text) < 255 else (resp.text[:253] + '...')))
                elif resp.headers['content-type'] != 'application/json':
                    print('wrong response format:', resp.headers['content-type'] + ',',
                          resp.text if len(resp.text) < 255 else resp.text[:253] + '...')
                else:
                    j = resp.json()
                    if type(j) == list:
                        j = j[0]

                    if type(j) == dict:
                        if 'id' in j.keys():
                            self.my_pets.append(j['id'])
                        print('Pet', j['name'] if 'name' in j.keys() and len(j['name']) > 0
                              else ('(no name)' if 'name' in j.keys() else '(#ERR)'), 'successfully added.')
                    else:
                        print('Unsupported json response type', j)

    def delete_pet(self, pet_id=None):
        if not pet_id:
            pet_id = self.my_pets.pop()
        else:
            self.my_pets.pop(self.my_pets.index(pet_id))
        if pet_id:
            url = self.base_url + self.paths['delete_pet'] + str(pet_id)
            resp = requests.delete(url, headers=self.headers)
            if resp.status_code == 200:
                print(f'pet (id={pet_id}) deleted successfully')
                print(resp.text)
            else:
                print('wrong reply from server:', f'{resp.status_code}: {resp.text}')
        else:
            print('cannot find pet_id to delete. Probably pet\'s already deleted from the shop')


pet_friends = PetFriends()
pet_friends.list_pets()
pet_friends.create_pet('Кусака', 'собака', 3, 'kusaka.jpg')
while pet_friends.my_pets:
    pet_friends.delete_pet()
