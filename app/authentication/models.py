import time
from app import db

def get_user(user_name):
    return db.users.find_one({"username": user_name}, {"_id": 0})


def insert_user(user, hashed_password):
    db.users.insert_one({"username": user, "password": hashed_password, "registered": int(time.time())})