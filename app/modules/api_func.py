import os, sys
sys.path.append(os.path.dirname(__file__))

from flask_dance.contrib.github import github
from flask import redirect
from functools import wraps
from pymongo import MongoClient

def get_gh_user_info():
    resp = github.get("/user")
    if resp.ok:
        return resp.json()
    else:
        None

def get_gh_projects_info(username):
    resp = github.get(f"/user/repos")
    if resp.ok:
        return resp.json()
    else:
        []

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not github.authorized:
            return redirect("/user/login")

        mongo_client = MongoClient(os.environ["DATABASE_URL"])
        db = mongo_client.circruit

        user = db.users.find_one({
            "username": get_gh_user_info()["login"]
        })

        return f(user, *args, **kwargs)
    
    return decorated