import os, sys
sys.path.append(os.path.dirname(__file__))

from flask import Flask, render_template, redirect, url_for, request
from flask_dance.contrib.github import make_github_blueprint, github
from pymongo import MongoClient
from blueprints import user, project
from blueprints.modules.api_func import get_gh_user_info
from blueprints.modules import auth_required
from modules import display_rank
from blueprints.modules import auth_required, db_required

mongo_client = MongoClient(os.environ["DATABASE_URL"])
db = mongo_client.circruit

DEV_ENV = os.environ["FLASK_ENV"] == "development"

app = Flask(__name__)
app.secret_key = "NEA#@WREBFsdfb{"
blueprint = make_github_blueprint(
    client_id=("8ca7590993a769d4d8aa" if DEV_ENV else "28e9cff80df971929acf"),
    client_secret=("a85159c48436050fc1558d6f2b41bb944e027823" if DEV_ENV else "e334101fb61d08f4198cf521bb8103b715fd5043"),
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
@db_required
def my_page(user,db):
    projects=db.projects.find({})
    print(projects)
    section = request.args.get("section")

    rank, point = display_rank(user["rank"])

    return render_template(
        "user/mypage.html",
        user=user,
        section=section,
        rank_title=user["display_rank"]["rank_title"],
        exp=user["exp"],
        projects=projects
    )

app.register_blueprint(user.blueprint, url_prefix="/user")
app.register_blueprint(project.blueprint, url_prefix="/project")

if __name__ == "main":
    app.run(debug=True)