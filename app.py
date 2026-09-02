from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

from config import SECRET_KEY, DATABASE
from database import get_connection, create_tables

app = Flask(__name__)
app.secret_key = SECRET_KEY
create_tables()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )

        user = cursor.fetchone()

        conn.close()


        if user:

           session["name"] = user[1]
           session["email"] = user[2]

           return redirect(url_for("dashboard"))

        else:
            return "<h2>Invalid Email or Password</h2>"

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():

    if "email" not in session:
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        name=session["name"]
    )


@app.route("/profile")
def profile():

    if "email" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name, email, phone, branch, year, skills FROM users WHERE email=?",
        (session["email"],)
    )

    user = cursor.fetchone()

    print("Session email:", session["email"])
    print("Database result:", user)

    conn.close()

    return render_template(
       "profile.html",
       name=user[0],
       email=user[1],
       phone=user[2],
       branch=user[3],
       year=user[4],
       skills=user[5]
    )
@app.route("/logout")
def logout():

    session.pop("name", None)
    session.pop("email", None)

    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users(name,email,password) VALUES(?,?,?)",
            (name, email, password)
        )

        conn.commit()
        conn.close()

        return "<h2>Registration Successful!</h2>"

    return render_template("register.html")


@app.route("/update_profile", methods=["POST"])
def update_profile():

    if "email" not in session:
        return redirect("/login")

    phone = request.form["phone"]
    branch = request.form["branch"]
    year = request.form["year"]
    skills = request.form["skills"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE users
    SET phone=?, branch=?, year=?, skills=?
    WHERE email=?
    """, (phone, branch, year, skills, session["email"]))

    conn.commit()
    conn.close()

    return redirect("/profile")
if __name__ == "__main__":
    app.run(debug=True)