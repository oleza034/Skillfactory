# Testing PetFriends in Selenium

## Desctiption
Testing site with different browsers. Tasks:
- [login user](https://petfriends.skillfactory.ru/login)
- open [my_pets](https://petfriends.skillfactory.ru/my_pets) page when user is logged in
- make all checkings:
 - the pet counter on the left is equal to the number of displayed pets
   <a href="https://lms.skillfactory.ru/assets/courseware/v1/276797f0a5529d308ae6e6bb045699ab/asset-v1:Skillfactory+QAP+18JUNE2020+type@asset+block/QAP.25.3.2.png" target="_blank"><img src="https://lms.skillfactory.ru/assets/courseware/v1/276797f0a5529d308ae6e6bb045699ab/asset-v1:Skillfactory+QAP+18JUNE2020+type@asset+block/QAP.25.3.2.png" alt="Picture 1. Pets counter" style="max-width: 200px;" /></a>
 - at least half of pets have photo image
 - all pets have name, animal_type and age
 - All pets names are unique, there are no pets with the same name.
- make tests with implicit waiters
- make tests with explicit waiters

***IMPORTANT***: Project has missing `.env` file with sensitive data. Please create one before using tests. Contents of .env:
``` Python
valid_email = "your@vaild.email"
valid_password = "yourP@$$w0rd"
```
If you don't have an account on site, please create one.

## Environment
To run tests, you must have the followind modules installed, for Python 3.11:
- Pytest
- Pytest-Selenium
- Python-Dotenv

Also, you must have installed browsers and their Selenium drivers. Make sure paths in [settings.py](settings.py) point to your actual browsers or drivers
