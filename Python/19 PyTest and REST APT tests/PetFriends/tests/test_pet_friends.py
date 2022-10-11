import settings
from api import PetFriends
from settings import valid_email, valid_password
from requests_toolbelt import MultipartEncoder
import os
import pytest

pf = PetFriends()


def test_get_api_key_for_invalid_user(email=settings.invalid_email, password=settings.invalid_password):
    """
    Проверяем вход с неправильными данными
    """
    # отправляем запрос на авторизацию с неправильными данными
    status, result = pf.get_api_key(force=True, email=email, password=password)
    # проверяем статус
    assert status == 403

def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """
    Получаем ключ auth_key для верных данных (email, password)
    :param email: valid_email
    :param password: valid_password
    :return:
    """
    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key()

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert type(result) is str and len(result) > 0

def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
    запрашиваем список всех питомцев и проверяем что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """

    # проверяем, есть ли действительный ключ api_key
    if 'auth_key' not in pf.headers:
        pf.get_api_key() # если нет, авторизуемся

    # отправляем запрос на получение всех питомцев
    status_code, list_pets = pf.get_pets(filter=filter)

    # проверяем статус и тело ответа
    assert status_code == 200 and type(list_pets) == list
    # тело должно быть непустым списком, и в первом питомце должно быть поле 'id' (как минимум)
    assert len(list_pets) >= 0
    if len(list_pets) > 0:
        assert type(list_pets[0]) == dict
        assert 'id' in list_pets[0].keys()

def test_get_pets_w_invalid_key(api_key = 'none'):
    """
    проверяем запрос на питомцев с неправильной авторизацией
    :param api_key: ключ с неправильной авторизацией
    :return:
    """
    # отправляем запрос на получение питомцев с заведомо неверным ключом
    status_code, list_pet = pf.get_pets(auth_key=api_key)
    # код ответа должен быть 403
    assert status_code == 403

def test_get_my_pets():
    # отправляем запрос на получение питомцев
    status, resp = pf.get_pets(filter='')

    # проверяем статус и тип тела ответа
    assert status == 200 and type(resp) == list

def test_add_new_pet_with_valid_data(name='Барбоскин', animal_type='двортерьер', age='4', pet_photo='images/cat1.jpg'):
    """Проверяем что можно добавить питомца с корректными данными"""
    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Добавляем питомца
    status, new_pet = pf.create_pet(name, animal_type, age, pet_photo)

    # проверяем статус ответа
    assert status == 200
    # Сверяем полученный ответ с ожидаемым результатом
    assert type(new_pet) == dict
    assert 'name' in new_pet.keys() and new_pet['name'] == name

def test_add_new_pet_with_partial_data(name='', animal_type='соня', age=-3, pet_photo='', bypass=True):
    """Проверяем что можно добавить питомца с корректными данными"""
    # Добавляем питомца
    status, new_pet = pf.create_pet(name, animal_type, age, pet_photo, bypass=bypass)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 400

def test_add_new_pet_with_invalid_data(name='\n', animal_type='\t', age=-500, pet_photo='', bypass=True):
    """Проверяем что можно добавить питомца с корректными данными"""
    # Добавляем питомца
    status, new_pet = pf.create_pet(name, animal_type, age, pet_photo, bypass=True)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 400

def test_create_pet_simple_correct(name='Котяра', animal_type='Сибиряк', age=2):
    # отправляем запрос на нового питомца
    status, resp = pf.create_pet_simple(name, animal_type, age)

    # Проверяем статус и тип тела ответа
    assert status == 200
    assert type(resp) in [list, dict]

def test_create_pet_simple_invalid(method='POST', path='api/create_pet_simple', body={'name': '', 'age':'3'}):
    """
    Проверяем неправильный запрос на создание питомца (simple).
    Запрос генерируется в самом тесте, не в api, поэтому берём на входе нужные для него данные с неправильным body
    :param method: метод должен быть POST
    :param path: относительный путь запроса: 'api/create_pet_simple'
    :param body: в body должно отсутствовать требуемое поле
    :return:
    """
    # в API функция отправляет все поля; мы же должны отправить не все. Поэтому пишем новый запрос
    # подготавливаем и отправляем запрос
    data = MultipartEncoder(fields=body)
    status, _ = pf.request(method, path, data.content_type, data)

    # проверяем статус
    assert status == 400

def test_update_pet(name='Мурзик', animal_type='Котэ', age=5):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, my_pets = pf.get_pets()

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets) == 0:
        _, pet = pf.create_pet("Суперкот", "кот", "3", "images/cat1.jpg")
        my_pets = [pet]

    # посылаем запрос на обновление
    status, result = pf.update_pet(my_pets[0]['id'], name, animal_type, age)

    # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
    assert status == 200
    assert result['name'] == name
    assert result['animal_type'] == animal_type
    assert result['age'] == str(age)

def test_add_invalid_photo(pet_photo=''):
    """Проверяем запрос на добавление фото с пустым фото"""
    # берём список своих питомцев
    my_pets = pf.get_pets()
    # и ищем ID питомца без фото
    pet_id = None
    if type(my_pets) == list and len(my_pets) > 0:
        for i in range(len(pf.my_pets)):
            if type(my_pets[i]) == dict and 'id' in my_pets[i].keys() and 'pet_photo' in my_pets[i].keys() \
                and my_pets[i]['pet_photo'] == '':
                pet_id = i
                break
    # если питомца без фото нет, создаём его
    if pet_id == None:
        _, pets = pf.create_pet_simple('Мурзилка', 'котик', '3')
        pet_id = pets['id']

    # отправляем запрос на добаление пустого фото с опцией bypass, чтобы игнорировать явную ошибку (для теста)
    status, resp = pf.add_photo(pet_id, pet_photo, bypass=True)

    # проверяем, что статус = 400
    assert status == 400

def test_add_valid_photo(pet_photo='images/cat1.jpg'):
    # получаем список своих питомцев
    my_pets = pf.get_pets()

    # пытаемся найти ID питомца без фото
    pet_id = None
    if type(my_pets) == list and len(my_pets) > 0:
        for i in range(len(pf.my_pets)):
            if type(my_pets[i]) == dict and 'id' in my_pets[i].keys() and 'pet_photo' in my_pets[i].keys() \
                and my_pets[i]['pet_photo'] == '':
                pet_id = i
                break
    # если не нашли, создаём нового питомца без фото
    if pet_id == None:
        _, pets = pf.create_pet_simple('Мурзилка', 'котик', '3')
        pet_id = pets['id']

    # добавляем фото
    status, resp = pf.add_photo(pet_id, pet_photo)

    # проверяем статус и наличие фото
    assert status == 200
    assert resp['pet_photo'][:23] == 'data:image/jpeg;base64,'

def test_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, my_pets = pf.get_pets()

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets) == 0:
        _, pet = pf.create_pet("Суперкот", "кот", "3", "images/cat1.jpg")
        my_pets = [pet]

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets[0]['id']

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_pets()

    # Проверяем что в списке питомцев нет id удалённого питомца
    pet_ids = [p['id'] for p in my_pets]
    assert pet_id is not None
    assert pet_id not in my_pets

def test_delete_pet_w_incorrect_id(pet_id = '99999999999'):
    """Проверяем возможность удаления питомца"""

    # запрашиваем список своих питомцев
    _, my_pets = pf.get_pets()

    # если есть питомцы, проверяем, что питомца нет среди моих питомцев:
    if len(my_pets) > 0:
        assert pet_id not in list(map(lambda x: x['id'], my_pets))

    # удаляем питомца с неправильным ключом
    status, resp = pf.delete_pet(pet_id)

    # Согласно докам, код ответа == 200, если пет был удалён (даже если его и не существовало)
    assert status == 200
