from dotenv import load_dotenv, find_dotenv
import os

if not load_dotenv(find_dotenv()):
    raise RuntimeError(".env file not found! Please create it.")

DB_PATH = os.getenv("DB_PATH", "currency.db")
BASE_URL = os.getenv("BASE_URL", "http://localhost")
BASE_PORT = int(os.getenv("BASE_PORT", 8000))
