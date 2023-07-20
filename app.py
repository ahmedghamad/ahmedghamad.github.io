import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

from helpers import apology, login_required, get_books

# Configure application
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///books.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


"""route to view the history of the users recomendations """


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    reconmendations = db.execute("SELECT recomendations FROM portfolio WHERE id = ?", session["user_id"])
    if len(reconmendations) == 0:  # if there has not been any transactions
        return render_template("success.html")
    else:

        return render_template("recomended.html", reconmendations=reconmendations)  # displays previous transactions


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/search")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


""" displays the books through post and display a table with the a list of books using GET """


@app.route("/search", methods=["GET", "POST"])
@login_required
def quote():

    if request.method == "GET":
        return render_template("search.html")
    if request.method == "POST":
        genre = request.form.get("Categories")
        reconmendations = get_books(genre)
        if reconmendations == None:
            return apology("There are no recomendations")
        else:
            for reconmendation in reconmendations:
                book_title = reconmendation['title']
                existing_book = db.execute("SELECT recomendations FROM portfolio WHERE id = ?",session["user_id"] ) # checks if it already in the db
                if book_title != existing_book:
                    db.execute("INSERT INTO portfolio (id, recomendations) VALUES (?, ?)", session["user_id"], book_title) # adds to teh db

            return render_template("results.html", reconmendations=reconmendations)



""" displays register fourm through GET and cheks for validations then inserts user in db through POST and creats a portfolio table and history table """


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")  # display the register fourm
    if request.method == "POST":
        name = request.form.get("username")
        password = request.form.get("password")
        password_confirmation = request.form.get("confirmation")
        if not name:  # check not empty
            return apology("must provide username")
        if not password or not password_confirmation:  # check not empty
            return apology("must provide password")
        if password != password_confirmation:  # checks if passwords match
            return apology("New passwrod does not match password confirmation")
        usernames = db.execute("SELECT * FROM users WHERE username = ? ", name)  # checks if the name already exists
        if len(usernames) > 0:
            return apology("username already exists")

        hash_password = generate_password_hash(password)  # hashs the password
        # inserts the username and password into the users db
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", name, hash_password)
        rows = db.execute("SELECT * FROM users WHERE username = ?", name)
        session["user_id"] = rows[0]["id"]
        db.execute("CREATE TABLE IF NOT EXISTS portfolio (id INTEGER, recomendations TEXT NOT NULL, FOREIGN KEY (id) REFERENCES users(id));")
        return redirect("/history")



"""Chaning the users password route"""


@app.route("/changePassword", methods=["GET", "POST"])
@login_required
def changePassword():
    if request.method == "GET":
        return render_template("changePassword.html")
    if request.method == "POST":
        oldPassword = request.form.get("oldpassword")
        new_password = request.form.get("newpassword")
        password_confirmation = request.form.get("newpasswordconfirmation")
        if not oldPassword:  # checks for the old password not empty
            return apology("must provide old password")
        if not new_password:  # checks for the new password not empty
            return apology("must provide new password")

        if not password_confirmation:  # checks for the password confirmation not empty
            return apology("must provide new password confirmation")

        check_existingPassword = db.execute("SELECT hash FROM users WHERE id = ?", session["user_id"])
        check_existingPassword = check_existingPassword[0]['hash']
        check_Password = check_password_hash(check_existingPassword, oldPassword)
        if check_Password == True:
            if new_password != password_confirmation:  # checks if old password matches what is stored on the db
                return apology("New password does not match password confirmation")
            hash_password = generate_password_hash(new_password)
            db.execute("UPDATE users SET  hash = ? WHERE id = ?", hash_password, session["user_id"])
            return render_template("success.html")

        else:
            return apology("Incorrect old Password")