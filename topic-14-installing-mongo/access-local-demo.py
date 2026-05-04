import os

from pymongo import MongoClient


host = os.environ.get("MONGO_HOST", "127.0.0.1")
port = int(os.environ.get("MONGO_PORT", "27017"))
username = os.environ.get("MONGO_APP_USERNAME", "petsApp")
password = os.environ.get("MONGO_APP_PASSWORD", "user1")
auth_db = os.environ.get("MONGO_AUTH_DB", "pets_demo")
db_name = os.environ.get("MONGO_DB", "pets_demo")
uri = os.environ.get("MONGO_URI", "").strip()

if uri:
    client = MongoClient(uri)
elif password:
    client = MongoClient(
        host=host,
        port=port,
        username=username,
        password=password,
        authSource=auth_db,
    )
else:
    client = MongoClient(host=host, port=port)

db = client[db_name]

print("Ping:", db.command("ping"))
print("Collections:", db.list_collection_names())
print("Pets:")
for pet in db.pets.find():
    print(pet)
