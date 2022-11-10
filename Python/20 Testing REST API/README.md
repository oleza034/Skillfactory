# Тестирование API портала https://petfriends.skillfactory.ru/

## Задание 20.4.1 - план тестирования всех запросов:
1. [Тестирование запроса GET /api/key](tests/1_get_api_key.md)
2. [Тестирование запроса GET /api/pets](tests/2_get_api_pets.md)
3. [Тестирование запроса POST /api/create_pet_simple](tests/3_create_pet_simple.md)
4. [Тестирование запроса POST /api/pets/set_photo](tests/4_post_api_pets_set_photo.md)
5. [Тестирование запроса POST /api/pets](tests/5_post_api_pets.md)
6. [Тестирование запроса PUT /api/pets](tests/6_put_api_pets.md)
7. [Тестирование запроса DELETE /api/pets](tests/7_delete_api_pets.md)
8. [Пользовательские сценарии тестирования](user_tests.md) (*пока* не имплементированы на Python)

## Структура проекта
- Файлы `api.py`, `settings.py` - файлы проекта
- Директория `tests` с файлами `test_n_*.py` - разделы тестирования конкретного запроса, а файлы `n_*.md` - тестовая документация
- Директория `images` содержит иллюстрации к тестовой документации
- Файл `.env` (не загружен в GIT) содержит следующую структуру:
```
# both users **must** be registered on portal
valid_email = 'user1@email1.com'
valid_password = 'User1_password'
email2 = 'user2@email2.com'
password2 = 'User2_password'
```

**Внимание**! Проект Python ссылается на следующие модули:
- `json`
- `python-dateutil`
- `python-dotenv`
- `random`
- `requests`
- `requests-toolbelt`
- `urllib.parse`
