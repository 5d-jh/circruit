from pymongo import MongoClient
import os

db_url = "mongodb://localhost"
mongo_client = MongoClient("mongodb://localhost")
db = mongo_client.circruit

devstacks = "Python C C++ C# Go Rust JavaScript Dart Ruby Java React Vue Angular Node.js Flask Django Expressjs Unity Unreal MachineLearning Android iOS macOS Windows Linux ReactNative Xamarin Flutter".split()
devstacks = [{"name": dvstack} for dvstack in devstacks]

print(devstacks)

db.devstacks.insert_many(devstacks)