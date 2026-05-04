# Lecture 14: Installing MongoDB in a GitHub Codespace

This note walks through installing MongoDB Community Edition inside a GitHub Codespace, starting the server on a Linux Codespace machine, creating an administrative user, and creating an application user for a demo database named `pets_demo` with a `pets` collection.

This is a classroom setup, not a production deployment. We are aiming for correct, repeatable, and not needlessly theatrical.

## Goals

By the end, you should have:

- MongoDB Community Edition installed in the Codespace
- `mongod` running locally on `127.0.0.1:27017`
- an administrative user in the `admin` database
- an application user for `pets_demo`
- a `pets` collection with a few demo documents

## Before You Start

These instructions assume:

- the Codespace is Ubuntu-based
- you have `sudo`
- you are working in a normal GitHub Codespace terminal

Check the OS first:

```bash
cat /etc/os-release
```

You should see something like Ubuntu `22.04` or `24.04`.

## Why We Are Not Using `systemctl`

MongoDB's official Ubuntu install docs assume a more normal Linux machine with `systemd`. A GitHub Codespace is often closer to "container with opinions" than "full VM." That means `systemctl start mongod` is often the wrong move.

So we will:

- install MongoDB with `apt`
- create our own data directory
- start `mongod` manually
- enable authentication with a local config file

That is uglier than a polished service install, but also more likely to work in a Codespace, which is the point.

## Step 1: Install MongoDB Community Edition

Update package metadata and install the helper packages:

```bash
sudo apt-get update
sudo apt-get install -y gnupg curl
```

Import MongoDB's official public key for version `8.0`:

```bash
curl -fsSL https://www.mongodb.org/static/pgp/server-8.0.asc | \
  sudo gpg --dearmor -o /usr/share/keyrings/mongodb-server-8.0.gpg
```

Add the MongoDB repository for your Ubuntu codename:

```bash
. /etc/os-release
echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] https://repo.mongodb.org/apt/ubuntu ${VERSION_CODENAME}/mongodb-org/8.0 multiverse" | \
  sudo tee /etc/apt/sources.list.d/mongodb-org-8.0.list
```

Update package metadata again and install MongoDB:

```bash
sudo apt-get update
sudo apt-get install -y mongodb-org
```

Verify the binaries exist:

```bash
mongod --version
mongosh --version
```

## Step 2: Create a Local Data Directory

Make a place for MongoDB to store its data and logs:

```bash
mkdir -p ~/mongodb-data
mkdir -p ~/mongodb-data/log
```

## Step 3: Create a Minimal Config File

Create a file named `mongod-codespace.conf` in your home directory:

```yaml
storage:
  dbPath: /home/codespace/mongodb-data

systemLog:
  destination: file
  path: /home/codespace/mongodb-data/log/mongod.log
  logAppend: true

net:
  bindIp: 127.0.0.1
  port: 27017
```

If your Codespace username is not `codespace`, replace `/home/codespace` with the output of:

```bash
echo $HOME
```

## Step 4: Start MongoDB Without Authentication

Start the server:

```bash
mongod --config ~/mongod-codespace.conf --fork
```

Check that it is running:

```bash
ps -ef | grep mongod
mongosh --eval "db.runCommand({ ping: 1 })"
```

The `grep` command will, because the universe has a sense of humor, also show the `grep` process itself. Ignore that one.

## Step 5: Create the Initial Administrative User

Connect to MongoDB:

```bash
mongosh
```

Switch to the `admin` database:

```javascript
use admin
```

Create an admin user. For class, using the built-in `root` role is simple and effective:

```javascript
db.createUser({
  user: "siteAdmin",
  pwd: passwordPrompt(),
  roles: [
    { role: "root", db: "admin" }
  ]
})
```

Exit `mongosh`:

```javascript
exit
```

## Step 6: Enable Authentication

Edit `~/mongod-codespace.conf` so it includes a `security` section:

```yaml
storage:
  dbPath: /home/codespace/mongodb-data

systemLog:
  destination: file
  path: /home/codespace/mongodb-data/log/mongod.log
  logAppend: true

net:
  bindIp: 127.0.0.1
  port: 27017

security:
  authorization: enabled
```

Again, use your real home directory path if it is not `/home/codespace`.

Now shut MongoDB down cleanly:

```bash
mongosh --eval "db.getSiblingDB('admin').shutdownServer()"
```

Start it again with authentication enabled:

```bash
mongod --config ~/mongod-codespace.conf --fork
```

## Step 7: Log In as the Admin User

Connect as the admin user you just created:

```bash
mongosh -u siteAdmin --authenticationDatabase admin
```

It will prompt for the password.

Verify who you are:

```javascript
db.runCommand({ connectionStatus: 1 })
```

## Step 8: Create the Demo Database User

Now create a user for the demo database.

Switch to the demo database:

```javascript
use pets_demo
```

Create an application user with `readWrite` access to `pets_demo`:

```javascript
db.createUser({
  user: "petsApp",
  pwd: passwordPrompt(),
  roles: [
    { role: "readWrite", db: "pets_demo" }
  ]
})
```

This user is the one your demo app should use. It does not need the keys to the kingdom.

## Step 9: Create the `pets` Collection and Seed Some Data

Still in `pets_demo`, insert a few documents:

```javascript
db.pets.insertMany([
  {
    name: "Mochi",
    species: "cat",
    age: 3,
    adopted: true
  },
  {
    name: "Biscuit",
    species: "dog",
    age: 5,
    adopted: false
  },
  {
    name: "Dot",
    species: "rabbit",
    age: 2,
    adopted: true
  }
])
```

Verify the collection exists:

```javascript
show collections
db.pets.find().pretty()
```

## Step 10: Test the Database User

Exit the admin session:

```javascript
exit
```

Connect as the application user:

```bash
mongosh -u petsApp --authenticationDatabase pets_demo
```

After logging in, switch to the demo database and test a query:

```javascript
use pets_demo
db.pets.find()
```

Try an insert:

```javascript
db.pets.insertOne({
  name: "Pico",
  species: "parrot",
  age: 4,
  adopted: false
})
```

That should work because `petsApp` has `readWrite` on `pets_demo`.

## Step 11: Useful Commands

### Check whether MongoDB is running

```bash
ps -ef | grep mongod
```

### Stop MongoDB

If you are logged in as the admin:

```bash
mongosh -u siteAdmin --authenticationDatabase admin
```

Then:

```javascript
use admin
db.shutdownServer()
```

### Restart MongoDB

```bash
mongod --config ~/mongod-codespace.conf --fork
```

### Read the log

```bash
tail -n 50 ~/mongodb-data/log/mongod.log
```

## Step 12: What You Built

At this point you have:

- a local MongoDB server running in the Codespace
- an admin account named `siteAdmin`
- an application account named `petsApp`
- a database named `pets_demo`
- a collection named `pets`

That is enough to support a classroom demo app, test queries in `mongosh`, and start building a Flask or Node app against a real MongoDB instance.

## Common Problems

### `systemctl` does not work

That is normal in many Codespaces. Use `mongod --config ... --fork` instead.

### `mongod` will not start

Check the log:

```bash
tail -n 100 ~/mongodb-data/log/mongod.log
```

Also verify:

- the `dbPath` directory exists
- the log directory exists
- the home directory path in the config file is correct

### Authentication suddenly blocks everything

That usually means:

- authentication is enabled
- you did not log in as `siteAdmin`
- or you created the first user incorrectly

Log in explicitly with:

```bash
mongosh -u siteAdmin --authenticationDatabase admin
```

### You forgot your passwords

That is less a database issue and more an organic storage issue. For class, document the usernames and passwords in a secure place you actually control.

## Recommended User Summary

Use something like this:

- admin user: `siteAdmin`
- admin auth DB: `admin`
- app user: `petsApp`
- app auth DB: `pets_demo`
- app database: `pets_demo`
- collection: `pets`

## References

These instructions were adapted from the official MongoDB documentation:

- [Install MongoDB Community Edition on Ubuntu](https://www.mongodb.com/docs/v8.0/tutorial/install-mongodb-on-ubuntu/)
- [db.createUser()](https://www.mongodb.com/docs/current/reference/method/db.createUser/)
- [Role-Based Access Control in Self-Managed Deployments](https://www.mongodb.com/docs/manual/core/authorization/)
- [Localhost Exception in Self-Managed Deployments](https://www.mongodb.com/docs/rapid/core/localhost-exception/)
