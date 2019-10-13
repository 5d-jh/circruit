from flask_dance.contrib.github import github

def get_gh_user_info():
    resp = github.get("/user")
    if resp.ok:
        return resp.json()
    else:
        None