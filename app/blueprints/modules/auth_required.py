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

        rank_titles = [
            "브론즈 I", "브론즈 II", "브론즈 III", "브론즈 IV", "브론즈 V",
            "실버 I", "실버 II", "실버 III", "실버 IV", "실버 V",
            "플레티넘 I", "플레티넘 II", "플레티넘 III", "플레티넘 IV", "플레티넘 V",
            "다이아몬드 I", "다이아몬드 II", "다이아몬드 III", "다이아몬드 IV", "다이아몬드 V",
        ]
        user["display_rank"] = { 
            "rank_title": rank_titles[int(user["rank"]//250)],
            "exp": int(user["rank"]%250)
        }

        return f(user=user, *args, **kwargs)
    
    return decorated