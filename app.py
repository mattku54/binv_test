from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from admin_bp import bp as admin_bp
from student_bp import bp as student_bp
import re
import os
import sqlite3

from db_helpers import confirm_query_exists, extract_query_info
from helpers import login_required, send_reset_email, verify_reset_token

# Configure application
app = Flask(__name__)

# Register blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(student_bp)

# Configure session to use filesystem (instead of signed cookies), also logs user out after 1 hour
app.config["SESSION_PERMANENT"] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours = 1)
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Global variables
now = datetime.now()
db_name = "inventory"

@app.route("/")
@login_required
def index():
    return redirect("/success")

@app.route("/register", methods=["GET", "POST"])
def register():
    # If user has submitted registration info
    if request.method == "POST":
        # Input parameters from the form
        pcc_id = request.form.get("id")
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')

        # For queries, we're going to select from the "students" table
        table = "students"

        # Check that the user filled in every spot on the form
        if not pcc_id or not fname or not lname or not password or not confirmation or not email:
            flash("Please fill in every spot on the form")
            return render_template("register.html")

        # Check that pcc_id is valid
        if not pcc_id.isdigit() and len(pcc_id) != 8:
            flash("Invalid PCC ID")
            return render_template("register.html")

        # Check to see if it's a valid email
        if not re.match(r"[^@]+@[^@]+.[^@]", email):
            flash("Please put in a valid email address")
            return render_template("register.html")

        # Query the db to see if user has already registered or email is being used
        id_query = {"pcc_id": f"{pcc_id}"}
        email_query = {"email" : f"{email}"}

        if confirm_query_exists(db_name, table, id_query):
            flash("You've already registered, try to remember your pw")
            return render_template("register.html")

        if confirm_query_exists(db_name, table, email_query):
            flash("Email is already in use")
            return render_template("register.html")

        # Confirm that password and confirmation are the same...if so, hash the password
        if password != confirmation:
            flash("Password and confirmation must be the same")
            return render_template("register.html")
        else:
            hash_password = generate_password_hash(password)

        # Save the student information
        with sqlite3.connect(f"{db_name}.db") as db:
            try:
                db.execute("INSERT INTO students (pcc_id, FirstName, LastName, hash_password, email) VALUES (?,?,?,?,?)", (pcc_id, fname, lname, hash_password, email,))
            except sqlite3.Error as e:
                print(f"An error occurred: {e}")
                return False

        # Confirm that the id was added
        if confirm_query_exists(db_name, table, id_query):
            flash("Registration successful")
            return render_template("login.html")
        else:
            flash("Registration Unsuccessful...you may have already registered or the email address is already in use")
            return render_template("register.html")

    # If method is "GET" or user is still logging in
    else:
        return render_template("register.html")

@app.route("/admin_register", methods=["GET", "POST"])
def admin_register():
    # If user has submitted registration info
    if request.method == "POST":
        # User input parameters
        pcc_id = request.form.get("id")
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')
        admin_key = request.form.get("admin_key")

        # For queries, we're going to select from the "admins" table
        table = "admins"

        # Check to see that user has the correct admin password
        if admin_key != os.getenv("ADMIN_KEY"):
            flash ("Incorrect admin password")
            return render_template("admin_register.html")

        # Check that the user filled in every spot on the form
        if not pcc_id or not fname or not lname or not password or not confirmation:
            flash("Please fill in every spot on the form")
            return render_template("admin_register.html")

        # Check that pcc_id is valid
        if not pcc_id.isdigit() and len(pcc_id) != 8:
            flash("Invalid PCC ID")
            return render_template("admin_register.html")

        # Check to see if it's a valid email
        if not re.match(r"[^@]+@[^@]+.[^@]", email):
            flash("Please put in a valid email address")
            return render_template("admin_register.html")

        # Confirm that password and confirmation are the same...if so, hash the password
        if password != confirmation:
            flash("Password and confirmation must be the same")
            return render_template("admin_register.html")
        else:
            hash_password = generate_password_hash(password)

        # Query the db to see if user has already registered or email is being used
        id_query = {"pcc_id": f"{pcc_id}"}
        email_query = {"email" : f"{email}"}

        if confirm_query_exists(db_name, table, id_query):
            flash("You've already registered, try to remember your pw")
            return render_template("admin_register.html")

        if confirm_query_exists(db_name, table, email_query):
            flash("Email is already in use")
            return render_template("register.html")

        # Save the admins information
        with sqlite3.connect(f"{db_name}.db") as db:
            try:
                db.execute("INSERT INTO admins (pcc_id, FirstName, LastName, hash_password, email) VALUES (?,?,?,?,?)", (pcc_id, fname, lname, hash_password, email,))
            except sqlite3.Error as e:
                flash(f"Database error: {e}")
                return render_template("admin_register.html")


        # Confirm that it worked
        if confirm_query_exists(db_name, table, id_query):
            flash("Registration successful!")
            return render_template("admin_login.html")
        else:
            flash("Registration Unsuccessful...you may have already registered or the email address is already in use")
            return render_template("admin_register.html")

    # If method is "GET" or user is still logging in
    else:
        return render_template("admin_register.html")

@app.route("/login", methods = ["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()

    # Log user in, handle admin login as well
    if request.method == "POST":
        # Ensure pcc_id and pw was submitted
        email = request.form.get("email")
        password = request.form.get("password")

        if not email:
            flash("Must provide email")
            return render_template("login.html")

        if not password:
            flash("Must provide password")
            return render_template("login.html")

        # Query database for id
        with sqlite3.connect(f"{db_name}.db") as db:
            try:
                cursor = db.execute("SELECT * FROM students WHERE email = ?", (email,))
            except sqlite3.Error as e:
                flash(f"Database error, {e}")
                return render_template ("login.html")

        check = cursor.fetchall()
        cursor.close()

        # Ensure id exists and is the only one
        if len(check) != 1:
            flash ("Invalid email and/or password")
            return render_template("login.html")

        if not check_password_hash(check[0][3], password):
            flash ("Incorrect Password")
            return render_template("login.html")

        # Remember which user has logged in and give role assignment
        session["user_id"] = check[0][0]
        session["user_role"] = "student"

        # Redirect user to home page
        return redirect("/")
    return render_template("login.html")

@app.route("/admin_login", methods = ["GET", "POST"])
def admin_login():
    # Forget any user_id
    session.clear()

    # Log admin user in
    if request.method == "POST":
        # Ensure pcc_id and pw was submitted
        email = request.form.get("email")
        password = request.form.get("password")

        if not email:
            flash("Must provide email")
            return render_template("admin_login.html")

        if not password:
            flash("Must provide password")
            return render_template("admin_login.html")

        # Query database for id
        with sqlite3.connect(f"{db_name}.db") as db:
            try:
                cursor = db.execute("SELECT * FROM admins WHERE email = ?", (email,))
                check = cursor.fetchall()
                cursor.close()

            except sqlite3.Error as e:
                flash(f"Email Check Database error, {email}, {e}")
                return render_template ("admin_login.html")

        # Ensure id exists in the database
        if len(check) != 1:
            flash(f"User not found or multiple users with same info")
            return render_template("admin_login.html")

        # Ensure id exists and password is correct
        if not check_password_hash(check[0][3], password):
            flash (f"Incorrect password, query returned {check[0][4]}")
            return render_template("admin_login.html")

        # Remember which user has logged in and assign admin user role
        session["user_id"] = check[0][0]
        session["user_role"] = "admin"

        # Redirect user to home page
        return redirect("/")
    return render_template("admin_login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")

@app.route("/success")
@login_required
def successful():
    role = session["user_role"]
    id = session["user_id"]

    if role == "admin":
        table = "admins"
    else:
        table = "students"

    id_query = {"pcc_id": f"{id}"}
    name = extract_query_info(db_name, table, id_query, "FirstName")
    return render_template("success.html", name=name, role=role)

# User will submit an email and have reset link sent to email addy
@app.route("/reset", methods = ["GET", "POST"])
def reset():
    # If a new password is entered, v
    if request.method == "POST":
        email = request.form.get("email")
        table = request.form.get("role")

        if not email:
            flash("Must enter email")
            return redirect("reset.html")

        if table != "admin" or table != "students":
            flash("Invalid role")
            return redirect("reset.html")

        # Query database to confirm email
        email_query = {"email":f"{email}"}

        if confirm_query_exists(db_name, table, email_query):
            # Send a password reset email
            flash(f"An email has been sent to {email} with a password reset link")
            send_reset_email(email, table)
            return redirect("login.html")

        flash(f"An account with email:{email} has not been found, please check for typos in your email addy")
        return redirect("reset.html")

    # On a 'GET' request, reset.html will just contain a form to input email
    return render_template("reset.html")

@app.route("/reset_verified", methods = ["GET", "POST"])
def reset_verify(token):
    # Change the password for the email
    if request.method == "POST":
        info = verify_reset_token(token)

        if not info:
            flash("Invalid or expired token, please request reset email again")
            return redirect('reset.html')

        email = info['email']
        role = info['role']

        if role != "admin" or role != "students":
            flash("Invalid role")
            return redirect("reset.html")

        new_password = request.form.get("password")
        hash_newpassword = generate_password_hash(new_password)

        with sqlite3.connect(f"{db_name}.db") as db:
            try:
                if role == 'admin':
                    db.execute("UPDATE admin SET hash_password = ? WHERE email = ?", (hash_newpassword, email,))
                if role == 'students':
                    db.execute("UPDATE students SET hash_password = ? WHERE email = ?", (hash_newpassword, email,))
            except sqlite3.Error as e:
                flash(f"Update error: {e}")
                return redirect('reset_verified.html')
            db.commit()
            db.close()
        flash("Password successfully reset")
        return redirect("login.html")

    return render_template("reset_verified.html")

