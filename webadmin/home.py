from webadm import app
from flask import render_template
from user import auth_required


@app.route('/')
@auth_required
def home():
    return render_template('index.html')
