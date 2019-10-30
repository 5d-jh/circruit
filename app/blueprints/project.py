import os, sys
sys.path.append(os.path.dirname(__file__))

from flask import Blueprint, request, render_template, redirect, url_for
from flask_dance.contrib.github import github
from modules.api_func import get_gh_projects_info, get_gh_user_info
from modules import auth_required, db_required
import json

blueprint = Blueprint('project', __name__)

@blueprint.route("/create", methods=['GET', 'POST'])
@auth_required
@db_required
def create_project(user, db):
    if request.method == "GET":
        return render_template(
            "project/feed.html",
            projects = project_list,
            user = user
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
@db_required
def feed(user, db):
    project_list = db.projects.find({
        "proj_stacks": {
            "$in": user["dev_stacks"]
        }
    })

    return render_template(
        "project/feed.html",
        projects = project_list,
        username = user["username"]
    )

@blueprint.route("/<gh_usrname>/<proj_name>")
@auth_required
@db_required
def project_detail(user, db, gh_usrname, proj_name):
    proj_info = db.projects.find_one(
        {
            "name": proj_name,
            "owner.username": gh_usrname
        }
    )
    
    if proj_info == None:
        return "프로젝트를 찾을 수 없습니다.", 404

    login_user = get_gh_user_info()
    my_todos = []
    others_todos = []
    todos_no_assignee = [] #배정 받은 사람이 아무도 없는 todo
    for todo in proj_info["todos"]:
        if len(todo["assignees"]) == 0:
            todos_no_assignee.append(todo)
            continue

        for assignee in todo["assignees"]:
            if login_user["login"] == assignee["login"]:
                my_todos.append(todo)
                break
        else:
            others_todos.append(todo)
        
    return render_template(
        "project/project_detail.html",
        proj_info = proj_info,
        my_todos = my_todos,
        others_todos = others_todos,
        todos_no_assignee = todos_no_assignee
    )

@blueprint.route("/<gh_usrname>/<proj_name>/join")
@auth_required
@db_required
def join_project(user, db, gh_usrname, proj_name):
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

@blueprint.route("/<gh_usrname>/<proj_name>/hook", methods=["POST"])
@db_required
def manage_project_todo(db, gh_usrname, proj_name):
    hook_payload = json.loads(request.data)

    if hook_payload["action"] == "opened":
        #Issue가 생성되면 새로운 todo 생성
        db.projects.update_one(
            {
                "name": proj_name,
                "owner.username": gh_usrname
            }, {
                "$push": {
                    "todos": {
                        "is_closed": False,
                        "vote": 0,
                        "id": hook_payload["issue"]["id"],
                        "title": hook_payload["issue"]["title"],
                        "link": hook_payload["issue"]["url"],
                        "assignees": hook_payload["issue"]["assignees"]
                    }
                }
            }
        )
         
    if hook_payload["action"] == "assigned":
        #Issue에 새로운 사람이 배정받게 되면 assignees 업데이트
        db.projects.update_one(
            {
                "name": proj_name,
                "owner.username": gh_usrname,
                "todos.id": hook_payload["issue"]["id"]
            }, {
                "$set": {
                    "todos.$.assignees": hook_payload["issue"]["assignees"]
                }
            }
        )

    return "OK", 200