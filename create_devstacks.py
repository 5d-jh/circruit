from pymongo import MongoClient

mongo_client = MongoClient("mongodb://circruitdb:FK7QSRVGwYoKObRfSRjdycTSjXluNvrKaOiMhgzX4GbmuaR51QZX5UCHBlBeYA3ogEhvy2XqeoyPEpUoj2OS5g==@circruitdb.documents.azure.com:10255/?ssl=true&replicaSet=globaldb")
db = mongo_client.circruit

stacks = [
    "javascript",
    "python",
    "c",
    "c#",
    "c++",
    "objective-C",
    "java",
    "kotlin",
    "typescript",
    "swift",
    "nodejs",
    "dart",
    "flutter",
    "react",
    "vue",
    "angular",
    "react-native",
    "xamarin",
    "go",
    "SQL",
    "php",
    "ruby",
    "visual basic",
    "matlab",
    "r",
    "unity",
    "unreal",
    "machine learning",
    "deep learning",
    "reinforcement learning",
    "spring",
    "flask",
    "django",
    "ruby on rails",
    "docker",
    ".NET framework",
    "serverless",
    "laravel",
    "expressjs",
    "android",
    "ios",
    "windows",
    "macOS",
    "UWP"
]

# for stack in stacks:
#     db.devstacks.replace_one({
#         "name": stack
#     }, {
#         "name": stack
#     }, True)

print("done")



print(list(db.devstacks.find()))