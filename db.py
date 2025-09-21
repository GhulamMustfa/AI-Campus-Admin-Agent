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


students = db["students"]
conversations = db["conversations"]
activity_logs = db["activity_logs"]


def fix_id(doc):
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc