from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def db_uri():
    try:
        client = MongoClient(os.getenv("DB_URI"))
        print("DataBase connected successfully ")
        return client
    except Exception as e:
        print(f"Error connecting to DataBase, {e}")
        return None

client = db_uri()
db = client["campus_admin_agent"]

students_collection = db["students"]
get_db = db["events"]
admins_collection = db["admins"]
threads_collection = db["threads"]
