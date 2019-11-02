import os, sys
sys.path.append(os.path.dirname(__file__))

from flask import Blueprint, request, render_template, redirect, url_for
from flask_dance.contrib.github import github
from modules.api_func import get_gh_projects_info, get_gh_user_info
from modules import auth_required, db_required
from datetime import datetime, timedelta
import json
import copy

blueprint = Blueprint('project', __name__)

@blueprint.route("/create", methods=['GET', 'POST'])
@auth_required
@db_required
def create_project(user, db):
    if request.method == "GET":
        return render_template(
            "project/submit_project.html",
            user=user,
            projects=get_gh_projects_info(user["username"]),
            devstacks=db.devstacks.find()
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
                    "status": "recruiting",
                    "proj_stacks": request.form["proj_stacks"].split(" ")[1:],
                    "owner": user,
                    "collaborators": [user],
                    "todos": [],
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
        projects=project_list,
        user=user
    )

@blueprint.route("/<gh_usrname>/<proj_name>")
@auth_required
@db_required
def project_detail(user, db, gh_usrname, proj_name):
    project = db.projects.find_one(
        {
            "name": proj_name,
            "owner.username": gh_usrname
        }
    )
    
    if project == None:
        return "프로젝트를 찾을 수 없습니다.", 404
        
    return render_template(
        "project/project_detail.html",
        project=project,
        user=user,
        is_owner=project["owner"]["username"] == user["username"]
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

@blueprint.route("/<gh_usrname>/<proj_name>/end")
@auth_required
@db_required
def end_project(user, db, gh_usrname, proj_name):
    project = db.projects.find_one(
        {
            "name": proj_name,
            "owner.username": gh_usrname
        }
    )

    if project == None:
        return "프로젝트를 찾을 수 없습니다.", 404

    if project["owner"]["username"] != user["username"]:
        return "프로젝트를 마칠 권환이 없습니다.", 403
    
    for todo in project["todos"]:
        db.users.update_many(
            {
                "username": {
                    "$in": [assignee["username"] for assignee in todo["assignees"]]
                }
            }, {
                "$inc": {
                    "rank": todo["vote"]["good"]*100 - todo["vote"]["bad"]*70
                }
            }
        )

    db.projects.update_one(
        {
            "name": proj_name,
            "owner.username": gh_usrname
        }, {
            "$set": {
                "status": "end"
            }
        }
    )

    return redirect(f"/project/{gh_usrname}/{proj_name}/todo")

@blueprint.route("/<gh_usrname>/<proj_name>/todo")
@auth_required
@db_required
def project_todo_view(user, db, gh_usrname, proj_name):
    project = db.projects.find_one(
        {
            "name": proj_name,
            "owner.username": gh_usrname
        }
    )

    if project == None:
        return "프로젝트를 찾을 수 없습니다.", 404

    my_todos = []
    others_todos = []
    todos_no_assignee = [] #배정 받은 사람이 아무도 없는 todo
    for todo in project["todos"]:
        if len(todo["assignees"]) == 0:
            todos_no_assignee.append(todo)
            continue

        for assignee in todo["assignees"]:
            if user["username"] == assignee["username"]:
                my_todos.append(todo)
                break
        else:
            others_todos.append(todo)
    
    #날짜순으로 정렬
    my_todos.sort(key=lambda t: t["deadline"])

    #가장 급한 todo가 뭔지 찾음
    my_most_urgents = []
    for i in range(1, len(my_todos)):
        prev_date = my_todos[i-1]["deadline"].strftime("%Y%m%d")
        next_date = my_todos[i-1]["deadline"].strftime("%Y%m%d")
        if prev_date == next_date:
            my_most_urgents = copy.deepcopy(my_todos[0:i+1])
            break

    return render_template(
        "project/project_todo.html",
        project = project,
        my_todos = my_todos,
        my_most_urgents = my_most_urgents,
        others_todos = others_todos,
        todos_no_assignee = todos_no_assignee,
        user = user
    )

@blueprint.route("/<gh_usrname>/<proj_name>/todo/vote", methods=["POST"])
@auth_required
@db_required
def project_todo_vote(user, db, gh_usrname, proj_name):
    project = db.projects.find_one(
        {
            "name": proj_name,
            "owner.username": gh_usrname
        }
    )

    if project == None:
        return "프로젝트를 찾을 수 없습니다.", 404

    good_issue_ids = list(map(int, request.form.keys()))

    for todo in project["todos"]:
        if todo["is_closed"] and not gh_usrname in todo["voted"]:
            if todo["id"] in good_issue_ids:
                todo["vote"]["good"] += 1
            else:
                todo["vote"]["bad"] += 1

            todo["voted"].append(gh_usrname)

    db.projects.update_one(
        {
            "name": proj_name,
            "owner.username": gh_usrname
        }, {
            "$set": {
                "todos": project["todos"]
            }
        }
    )

    return redirect(f"/project/{gh_usrname}/{proj_name}/todo")

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
                        "voted": [],
                        "vote": {
                            "good": 0,
                            "bad": 0
                        },
                        "id": hook_payload["issue"]["id"],
                        "title": hook_payload["issue"]["title"],
                        "link": hook_payload["issue"]["html_url"],
                        "deadline": datetime.now()+timedelta(days=7),
                        "assignees": [
                            {
                                "username": assignee["login"],
                                "avatar_url": assignee["avatar_url"]
                            } for assignee in hook_payload["issue"]["assignees"]
                        ]
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
                    "todos.$.assignees": [
                        {
                            "username": assignee["login"],
                            "avatar_url": assignee["avatar_url"]
                        } for assignee in hook_payload["issue"]["assignees"]
                    ]
                }
            }
        )

    if hook_payload["action"] == "closed":
        db.projects.update_one(
            {
                "name": proj_name,
                "owner.username": gh_usrname,
                "todos.id": hook_payload["issue"]["id"]
            }, {
                "$set": {
                    "todos.$.is_closed": True
                }
            }
        )

    return "OK", 200
