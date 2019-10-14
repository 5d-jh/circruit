from flask_dance.contrib.github import github

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