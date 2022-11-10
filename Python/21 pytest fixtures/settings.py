from dotenv import load_dotenv
from os import getenv, path
from datetime import datetime


load_dotenv()

# variables from .env file
valid_email = getenv('valid_email')
valid_password = getenv('valid_password')
email2 = getenv('email2')
password2 = getenv('password2')
base_url = 'https://petfriends.skillfactory.ru/'
log_file = 'log_' + datetime.now().strftime('%Y%m%d') + '.txt'
log_path = path.join(path.dirname(__file__), 'logs')
expired_auth_key = 'd8b2ab76e42f5370ca3a8ea8265117a42d71b48a62d29766d34784e2'
