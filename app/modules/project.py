import os, sys
sys.path.append(os.path.dirname(__file__))

from flask import Blueprint, request, render_template, redirect, url_for
from flask_dance.contrib.github import github
from .api_func import get_gh_user_info, get_gh_projects_info, auth_required

def project_blueprint(db):
    blueprint = Blueprint('project', __name__)

    @blueprint.route("/create", methods=['GET', 'POST'])
    def create_project():
        user = get_gh_user_info()

        if request.method == "GET":
            return render_template(
                "project/submit_project.html",
                username = user["login"],
                projects = get_gh_projects_info(user["login"]),
                devstacks = db.devstacks.find()
            )
        elif request.method == "POST":
            if len(request.form["name"]) == 0 or len(request.form["proj_stacks"]) == 0:
                return "Data is missing", 400

            db_user = db.users.find_one({
                "username": user["login"]
            })
            db_user["project_rank"] = 0

            db.projects.update_one(
                {
                    "name": request.form["name"]
                }, {
                    "$set": {
                        "name": request.form["name"],
                        "rank": 0,
                        "proj_stacks": request.form["proj_stacks"].split(" ")[1:],
                        "collaborators": [db_user]
                    }
                },
                upsert=True
            )

            return redirect("/project/feed")
    
    @blueprint.route("/feed")
    @auth_required
    def feed():
        user = get_gh_user_info()
        return render_template("project/feed.html", projects=db.projects.find(), username = user["login"])

    return blueprint