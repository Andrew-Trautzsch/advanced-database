from flask import Flask, render_template, request, redirect, url_for

import database

database.initalize("pets.db")

app = Flask(__name__)

@app.route("/", methods=["GET"])
@app.route("/list", methods=["GET"])
def get_list():
    pets = database.get_pets()
    return render_template("list.html")
