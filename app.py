from flask import Flask, render_template, redirect, url_for
from flask_dance.contrib.github import make_github_blueprint, github

app = Flask(__name__)
app.secret_key = "NEA#@WREBFsdfb{"
blueprint = make_github_blueprint(
    client_id="28e9cff80df971929acf",
    client_secret="e334101fb61d08f4198cf521bb8103b715fd5043",
    redirect_url="/authorize"
)
app.register_blueprint(blueprint, url_prefix="/login")

#Frontend
@app.route("/")
def index():
    return render_template("index.html")

#Backend
@app.route("/authorize")
def authorize():
    if not github.authorized:
        return redirect(url_for("github.login"))
    resp = github.get("/user")
    assert resp.ok
    return f"You are @{resp.json()['login']} on GitHub"

if __name__ == "main":
    app.run(debug=True)