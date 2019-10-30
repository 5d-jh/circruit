import os, sys
sys.path.append(os.path.dirname(__file__))

from flask import Flask, render_template, redirect, url_for, request
from flask_dance.contrib.github import make_github_blueprint, github
from pymongo import MongoClient
from blueprints import user, project
from blueprints.modules.api_func import get_gh_user_info
from blueprints.modules import auth_required

mongo_client = MongoClient(os.environ["DATABASE_URL"])
db = mongo_client.circruit

app = Flask(__name__)
app.secret_key = "NEA#@WREBFsdfb{"
blueprint = make_github_blueprint(
    client_id="28e9cff80df971929acf",
    client_secret="e334101fb61d08f4198cf521bb8103b715fd5043",
    redirect_url="/user/authorize",
    scope="repo,user"
)
app.register_blueprint(blueprint, url_prefix="/login")

@app.route("/")
def index():
    if not github.authorized:
        return redirect("/user/login")

    return redirect("/mypage")

@app.route("/mypage")
@auth_required
def my_page(user):
    section = request.args.get("section")

    return render_template(
        "user/mypage.html",
        user = user,
        section = section
    )

app.register_blueprint(user.blueprint, url_prefix="/user")
app.register_blueprint(project.blueprint, url_prefix="/project")

if __name__ == "main":
    app.run()