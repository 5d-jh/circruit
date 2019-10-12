import os
from flask import Flask, render_template, redirect, url_for, request
from flask_dance.contrib.github import make_github_blueprint, github
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = "NEA#@WREBFsdfb{"
blueprint = make_github_blueprint(
    client_id="28e9cff80df971929acf",
    client_secret="e334101fb61d08f4198cf521bb8103b715fd5043",
    redirect_url="/user/authorize"
)
app.register_blueprint(blueprint, url_prefix="/login")

mongo_client = MongoClient(os.environ["DATABASE_URL"])
db = mongo_client.circruit

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/feed")
def feed():
    return render_template("feed.html")


@app.route("/user/create", methods=['GET', 'POST'])
def create_user():
    resp = github.get("/user")
    assert resp.ok
    user = resp.json()

    if request.method == 'GET':
        return render_template("create_user.html", username=user["login"])

    db.users.insert_one({
        "username": user["login"],
        "avatar_url": user["avatar_url"],
        "bio": user['bio'],
        "dev_stacks": request.form["dev_stacks"],
        "contacts": request.form["contacts"]
    })
    return redirect("/feed")


@app.route("/user/authorize")
def authorize():
    if not github.authorized:
        #깃허브 승인 페이지로 이동
        return redirect(url_for("github.login"))

    #승인 후 다시 이 페이지로 돌아와서 깃허브 유저 정보 획득
    resp = github.get("/user")
    assert resp.ok
    user = resp.json()

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

if __name__ == "main":
    app.run(debug=True)