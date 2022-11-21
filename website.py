from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for
import python_avatars as pa

#ENV_FILE = find_dotenv()
#if ENV_FILE:
    #load_dotenv(ENV_FILE)

app = Flask(__name__)
#app.

@app.route("/")
def home():
    return "<p>This is the home page</p>"

@app.route("/login")
def login():
    return "<p>This is the login page</p>"

@app.route("/avatar")
def avatar():
    randomAvatar = pa.Avatar.random()
    randomAvatar.render("static/avatar.svg")
    return render_template("avatar.html", avatar = "static/avatar.svg")