import os, sys
sys.path.append(os.path.dirname(__file__))

from flask import Blueprint, request, render_template, redirect, url_for
from flask_dance.contrib.github import github
from modules.api_func import get_gh_user_info
from modules import db_required

blueprint = Blueprint('user', __name__)

@blueprint.route("/create", methods=['GET', 'POST'])
@db_required
def create_user(db):
    user = get_gh_user_info()

    if request.method == "GET":
        return render_template(
            "user/create_user.html",
            username=user["login"],
            dev_stacks=db.devstacks.find()
        )
    elif request.method == "POST":
        db.users.insert_one({
            "username": user["login"],
            "avatar_url": user["avatar_url"],
            "bio": user['bio'],
            "rank": 0,
            "dev_stacks": request.form["dev_stacks"].split(" ")[1:],
            "contacts": request.form["contacts"],
            "joined_projects": []
        })

    return redirect("/mypage")


@blueprint.route("/authorize")
@db_required
def authorize(db):
    if not github.authorized:
        #깃허브 승인 페이지로 이동
        return redirect(url_for("github.login"))

    #승인 후 다시 이 페이지로 돌아와서 깃허브 유저 정보 획득
    user = get_gh_user_info()

    users_collection = db.users

    #이미 회원가입된 사람인지 확인
    result = users_collection.find_one({
        "username": user["login"]
    })

    #신규 사용자라면 도큐먼트 생성 후 회원가입 페이지로 이동
    if not result:
        return redirect(f"/user/create")

    #기존 사용자라면 피드로 이동
    return redirect("/")

@blueprint.route("/login")
def user_login_view():
    return render_template("user/login.html")
