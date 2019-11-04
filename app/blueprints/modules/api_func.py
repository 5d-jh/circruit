import os, sys
sys.path.append(os.path.dirname(__file__))

from flask_dance.contrib.github import github
from flask import redirect
from functools import wraps
from pymongo import MongoClient

def get_gh_user_info():
    resp = github.get("/user")
    if resp.ok:
        return resp.json()
    else:
        None

def get_gh_projects_info():
    resp = github.get("/user/repos?affiliation=owner")
    json_data = resp.json()
    if resp.ok:
        return resp.json()
    else:
        []