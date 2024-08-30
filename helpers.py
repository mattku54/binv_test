import jwt
import os

from datetime import datetime, timedelta
from flask_mail import Mail, Message
from flask import flash, redirect, render_template, session
from functools import wraps

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            flash("Login Required")
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def admin_login_required(f):
    """
    Decorate routes to require an admin login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None or session.get("user_role") != "admin":
            flash("Admin Login Required")
            return redirect("/admin_login")
        return f(*args, **kwargs)
    return decorated_function

def verify_reset_token(token):
    
    key=os.getenv('RESET_KEY_FLASK')
    print(f"{key}")

    # Decodes the token and verifies that the key is the same
    info = jwt.decode(token, key=os.getenv('RESET_KEY_FLASK'), algorithms="HS256")


    if info:
        return info
    return False
