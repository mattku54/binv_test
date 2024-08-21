import csv
import datetime
import pytz
import requests
import subprocess
import urllib
import uuid
import jwt
import os

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

def send_reset_email(email, role):
    """
    Send a password reset email

    """
    token = jwt.encode({'email':f"{email}",
                       'exp': datetime.time() + 500},
                       key = os.getenv('RESET_KEY_FLASK'))
    msg = Message()
    msg.subject = "Binventory App Password Reset"
    msg.sender = os.getenv('RESET_USERNAME')
    msg.recipients = email
    msg.html = render_template('reset_email.html', email=email, role=role, token=token)

    Mail.send(msg)

    return

def verify_reset_token(token):
    # Decodes the token and verifies that the key is the same
    info = jwt.decode(token, key=os.getenv('RESET_KEY_FLASK'))

    if info:
        return info
    return False
