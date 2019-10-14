import os
from flask import Flask, render_template, redirect, url_for, request
from flask_dance.contrib.github import make_github_blueprint, github
from pymongo import MongoClient
from modules.user import user_blueprint
from modules.project import project_blueprint
from modules.api_func import get_gh_user_info

app = Flask(__name__)
app.secret_key = "NEA#@WREBFsdfb{"
blueprint = make_github_blueprint(
    client_id="28e9cff80df971929acf",
    client_secret="e334101fb61d08f4198cf521bb8103b715fd5043",
    redirect_url="/user/authorize",
    scope="repo,user"
)
app.register_blueprint(blueprint, url_prefix="/login")

mongo_client = MongoClient(os.environ["DATABASE_URL"])
db = mongo_client.circruit

@app.before_request
def before_request():
    pass
    # if not github.authorized:
    #     return render_template("login.html")
    
@app.route("/")
def index():
    if not github.authorized:
        return redirect("/user/login")

    return redirect("/mypage")

@app.route("/mypage")
def my_page():
    user = get_gh_user_info()

    return render_template(
        "user/mypage.html",
        username = user["login"] if user else None
    )

app.register_blueprint(user_blueprint(db), url_prefix="/user")
app.register_blueprint(project_blueprint(db), url_prefix="/project")

if __name__ == "main":
    app.run(debug=True)