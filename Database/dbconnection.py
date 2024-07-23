from pymongo import MongoClient
import os


def get_db_connection():
    client = MongoClient(os.environ["MONGO_DB_KEY"])
    db = client.news_db
    return db
