
This repository contains code for working with the Canvas v1 API and doing various teaching and marking related tasks. 

**WARNING**: This code is all still very much preliminary, probably quite buggy, and it's usefulness for different tasks will vary.

# Installation

This framework stores results locally using [MongoDB](https://www.mongodb.org), so you should have a MongoDB database running. Your OS's package manager probably has a binary for this (e.g. apt on Ubuntu, Homebrew on OS X), so install it and start it up with an empty database, e.g. 

```bash
mkdir -p ~/teaching/databases/2015_16
mongod --dbpath ~/teaching/databases/2015_16
```

You also need the following additional Python packages:

```bash
pip install requests pymongo==2.9.1 gitpython subprocess32 
```


# The Basics

The framework needs a lot more documentation, but there are three key parts to it:

1. The `marking.canvas_api.CanvasAPI` object acts as the interface to the Canvas API. Most methods require a `course_id` and many an `assignment_id` to describe the particular course and assignment you are working with. These methods typically make some kind of call to the Canvas v1 API via a Web service (using the Python Requests library) and return JSON documents.

2. The `marking.mongodb_store.SubmissionStore` object acts as an interface to a MongoDB database for storing assignment submissions and also related student information. Input and output is typically also done with JSON documents. 

3. The collection of `marking.*_actions.py` files which provide functionality for performing a range of actions on submissions. These include cloning git repositores (`git_actions.py`); working with the file system and running external process (`file_actions.py`); compiling and running java programs (`java_actions.py`); and wrapping other actions in functions to assess their output (`marking_actions.py`).


# Workflow

Start up your database (or ensure it's running), e.g. 

```bash
mongod --dbpath ~/teaching/databases/2015_16
```

The first time you use this framework you need to generate a new API key to give you access to Canvas. To do this go to your Canvas Profile page and then go to Settings. From here you should click "New access token". Generate the token and copy the key. Then running the following. This will store the token in the database so you can use it in future.

```bash
store_token.py <token>
```



