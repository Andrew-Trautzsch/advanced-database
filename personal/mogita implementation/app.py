from flask import Flask, render_template, request, redirect, url_for
import database

# remember to $ pip install flask
# remember to $ pip install peewee

database.initialize("pets")

app = Flask(__name__)


def error_page(message, status=400):
    # Simple text response page, as requested.
    return message, status, {"Content-Type": "text/plain; charset=utf-8"}


@app.route("/", methods=["GET"])
@app.route("/list", methods=["GET"])
def get_list():
    pets = database.get_pets()
    return render_template("list.html", pets=pets)


@app.route("/create", methods=["GET"])
def get_create():
    return render_template("create.html")


@app.route("/create", methods=["POST"])
def post_create():
    data = dict(request.form)
    name = (data.get("name") or "").strip()
    pet_type = (data.get("type") or "").strip()
    if name == "":
        return error_page("Error: name is required.", 400)
    if pet_type == "":
        return error_page("Error: type is required.", 400)

    database.create_pet(data)
    return redirect(url_for("get_list"))


@app.route("/delete/<id>", methods=["GET"])
def get_delete(id):
    database.delete_pet(id)
    return redirect(url_for("get_list"))


@app.route("/update/<id>", methods=["GET"])
def get_update(id):
    data = database.get_pet(id)
    if data is None:
        return error_page("Error: pet not found.", 404)
    return render_template("update.html", data=data)


@app.route("/update/<id>", methods=["POST"])
def post_update(id):
    data = dict(request.form)
    name = (data.get("name") or "").strip()
    pet_type = (data.get("type") or "").strip()
    if name == "":
        return error_page("Error: name is required.", 400)
    if pet_type == "":
        return error_page("Error: type is required.", 400)

    database.update_pet(id, data)
    return redirect(url_for("get_list"))


@app.route("/health", methods=["GET"])
def health():
    try:
        database.get_pets()
        return error_page("ok", 200)
    except Exception as e:
        return error_page(f"Error checking health: {e}", 500)
