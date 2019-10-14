from flask import Blueprint, request, render_template, redirect, url_for
from flask_dance.contrib.github import github
from modules.api_func import get_gh_user_info

def user_blueprint(db):
    blueprint = Blueprint('user', __name__)

    @blueprint.route("/create", methods=['GET', 'POST'])
    def create_user():
        user = get_gh_user_info()

        if request.method == 'GET':
            return render_template("user/create_user.html", username=user["login"])

        db.users.insert_one({
            "username": user["login"],
            "avatar_url": user["avatar_url"],
            "bio": user['bio'],
            "dev_stacks": request.form["dev_stacks"],
            "contacts": request.form["contacts"]
        })
        return redirect("/feed")


    @blueprint.route("/authorize")
    def authorize():
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
        return redirect("/feed")

    @blueprint.route("/login")
    def user_login_view():
        return render_template("user/login.html")

    return blueprint