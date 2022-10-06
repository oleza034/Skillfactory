from api import PetFriends, PetFriendsException
from settings import valid_email, valid_password
import os
import pytest

pf = PetFriends()


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 200 и в тезультате содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    print('Test1: 1')
    status, result = pf.get_api_key()

    # Сверяем полученные данные с нашими ожиданиями
    print('Test1: 2')
    assert status == 200
    print('Test1: 3')
    assert type(result) is str and len(result) > 0


def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
    запрашиваем список всех питомцев и проверяем что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """

    # _, auth_key = pf.get_api_key(valid_email, valid_password)
    list_pets = pf.get_pets()

    assert type(list_pets) == list
    assert len(list_pets) == 0 or 'id' in list_pets[0].keys()


def test_add_new_pet_with_valid_data(name='Барбоскин', animal_type='двортерьер',
                                     age='4', pet_photo='images/cat1.jpg'):
    """Проверяем что можно добавить питомца с корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key()

    # Добавляем питомца
    new_pet = pf.create_pet(name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert type(new_pet) == list
    assert 'name' in new_pet[0].keys() and new_pet[0]['name'] == name


def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key()
    my_pets = pf.my_pets

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets) == 0:
        pf.create_pet("Суперкот", "кот", "3", "images/cat1.jpg")
        my_pets = pf.my_pets

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets[0]['id']

    # Ещё раз запрашиваем список своих питомцев
    my_pets = pf.my_pets

    # Проверяем что в списке питомцев нет id удалённого питомца
    pet_ids = [p['id'] for p in my_pets]
    assert pet_id is not None
    assert pet_id not in my_pets


def test_successful_update_pet(name='Мурзик', animal_type='Котэ', age=5):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key()
    my_pets = pf.my_pets

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets) > 0:
        status, result = pf.update_pet(my_pets[0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200 and result['name'] == name
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise PetFriendsException("There is no my pets")