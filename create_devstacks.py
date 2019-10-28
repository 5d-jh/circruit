from pymongo import MongoClient
import os

db_url = "mongodb://localhost"
mongo_client = MongoClient(os.environ["DATABASE_URL"])
db = mongo_client.circruit

devstacks = "Python C C++ Go Rust JavaScript Ruby Java React Vue Angular Node.js Flask Django Unity Unreal MachineLearning".split()
devstacks = [{"name": dvstack} for dvstack in devstacks]

print(devstacks)

db.devstacks.insert_many(devstacks)