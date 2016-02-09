
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

Then you need to add the `src` directory to your `PYTHONPATH` and the `scripts` directory to your `PATH` (or execute them directly).

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

The **first time** you use this framework you need to generate a new API key to give you access to Canvas. To do this go to your Canvas Profile page and then go to Settings. From here you should click "New access token". Generate the token and copy the key. Then running the following. This will store the token in the database so you can use it in future.

```bash
store_token.py <token>
```

With this in place you can see what courses you have access to on Canvas:

```bash
$ list_courses.py 
https://canvas.bham.ac.uk/api/v1/courses
Courses:
4458: PGCARMS Public Engagement module
5769: Test Module
15668: LC Robot Programming
4945: Turnitin Test Module
15693: LH Individual Study 1
16318: LC Software Workshop 1
15699: Computer Science Project
7787: Research Data Management
16042: MSc. Robotics
9967: Chemical Engineering Home Canvas Page 2014-15
15669: Personal Tutors
```

The number at the start of the line is the `course_id` you'll use when talking to the API about a particular course. 

I can use this to see the assignments available for a particular course:

```bash
$ list_assignments.py 15668
https://canvas.bham.ac.uk/api/v1/courses/15668/assignments
Assignments:
40939: Team Assignment 0: Get Your Kit... ([u'not_graded'])
50597: Team Assignment 1: Movement and Control ([u'online_upload'])
51113: Team Assignment 2: Feedback and Friends ([u'online_upload'])
51114: Team Assignment 3: An Autonomous Warehouse ([u'none'])
50340: Individual Assignment 1: Movement and Control ([u'online_upload'])
51115: Team Preferences for the Autonomous Warehouse Assignment ([u'online_quiz'], quiz_id: 25653)
```

The number at the start of the line is the `assignment_id` you'll use when talking to the API about a particular assignment on the course. 

To be able to associate students with usernames and assignments (from Canvas, which uses a few different types of IDs), it's wise to grab all the information on users from Canvas:

```bash
$ store_users.py 15668
https://canvas.bham.ac.uk/api/v1/courses/15668/users
Stored 178 users
```

You can verify what has been stored by using a MongoDB viewer such as [RoboMongo](https://robomongo.org).

## Export Submission Attachments

When a student submits a solution to an assignment, this creates a *submission*. If this involved a file upload or attachment this creates an additional *submission attachment*. One common use case is to export all the submission attachments for a particular assignment to disk. This is done with `export_submission_attachments.py <course_id> <assignment_id>`.

```bash
$ export_submission_attachments.py 16318 51032
https://canvas.bham.ac.uk/api/v1/courses/16318/assignments/51032/submissions
66 submissions retrieved from Canvas
39183 1/66
69024 2/66
72613 3/66
91122 4/66
92731 5/66
93964 6/66
94385 7/66
94545 8/66
95100 9/66
...
```

In this case the submissions and attachments are downloaded to the database, then the attachments are read back out and 