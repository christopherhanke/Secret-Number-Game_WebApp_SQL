import random
import uuid
import hashlib

from datetime import datetime
from flask import Flask, render_template, request, make_response, redirect, url_for
from models import User, db
from werkzeug.exceptions import HTTPException


# runtime environment starts
app = Flask(__name__)
db.create_all()


# index page
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("user-name")
        email = request.form.get("user-email")
        password = request.form.get("user-password")
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        user = db.query(User).filter_by(email=email).first()
        if not user:
            user = User(
                name=name,
                email=email,
                secret_number=random.randint(1, 30),
                password=hashed_password,
                solved=None,
                deleted=False
            )
            db.add(user)
            db.commit()

        if hashed_password != user.password:
            return "Wrong password! Go back and try again."

        session_token = str(uuid.uuid4())
        user.session_token = session_token
        db.add(user)
        db.commit()

        response = make_response(render_template("game.html"))
        response.set_cookie("session_token", session_token, httponly=True, samesite="Strict")
        return response

    else:
        return render_template("welcome.html")


# game page and game routine
@app.route("/game", methods=["GET", "POST"])
def game():
    if request.method == "POST":
        session_token = request.cookies.get("session_token")
        user = db.query(User).filter_by(session_token=session_token, deleted=False).first()

        if not user:
            return redirect(url_for("index"))

        try:
            guess = int(request.form.get("guess"))
        except ValueError:
            return render_template("game.html", no_int=True)

        if guess < user.secret_number:
            helpline = "Your guess is below the secret number."
        elif guess > user.secret_number:
            helpline = "Your guess is above the secret number."
        else:
            if not user.solved:
                user.solved = datetime.now()
                db.commit()
            helpline = "Hooray"

        return render_template("game.html", helpline=helpline)

    else:
        session_token = request.cookies.get("session_token")
        user = db.query(User).filter_by(session_token=session_token, deleted=False).first()

        if user:
            return render_template("game.html")
        else:
            return redirect(url_for("index"))


@app.route("/profile", methods=["GET"])
def profile():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token, deleted=False).first()

    if user:
        return render_template("profile.html", user=user)
    else:
        return redirect(url_for("index"))


@app.route("/profile/edit", methods=["GET", "POST"])
def profile_edit():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token, deleted=False).first()

    if request.method == "GET":
        if user:
            return render_template("profile_edit.html", user=user)
        else:
            return redirect(url_for("index"))

    elif request.method == "POST":
        if not user:
            return redirect(url_for("index"))

        name = request.form.get("user-name")
        email = request.form.get("user-email")

        user.name = name
        user.email = email
        db.add(user)
        db.commit()

        return redirect(url_for("profile"))


@app.route("/profile/delete", methods=["GET", "POST"])
def profile_delete():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token, deleted=False).first()

    if request.method == "GET":
        if user:
            return render_template("profile_delete.html", user=user)
        else:
            return redirect(url_for("index"))
    elif request.method == "POST":
        if not user:
            return redirect(url_for("index"))

        user.deleted = True
        db.commit()

        return redirect(url_for("index"))


@app.route("/users", methods=["GET"])
def all_users():
    users = db.query(User).filter_by(deleted=False).all()

    return render_template("users.html", users=users)


@app.route("/users/<user_id>", methods=["GET"])
def user_details(user_id):
    user = db.query(User).get(int(user_id))
    return render_template("user_details.html", user=user)


# top score page
# TODO
@app.route("/topscore")
def topscore():
    return redirect(url_for("index"))


def get_user_from_request():
    session_token = request.cookies.get("session_token")
    if not session_token:
        raise HTTPException("Session Token required", redirect(url_for("index")))
    user = db.query(User).filter_by(session_token=session_token, deleted=False).first()
    if not user:
        raise HTTPException("User required", redirect(url_for("index")))
    return user


# main routine to start the app
if __name__ == "__main__":
    app.run(debug=True)
