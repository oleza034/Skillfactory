from dotenv import load_dotenv
import os

base_url = 'https://petfriends.skillfactory.ru'
auth_path = '/login'

load_dotenv()
valid_email = os.getenv('valid_email')
valid_password = os.getenv('valid_password')