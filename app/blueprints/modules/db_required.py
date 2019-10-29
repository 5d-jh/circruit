from pymongo import MongoClient
from functools import wraps
import os

mongo_client = MongoClient(os.environ["DATABASE_URL"] or "mongodb://localhost")
db = mongo_client.circruit

def db_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        return f(db=db, *args, **kwargs)
    
    return decorated