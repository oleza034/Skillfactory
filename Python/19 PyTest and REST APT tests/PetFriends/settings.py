import os
from dotenv import load_dotenv

load_dotenv()

valid_email = os.getenv('valid_email')
valid_password = os.getenv('valid_password')
redis_connection = os.getenv('redis_connection') # dict with server, port and password