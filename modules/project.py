from flask import Blueprint, request, render_template, redirect, url_for
from flask_dance.contrib.github import github
from modules.api_func import get_gh_user_info, get_gh_projects_info

def project_blueprint(db):
    blueprint = Blueprint('project', __name__)

    @blueprint.route("/create", methods=['GET', 'POST'])
    def create_user():
        user = get_gh_user_info()

        if request.method == "GET":
            return render_template(
                "project/submit_project.html",
                username = user["login"],
                projects = get_gh_projects_info(user["login"]),
                devstacks = db.devstacks.find()
            )
        elif request.method == "POST":
            db_user = db.users.find_one({
                "username": user["login"]
            })
            db_user["project_rank"] = 0

            db.projects.replace_one(
                {
                    "name": request.form["name"]
                }, {
                    "name": request.form["name"],
                    "rank": 0,
                    "proj_stacks": request.form["proj_stacks"].split(" ")[1:],
                    "collaborators": [db_user]
                }
            )

            return "Good"
    
    @blueprint.route("/feed")
    def feed():
        return render_template("project/feed.html", projects=db.projects.find())

    return blueprint