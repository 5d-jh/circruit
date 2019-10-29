import os
from flask_dance.contrib.github import github
from flask import redirect
from functools import wraps
from pymongo import MongoClient
from api_func import get_gh_user_info

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not github.authorized:
            return redirect("/user/login")

        github.get("/user").json()

        mongo_client = MongoClient(os.environ["DATABASE_URL"])
        db = mongo_client.circruit

        user = db.users.find_one({
            "username": get_gh_user_info()["login"]
        })

        return f(user=user, *args, **kwargs)
    
    return decorated