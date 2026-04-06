import os

from mongita import MongitaClientDisk
from bson.objectid import ObjectId

client = None
db = None
pets_collection = None
owners_collection = None


def initialize(db_name):
    global client, db, pets_collection, owners_collection
    client = MongitaClientDisk()
    db = client[db_name]
    pets_collection = db.pets
    owners_collection = db.owners


def _normalize_age(value):
    if value is None:
        return 0
    if isinstance(value, str) and value.strip() == "":
        return 0
    age = int(value)
    if age < 0:
        raise ValueError("Age must be non-negative.")
    return age


# ---------------------------------------------------------------------------
# Owners
# ---------------------------------------------------------------------------

def owner_to_dict(owner):
    return {
        "id": str(owner["_id"]),
        "name": owner["name"],
        "city": owner.get("city"),
        "type_of_home": owner.get("type_of_home"),
    }


def get_owners():
    owners = list(owners_collection.find())
    return sorted([owner_to_dict(o) for o in owners], key=lambda o: o["name"])


def get_owner(id):
    try:
        owner = owners_collection.find_one({"_id": ObjectId(id)})
        if owner is None:
            return None
        return owner_to_dict(owner)
    except Exception:
        return None


def create_owner(data):
    name = (data.get("name") or "").strip()
    if name == "":
        raise ValueError("Owner name is required.")

    owner = {
        "name": name,
        "city": (data.get("city") or "").strip() or None,
        "type_of_home": (data.get("type_of_home") or "").strip() or None,
    }
    result = owners_collection.insert_one(owner)
    return str(result.inserted_id)


def update_owner(id, data):
    name = (data.get("name") or "").strip()
    if name == "":
        raise ValueError("Owner name is required.")

    owners_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {
            "name": name,
            "city": (data.get("city") or "").strip() or None,
            "type_of_home": (data.get("type_of_home") or "").strip() or None,
        }}
    )


def delete_owner(id):
    # Enforce referential integrity: reject if owner has pets.
    pets = list(pets_collection.find({"owner_id": str(id)}))
    if pets:
        raise ValueError(
            "Cannot delete this owner because they have pets. "
            "Please delete their pets first."
        )
    owners_collection.delete_one({"_id": ObjectId(id)})


# ---------------------------------------------------------------------------
# Pets
# ---------------------------------------------------------------------------

def pet_to_dict(pet):
    owner = get_owner(pet.get("owner_id"))
    return {
        "id": str(pet["_id"]),
        "name": pet["name"],
        "type": pet["type"],
        "age": pet["age"],
        "owner_id": pet.get("owner_id"),
        "owner_name": owner["name"] if owner else None,
    }


def get_pets():
    pets = list(pets_collection.find())
    return sorted([pet_to_dict(p) for p in pets], key=lambda p: p["name"])


def get_pet(id):
    try:
        pet = pets_collection.find_one({"_id": ObjectId(id)})
        if pet is None:
            return None
        return pet_to_dict(pet)
    except Exception:
        return None


def create_pet(data):
    name = (data.get("name") or "").strip()
    pet_type = (data.get("type") or "").strip()
    owner_id = (data.get("owner_id") or "")
    if isinstance(owner_id, str):
        owner_id = owner_id.strip()

    if name == "":
        raise ValueError("Pet name is required.")
    if pet_type == "":
        raise ValueError("Pet type is required.")
    if owner_id == "":
        raise ValueError("owner_id is required.")

    # Enforce referential integrity: owner must exist.
    if get_owner(str(owner_id)) is None:
        raise ValueError(f"Owner with id {owner_id} does not exist.")

    pet = {
        "name": name,
        "type": pet_type,
        "age": _normalize_age(data.get("age")),
        "owner_id": str(owner_id),
    }
    result = pets_collection.insert_one(pet)
    return str(result.inserted_id)


def update_pet(id, data):
    name = (data.get("name") or "").strip()
    pet_type = (data.get("type") or "").strip()
    owner_id = (data.get("owner_id") or "")
    if isinstance(owner_id, str):
        owner_id = owner_id.strip()

    if name == "":
        raise ValueError("Pet name is required.")
    if pet_type == "":
        raise ValueError("Pet type is required.")
    if owner_id == "":
        raise ValueError("owner_id is required.")

    # Enforce referential integrity: owner must exist.
    if get_owner(str(owner_id)) is None:
        raise ValueError(f"Owner with id {owner_id} does not exist.")

    pets_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {
            "name": name,
            "type": pet_type,
            "age": _normalize_age(data.get("age")),
            "owner_id": str(owner_id),
        }}
    )


def delete_pet(id):
    pets_collection.delete_one({"_id": ObjectId(id)})


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def setup_test_database(db_name="test_pets"):
    initialize(db_name)
    pets_collection.delete_many({})
    owners_collection.delete_many({})

    owner_ids = {}
    for owner in [
        {"name": "greg", "city": "Portland", "type_of_home": "condo"},
        {"name": "david", "city": "Seattle", "type_of_home": "farm"},
    ]:
        owner_ids[owner["name"]] = create_owner(owner)

    for pet in [
        {"name": "dorothy", "type": "dog", "age": 9, "owner_id": owner_ids["greg"]},
        {"name": "suzy", "type": "mouse", "age": 9, "owner_id": owner_ids["greg"]},
        {"name": "casey", "type": "dog", "age": 9, "owner_id": owner_ids["greg"]},
        {"name": "heidi", "type": "cat", "age": 15, "owner_id": owner_ids["david"]},
    ]:
        create_pet(pet)

    assert len(get_pets()) == 4
    print("test database created")
    return owner_ids


def test_get_pets():
    pets = get_pets()
    assert type(pets) is list
    assert len(pets) >= 1
    assert type(pets[0]) is dict
    for key in ["id", "name", "type", "age", "owner_id", "owner_name"]:
        assert key in pets[0]
    assert type(pets[0]["name"]) is str
    print("test_get_pets succeeded")


def test_create_pet_and_get_pet(owner_ids):
    new_id = create_pet({"name": "walter", "age": "2", "type": "mouse", "owner_id": owner_ids["greg"]})
    pet = get_pet(new_id)
    assert pet is not None
    assert pet["name"] == "walter"
    assert pet["age"] == 2
    assert pet["type"] == "mouse"
    assert pet["owner_id"] == str(owner_ids["greg"])
    print("test_create_pet_and_get_pet succeeded")


def test_update_pet(owner_ids):
    new_id = create_pet({"name": "temp", "age": 1, "type": "cat", "owner_id": owner_ids["greg"]})
    update_pet(new_id, {"name": "updated", "age": "8", "type": "dog", "owner_id": owner_ids["david"]})
    pet = get_pet(new_id)
    assert pet is not None
    assert pet["name"] == "updated"
    assert pet["age"] == 8
    assert pet["type"] == "dog"
    assert pet["owner_id"] == str(owner_ids["david"])
    print("test_update_pet succeeded")


def test_delete_pet(owner_ids):
    new_id = create_pet({"name": "delete_me", "age": 3, "type": "fish", "owner_id": owner_ids["greg"]})
    delete_pet(new_id)
    assert get_pet(new_id) is None
    print("test_delete_pet succeeded")


def test_fk_rejects_bad_owner_id():
    try:
        create_pet({"name": "ghost", "age": 1, "type": "dog", "owner_id": "000000000000000000000000"})
        assert False, "Expected failure for non-existent owner, but insert succeeded."
    except ValueError as e:
        assert "owner" in str(e).lower()
    print("test_fk_rejects_bad_owner_id succeeded")


def test_delete_owner_restricted(owner_ids):
    try:
        delete_owner(owner_ids["greg"])
        assert False, "Expected delete restriction failure, but delete succeeded."
    except ValueError as e:
        assert "pets" in str(e).lower()
    print("test_delete_owner_restricted succeeded")


def test_delete_pet_then_delete_owner_succeeds():
    owner_id = create_owner({"name": "solo", "city": "Akron", "type_of_home": "house"})
    pet_id = create_pet({"name": "onepet", "age": 3, "type": "cat", "owner_id": owner_id})

    try:
        delete_owner(owner_id)
        assert False, "Expected delete restriction failure, but delete succeeded."
    except ValueError:
        pass

    delete_pet(pet_id)
    delete_owner(owner_id)
    assert get_owner(owner_id) is None
    print("test_delete_pet_then_delete_owner_succeeds succeeded")


def test_get_owners():
    owners = get_owners()
    assert type(owners) is list
    assert len(owners) >= 1
    assert type(owners[0]) is dict
    for key in ["id", "name", "city", "type_of_home"]:
        assert key in owners[0]
    print("test_get_owners succeeded")


def test_get_owner(owner_ids):
    owner = get_owner(owner_ids["david"])
    assert owner["name"] == "david"
    print("test_get_owner succeeded")


def test_create_owner():
    create_owner({"name": "santa", "city": "north pole", "type_of_home": "workshop"})
    owners = [o for o in get_owners() if o["name"] == "santa"]
    assert owners[0]["city"] == "north pole"
    assert owners[0]["type_of_home"] == "workshop"
    print("test_create_owner succeeded")


def test_update_owner(owner_ids):
    owner_id = owner_ids["david"]
    update_owner(owner_id, {"name": "dave", "city": "riverside", "type_of_home": "suburban"})
    owner = get_owner(owner_id)
    assert owner["name"] == "dave"
    assert owner["city"] == "riverside"
    assert owner["type_of_home"] == "suburban"
    print("test_update_owner succeeded")


def test_delete_owner():
    owners = [o for o in get_owners() if o["name"] == "santa"]
    owner_id = owners[0]["id"]
    delete_owner(owner_id)
    assert get_owner(owner_id) is None
    print("test_delete_owner succeeded")


def test_rejects_negative_age(owner_ids):
    try:
        create_pet({"name": "rex", "type": "dog", "age": -1, "owner_id": owner_ids["greg"]})
        assert False, "Expected ValueError for negative age"
    except ValueError as e:
        assert "age" in str(e).lower()
    print("test_rejects_negative_age succeeded")


if __name__ == "__main__":
    owner_ids = setup_test_database()
    test_get_pets()
    test_create_pet_and_get_pet(owner_ids)
    test_update_pet(owner_ids)
    test_delete_pet(owner_ids)
    test_fk_rejects_bad_owner_id()
    test_delete_owner_restricted(owner_ids)
    test_delete_pet_then_delete_owner_succeeds()
    test_get_owners()
    test_get_owner(owner_ids)
    test_create_owner()
    test_update_owner(owner_ids)
    test_delete_owner()
    test_rejects_negative_age(owner_ids)
    print("done.")