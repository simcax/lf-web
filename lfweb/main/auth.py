import functools
import json
import os
import socket

import requests
from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from loguru import logger

hostname = socket.gethostname()
bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=("GET", "POST"))
def login():
    logger.info("/login loaded.")
    logger.info(session)
    logger.info(session.get("user_id"))
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        error, r = lfUserLogin(username, password)
        if error is None:
            session.clear()
            userData = json.loads(r.text)
            session["user_id"] = userData["id"]
            session["user_name"] = f"{userData['first_name']} {userData['last_name']}"
            session["user_email"] = userData["email"]
            logger.info("User %s logged in. redirecting to index page.", username)
            logger.info(g)
            return render_template("snippets/logged_in.html", userdata=userData)
            # eturn render_template("snippets/auth_result.html", g=g)

        flash(error, "login_error")

    return render_template("snippets/auth_result.html")


def lfUserLogin(username, password):
    apiPass = os.environ.get("API_PASSWORD")
    apiUser = os.environ.get("API_USERNAME")
    if apiUser and apiPass:
        loginData = {
            "credentials": {
                "username": username,
                "password": password,
                "field": "email",
            }
        }

        url = "https://foreninglet.dk/api/memberlogin?version=1"
        error = None
        try:
            r = requests.post(url, auth=(apiUser, apiPass), json=loginData)
            logger.info("API Login succeeded for %s", username)
            if r.status_code != 200:
                data = json.loads(r.text)
                error = "Incorrect username or password."
                logger.info(error)
        except requests.exceptions.RequestException as e:
            raise (SystemExit(e))
    else:
        error = "Api username or password not set."
        r = "No data retrieved."
        logger.error(error)
    return error, r


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        apiPass = os.environ.get("API_PASSWORD")
        apiUser = os.environ.get("API_USERNAME")
        if not apiPass or not apiUser:
            raise ("Missing API Credentials")
        url = "https://foreninglet.dk/api/members?version=1"
        try:
            r = requests.get(url, auth=(apiUser, apiPass))
            users = json.loads(r.text)
            for user in users:
                if user["MemberId"] == user_id:
                    g.user = user
                    break
        except requests.exceptions.RequestException as e:
            raise (SystemExit(e))
        # db = get_conn()

        # with db.cursor() as cur:
        #    cur.execute("SELECT * FROM soc.user WHERE id = '{}'".format(user_id))
        #    g.user = cur.fetchone()[0]


@bp.route("/logout", methods=("POST",))
def logout():
    session.clear()
    return render_template("snippets/logged_out.html")


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view
