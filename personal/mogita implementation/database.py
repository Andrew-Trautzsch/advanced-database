import os

from mongita import MongitaClientDisk
from bson.objectid import ObjectId

client = None
db = None
collection = None

def initialize(db_name):
    global client, db, collection
    client = MongitaClientDisk()
    db = client[db_name]
    collection = db.pets

def _normalize_age(value):
    if value is None:
        return 0
    if isinstance(value, str) and value.strip() == "":
        return 0
    age = int(value)
    if age < 0:
        raise ValueError("Age must be non-negative.")
    return age

def pet_to_dict(pet):
    return {"id": pet.id, "name": pet.name, "type": pet.type, "age": pet.age}


def get_pets():
    pets = list(collection.find())
    for pet in pets:
        pet["id"] = str(pet["_id"])
    return pets

def get_pet(id):
    try:
        pet = collection.find_one({"_id": ObjectId(id)})
        if pet:
            pet["id"] = str(pet["_id"])
        return pet
    except:
        return None

def create_pet(data):
    name = (data.get("name") or "").strip()
    pet_type = (data.get("type") or "").strip()

    if name == "":
        raise ValueError("Pet name is required.")
    if pet_type == "":
        raise ValueError("Pet type is required.")

    pet_holder = {
        "name": name,
        "type": pet_type,
        "age": _normalize_age(data.get("age"))
    }
    result = collection.insert_one(pet_holder)
    return str(result.inserted_id)

def update_pet(id, data):
    name = (data.get("name") or "").strip()
    pet_type = (data.get("type") or "").strip()

    if name == "":
        raise ValueError("Pet name is required.")
    if pet_type == "":
        raise ValueError("Pet type is required.")

    collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {
            "name": name,
            "type": pet_type,
            "age": _normalize_age(data.get("age"))
        }}
    )


def delete_pet(id):
    collection.delete_one({"_id": ObjectId(id)})

def setup_test_database(db_file="test_pets"):
    initialize(db_file)

    collection.delete_many({})

    pets = [
        {"name": "dorothy", "type": "dog", "age": 9},
        {"name": "suzy", "type": "mouse", "age": 9},
        {"name": "casey", "type": "dog", "age": 9},
        {"name": "heidi", "type": "cat", "age": 15},
    ]
    for pet in pets:
        create_pet(pet)

    assert len(get_pets()) == 4
    print("test database created")


def test_get_pets():
    pets = get_pets()
    assert type(pets) is list
    assert len(pets) >= 1
    assert type(pets[0]) is dict
    for key in ["id", "name", "type", "age"]:
        assert key in pets[0]
    assert type(pets[0]["name"]) is str
    print("test_get_pets succeeded")


def test_create_pet_and_get_pet():
    new_id = create_pet({"name": "walter", "age": "2", "type": "mouse"})
    pet = get_pet(new_id)
    assert pet is not None
    assert pet["name"] == "walter"
    assert pet["age"] == 2
    assert pet["type"] == "mouse"
    print("test_create_pet_and_get_pet succeeded")


def test_update_pet():
    new_id = create_pet({"name": "temp", "age": 1, "type": "cat"})
    update_pet(new_id, {"name": "updated", "age": "8", "type": "dog"})
    pet = get_pet(new_id)
    assert pet is not None
    assert pet["name"] == "updated"
    assert pet["age"] == 8
    assert pet["type"] == "dog"
    print("test_update_pet succeeded")


def test_delete_pet():
    new_id = create_pet({"name": "delete_me", "age": 3, "type": "fish"})
    delete_pet(new_id)
    assert get_pet(new_id) is None
    print("test_delete_pet succeeded")


def test_rejects_empty_name():
    try:
        create_pet({"name": "", "type": "dog", "age": 1})
        assert False, "Expected ValueError for empty name"
    except ValueError as e:
        assert "name" in str(e).lower()
    print("test_rejects_empty_name succeeded")


def test_rejects_empty_type():
    try:
        create_pet({"name": "rex", "type": "", "age": 1})
        assert False, "Expected ValueError for empty type"
    except ValueError as e:
        assert "type" in str(e).lower()
    print("test_rejects_empty_type succeeded")


def test_rejects_negative_age():
    try:
        create_pet({"name": "rex", "type": "dog", "age": -1})
        assert False, "Expected ValueError for negative age"
    except ValueError as e:
        assert "age" in str(e).lower()
    print("test_rejects_negative_age succeeded")


if __name__ == "__main__":
    setup_test_database()
    test_get_pets()
    test_create_pet_and_get_pet()
    test_update_pet()
    test_delete_pet()
    test_rejects_empty_name()
    test_rejects_empty_type()
    test_rejects_negative_age()
    print("done.")