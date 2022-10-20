# Small API for PetFriends
**Project URL**: https://petfriends.skillfactory.ru/apidocs/

Project needs libraries:
- json
- dotenv-python
- requests
- requests-toolbelt
- datetime

## Files
- `api.py` - API for PetFriends. Contains necessary methods for API and a simple code that uses most of them
- `settings.py` - settings with vaild email and password
- `tests/test_pet_frends.py` - tests for main methods
- `.env` - does **not** exist here. You have to create it by yourself:
```
valid_email = "<email address registered in API>"
valid_password = "<valid password for email>"
```
If you don't have email / password, you should register in https://petfriends.skillfactory.ru/
