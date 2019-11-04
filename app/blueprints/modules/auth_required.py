import os
from flask_dance.contrib.github import github
from flask import redirect
from functools import wraps
from pymongo import MongoClient
from api_func import get_gh_user_info

mongo_client = MongoClient(os.environ["DATABASE_URL"])
db = mongo_client.circruit

def auth_required(fn):
    @wraps(fn)
    def decorated(*args, **kwargs):
        if not github.authorized:
            return redirect("/user/login")

        user = db.users.find_one({
            "username": get_gh_user_info()["login"]
        })

        if user == None:
            return redirect("/user/login")

        rank_class_idx = int(user["rank"] // 250)
        icon_filename = ""
        rank_titles = [
            "브론즈 I", "브론즈 II", "브론즈 III", "브론즈 IV", "브론즈 V",
            "실버 I", "실버 II", "실버 III", "실버 IV", "실버 V",
            "플레티넘 I", "플레티넘 II", "플레티넘 III", "플레티넘 IV", "플레티넘 V",
            "다이아몬드 I", "다이아몬드 II", "다이아몬드 III", "다이아몬드 IV", "다이아몬드 V",
        ]

        icon_filename += ["B_", "S_", "P_", "D_"][int(rank_class_idx // 5)]
        icon_filename += str((rank_class_idx % 5) + 1) + "_"

        user["display_rank"] = {
            "rank_title": rank_titles[rank_class_idx],
            "exp": int(user["rank"] % 250),
            "icons": (icon_filename+"small.png", icon_filename+"regular.png", icon_filename+"large.png")
        }

        return fn(user=user, *args, **kwargs)
    
    return decorated