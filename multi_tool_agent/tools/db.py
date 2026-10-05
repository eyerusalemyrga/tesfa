import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    db_config = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", 5432)),
        "dbname": os.getenv("DB_NAME", "tesfa"),  # Change from 'tesfa_db' to os.getenv("DB_NAME", "tesfa")
        "user": os.getenv("DB_USER", "tesfa_user"),
        "password": os.getenv("DB_PASSWORD", "mysecretpassword"),
    }
    return psycopg2.connect(**db_config, cursor_factory=RealDictCursor)