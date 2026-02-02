from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from pprint import pprint

connection = sqlite3.connect("pets.db", check_same_thread=False)
print("succeeded in making connection.")

app = Flask(__name__)

@app.route("/", methods=["GET"])
@app.route("/Hello/<name>", methods=["GET"])
def get_index(name = "World"):
    # return f"<html><h1>Hello {name}!<html>"
    return render_template("hello.html", name=name)

@app.route("/Bye", methods=["GET"])
def get_bye():
    return "Goodbye World!"

@app.route("/pets", methods=["GET"])
def get_pets():
    # list = ["a","b","c"]
    # return render_template("list.html", list=list)
    cursor = connection.execute("select * from pet")
    rows = cursor.fetchall()
    pprint(rows)
    return render_template("pets.html", pets=rows)

@app.route("/create", methods=["GET"])
def get_create():
    return render_template("create.html")

@app.route("/create", methods=["POST"])
def post_create():
    data = dict(request.form)
    cursor = connection.execute("insert into pet (name, kind, age, food) values (?, ?, ?, ?)", (data["name"],data["kind"],data["age"],data["food"]))
    rows = cursor.fetchall()
    connection.commit()
    return redirect(url_for("get_pets"))

@app.route("/delete/<id>", methods=["GET"])
def get_delete(id):
    id = int(id)
    cursor = connection.execute("delete from pet where id==?", (id))
    rows = cursor.fetchall()
    connection.commit()
    return render_template(url_for("get_pets"))