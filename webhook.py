from flask import Blueprint, Flask, request, abort, redirect, render_template
import hmac
import hashlib
import os

# Configure the blueprint
bp = Blueprint('webhook', __name__)

# Match the github secret
GITHUB_SECRET='t9fF[a=g4x$GDu]'

def verify_signature(request):
    signature = request.headers.get('X-Hub-Signature-256')
    if not signature:
        return False
    sha_name, signature = signature.split('=')
    if sha_name != 'sha256':
        return False
    
    digest = hmac.new(GITHUB_SECRET.encode(), request.data, hashlib.sha256.hexdigest())

    return hmac.compare_digest(digest, signature)

@bp.route("/webhook", methods = ["POST"])
def github_webhook():
    if not verify_signature(request):
        return abort(400, 'Invalid Signature')
    
    # Run script to pull the commit and restart the server
    os.system('/home/ec2-user/binv_test/.git/hooks/post-receive')
    
    return 'Webhook received', 200