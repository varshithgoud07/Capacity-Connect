from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import cloudinary
import cloudinary.uploader
from config import SECRET_KEY
from database import get_connection, create_tables
from ai_resume import extract_resume_text, analyze_resume

app = Flask(__name__)
app.secret_key = SECRET_KEY

cloudinary.config(
    secure=True
)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

create_tables()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        email=request.form["email"]
        password=request.form["password"]
        conn=get_connection()
        cur=conn.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()

        cur.close()
        conn.close()

        if user and check_password_hash(user[3], password):  
            session["name"]=user[1]
            session["email"]=user[2]
            return redirect(url_for("dashboard"))
        flash("Invalid Email or Password!")
        return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():

    if "email" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT resume FROM users WHERE email=%s",
        (session["email"],)
    )

    result = cur.fetchone()

    cur.close()
    conn.close()

    resume = result[0] if result else None

    return render_template(
        "dashboard.html",
        name=session["name"],
        resume=resume
    )

@app.route("/profile")
def profile():
    if "email" not in session:
        return redirect(url_for("login"))
    conn=get_connection(); cur=conn.cursor()
    cur.execute("SELECT name,email,phone,branch,year,skills FROM users WHERE email=%s",(session["email"],))
    user=cur.fetchone()
    cur.close(); conn.close()
    return render_template("profile.html",
        name=user[0],email=user[1],phone=user[2],branch=user[3],year=user[4],skills=user[5])

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        conn = get_connection()
        cur = conn.cursor()

        # Check if email already exists
        cur.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        existing_user = cur.fetchone()

        if existing_user:
            cur.close()
            conn.close()

            flash("An account with this email already exists. Please login.")
            return redirect(url_for("login"))

        cur.execute(
            "INSERT INTO users(name,email,password) VALUES(%s,%s,%s)",
            (name, email, hashed_password)
        )

        conn.commit()
        cur.close()
        conn.close()

        flash("Registration successful! Please login.")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/update_profile",methods=["POST"])
def update_profile():
    if "email" not in session:
        return redirect("/login")
    conn=get_connection(); cur=conn.cursor()
    cur.execute("""UPDATE users SET phone=%s,branch=%s,year=%s,skills=%s WHERE email=%s""",
        (request.form["phone"],request.form["branch"],request.form["year"],request.form["skills"],session["email"]))
    conn.commit(); cur.close(); conn.close()
    return redirect("/profile")

@app.route("/upload_resume", methods=["POST"])
def upload_resume():

    if "email" not in session:
        return redirect("/login")

    file = request.files["resume"]

    if file.filename == "":
        flash("No file selected.")
        return redirect("/dashboard")

    try:
        # Upload to Cloudinary as a raw file (PDF, DOC, DOCX)
        import uuid
        result = cloudinary.uploader.upload(
            file,
            resource_type="raw",
            folder="capacity_connect/resumes",
            public_id=session["email"].replace("@", "_").replace(".", "_")
        )

        resume_url = result["secure_url"]

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "UPDATE users SET resume=%s WHERE email=%s",
            (resume_url, session["email"])
        )

        conn.commit()
        cur.close()
        conn.close()

        flash("Resume uploaded successfully!")

    except Exception as e:
        flash(f"Upload failed: {e}")

    return redirect("/dashboard")
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))
@app.route("/test_resume")
def test_resume():

    if "email" not in session:
        return redirect("/login")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT resume FROM users WHERE email=%s",
        (session["email"],)
    )

    result = cur.fetchone()

    cur.close()
    conn.close()

    if not result or not result[0]:
        return "No resume found."

    text = extract_resume_text(result[0])

    return f"<pre>{text}</pre>"
@app.route("/resume_analysis")
def resume_analysis():

    if "email" not in session:
        return redirect("/login")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT resume FROM users WHERE email=%s",
        (session["email"],)
    )

    result = cur.fetchone()

    cur.close()
    conn.close()

    if not result or not result[0]:
        return "No resume uploaded."

    resume_text = extract_resume_text(result[0])

    if not resume_text:
        return "Could not read the resume."

    analysis = analyze_resume(resume_text)

    return render_template(
       "resume_analysis.html",
        analysis=analysis,
        name=session["name"]
    )
if __name__=="__main__":
    app.run(debug=True)
