from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from werkzeug.utils import secure_filename

from config import SECRET_KEY
from database import get_connection, create_tables

app = Flask(__name__)
app.secret_key = SECRET_KEY

# ------------------------
# Upload Folder
# ------------------------

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

create_tables()


# ------------------------
# Home
# ------------------------

@app.route("/")
def home():
    return render_template("index.html")


# ------------------------
# Login
# ------------------------

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

            flash("Welcome back!")
            return redirect(url_for("dashboard"))

        flash("Invalid Email or Password")
        return redirect(url_for("login"))

    return render_template("login.html")


# ------------------------
# Dashboard
# ------------------------

@app.route("/dashboard")
def dashboard():

    if "email" not in session:
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        name=session["name"]
    )


# ------------------------
# Profile
# ------------------------

@app.route("/profile")
def profile():

    if "email" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT name,email,phone,branch,year,skills
        FROM users
        WHERE email=?
        """,
        (session["email"],)
    )

    user = cursor.fetchone()
    conn.close()

    if not user:
        flash("User not found.")
        return redirect("/dashboard")

    return render_template(
        "profile.html",
        name=user[0],
        email=user[1],
        phone=user[2],
        branch=user[3],
        year=user[4],
        skills=user[5]
    )


# ------------------------
# Register
# ------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                INSERT INTO users(name,email,password)
                VALUES(?,?,?)
                """,
                (name, email, password)
            )

            conn.commit()

            flash("Registration Successful! Please Login.")

            return redirect(url_for("login"))

        except Exception:

            flash("Email already exists!")

            return redirect(url_for("register"))

        finally:
            conn.close()

    return render_template("register.html")


# ------------------------
# Update Profile
# ------------------------

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

    cursor.execute(
        """
        UPDATE users
        SET phone=?,
            branch=?,
            year=?,
            skills=?
        WHERE email=?
        """,
        (
            phone,
            branch,
            year,
            skills,
            session["email"]
        )
    )

    conn.commit()
    conn.close()

    flash("Profile Updated Successfully!")

    return redirect("/profile")


# ------------------------
# Resume Upload
# ------------------------

@app.route("/upload_resume", methods=["POST"])
def upload_resume():

    if "email" not in session:
        return redirect("/login")

    file = request.files.get("resume")

    if file is None or file.filename == "":
        flash("Please select a resume.")
        return redirect("/dashboard")

    filename = secure_filename(file.filename)

    file.save(
        os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )
    )

    flash("Resume Uploaded Successfully!")

    return redirect("/dashboard")


# ------------------------
# Logout
# ------------------------

@app.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully!")

    return redirect(url_for("login"))


# ------------------------
# Run App
# ------------------------

if __name__ == "__main__":
    app.run(debug=True)