# Topic 13: Mongo Indexes

Topic 13 moves from basic Mongo storage to Mongo Atlas and introduces MongoDB indexes.

---

## Atlas Context

- topic 13 uses a live Mongo Atlas database
- the API is standard MongoDB via PyMongo
- indexes are created in the database, not in Flask templates
- we add them when the app sets up the collections

Atlas gives us a real MongoDB deployment, so index behavior matters.

---

## Why Indexes

- without an index, MongoDB may scan the whole collection
- with an index, MongoDB can narrow the search quickly
- indexes matter more as collections grow
- reads get faster, but writes have extra overhead

Indexes trade write cost for faster queries.

---

## App Queries To Support

In this app, the common lookups are:

- find pets by `_id`
- find owners by `_id`
- check whether an `owner_id` exists
- check whether pets still reference an owner
- list pets and owners in a predictable order

Those access patterns tell us what fields deserve indexes.

---

## Indexes For This App

Useful single-field indexes include:

- `owners.name`
- `pets.name`
- `pets.type`
- `pets.owner_id`

The most important one for the constraint logic is `pets.owner_id`.

---

## Creating An Index

```python
owners_collection.create_index("name")
pets_collection.create_index("name")
pets_collection.create_index("type")
pets_collection.create_index("owner_id")
```

MongoDB automatically keeps the `_id` index, so we do not create that one ourselves.

---

## Setup Function

```python
def setup_database(database_name="pets"):
    initialize(database_name)

    owners_collection.count_documents({})
    pets_collection.count_documents({})

    owners_collection.create_index("name")
    pets_collection.create_index("name")
    pets_collection.create_index("type")
    pets_collection.create_index("owner_id")
```

Create indexes during startup so the database is ready before the first real request.

---

## Example Constraint Query

```python
def delete_owner(id):
    object_id, _ = _require_existing_owner(id)
    pet = pets_collection.find_one({"owner_id": object_id})
    if pet is not None:
        raise ConstraintError(
            "Cannot delete this owner because they have pets."
        )

    owners_collection.delete_one({"_id": object_id})
```

The `pets.owner_id` index helps this check avoid a full scan.

---

## Sorting And Indexes

```python
def get_pets():
    return [pet_to_dict(pet) for pet in pets_collection.find().sort("name", 1)]


def get_owners():
    return [owner_to_dict(owner) for owner in owners_collection.find().sort("name", 1)]
```

Sorting on indexed fields is often cheaper than sorting after scanning everything.

---

## Tradeoffs

- faster reads
- extra storage for each index
- slower inserts and updates
- too many indexes can hurt performance instead of helping

Index the fields you actually query, not every field in every document.

---

## Atlas Workflow

- connect to Atlas with a MongoDB URI
- choose the database and collections
- create indexes once during setup
- verify them in Atlas or with `index_information()`
- keep the index list aligned with real query patterns

Atlas lets you inspect and manage indexes from the dashboard too.

---

## Key Takeaways

- Atlas uses real MongoDB indexing behavior
- `_id` is already indexed
- add indexes for fields used in filters and sorts
- `pets.owner_id` is central to the manual relationship checks
- create indexes as part of database setup, not ad hoc in route handlers