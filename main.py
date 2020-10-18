import random

from datetime import datetime
from flask import Flask, render_template, request, make_response, redirect, url_for
from models import User, db


# runtime environment starts
app = Flask(__name__)
db.create_all()


# index page
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("user-name")
        email = request.form.get("user-email")

        user = db.query(User).filter_by(email=email).first()
        if not user:
            user = User(name=name, email=email, secret_number=random.randint(1, 30), solved=None)
            db.add(user)
            db.commit()

        response = make_response(render_template("game.html"))
        response.set_cookie("email", email)

        return response

    else:
        return render_template("welcome.html")


# game page and game routine
@app.route("/game", methods=["GET", "POST"])
def game():
    if request.method == "POST":
        email = request.cookies.get("email")
        if not email:
            return redirect(url_for("index"))

        user = db.query(User).filter_by(email=email).first()

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
        return render_template("game.html")


# main routine to start the app
if __name__ == "__main__":
    app.run(debug=True)
