from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/", methods=["GET"])
@app.route("/Hello/<name>", methods=["GET"])
def get_index(name = "World"):
    # return f"<html><h1>Hello {name}!<html>"
    return render_template("hello.html", name=name)

@app.route("/Bye", methods=["GET"])
def get_bye():
    return "Goodbye World!"

@app.route("/list", methods=["GET"])
def get_list():
    list = ["a","b","c"]
    return render_template("list.html", list=list)
