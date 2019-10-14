from flask_dance.contrib.github import github
from flask import redirect
from functools import wraps

def get_gh_user_info():
    resp = github.get("/user")
    if resp.ok:
        return resp.json()
    else:
        None

def get_gh_projects_info(username):
    resp = github.get(f"/user/repos")
    if resp.ok:
        return resp.json()
    else:
        []

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not github.authorized:
            return redirect("/user/login")

        return f(*args, **kwargs)
    
    return decorated