import os, sys
sys.path.append(os.path.dirname(__file__))

from flask import Blueprint, request, render_template, redirect, url_for
from flask_dance.contrib.github import github
from modules.api_func import get_gh_projects_info
from modules import auth_required

def project_blueprint(db):
    blueprint = Blueprint('project', __name__)

    @blueprint.route("/create", methods=['GET', 'POST'])
    @auth_required
    def create_project(user):
        if request.method == "GET":
            return render_template(
                "project/submit_project.html",
                user = user,
                projects = get_gh_projects_info(user["username"]),
                devstacks = db.devstacks.find()
            )
        elif request.method == "POST":
            if len(request.form["name"]) == 0 or len(request.form["proj_stacks"]) == 0:
                return "Data is missing", 400

            user["project_rank"] = 0

            db.projects.update_one(
                {
                    "name": request.form["name"]
                }, {
                    "$set": {
                        "name": request.form["name"],
                        "rank": 0,
                        "proj_stacks": request.form["proj_stacks"].split(" ")[1:],
                        "owner": user,
                        "collaborators": [user]
                    }
                },
                upsert=True
            )

            return redirect("/project/feed")
    
    @blueprint.route("/feed")
    @auth_required
    def feed(user):
        project_list = db.projects.find({
            "proj_stacks": {
                "$in": user["dev_stacks"]
            }
        })

        return render_template(
            "project/feed.html",
            projects = project_list,
            user = user
        )

    @blueprint.route("/<gh_usrname>/<proj_name>")
    @auth_required
    def project_detail(user, gh_usrname, proj_name):
        proj_info = None
        proj_by_name = db.projects.find(
            {
                "name": proj_name
            }
        )

        #GitHub에서는 다른 사용자가 같은 저장소 이름을 사용할 수 있으므로 사용자 이름까지 체크
        for proj in proj_by_name:
            if proj["owner"]["username"] == gh_usrname:
                proj_info = proj
                break
        
        if proj_info == None:
            return "프로젝트를 찾을 수 없습니다.", 404

        return render_template(
            "project/project_detail.html",
            proj_info = proj_info
        )

    @blueprint.route("/<gh_usrname>/<proj_name>/join")
    @auth_required
    def join_project(user, gh_usrname, proj_name):
        user["project_rank"] = 0

        try:
            db.projects.update_one(
                {
                    "name": proj_name,
                    "owner.username": gh_usrname
                }, {
                    "$addToSet": {
                        "collaborators": user
                    }
                }
            )
            return redirect(f"/project/{gh_usrname}/{proj_name}")
        except:
            return "프로젝트에 참여하는 과정에서 오류가 발생했습니다.", 503

    return blueprint