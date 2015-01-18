__author__ = 'nah'

import pymongo


class SubmissionStore():
    """Stores submissions obtained from the Canvas API."""

    def __init__(self, db_host='localhost', db_port=27017):
        """Construct a submission store working with a mongodb server at the given location."""
        self.client = pymongo.MongoClient(db_host, db_port)


    def store_assignment_submissions(self, course_id, assignment_id, submissions):
        """
        Stores the given submissions in the database.

        :param course_id: The id of the course to store the submissions unders
        :param assignment_id:  The id of the assignment to store the assignments unders
        :param submissions: The submissions themselves, in JSON format. Can be a single submission or a collection
        """
        course_id = str(course_id)
        assignment_id = str(assignment_id)
        submissions_collection = self.client[course_id][assignment_id]
        submissions_collection.insert(submissions)


    def store_submission_attachments(self, course_id, submission, attachments):
        course_id = str(course_id)
        assignment_id = str(submission['assignment_id'])

        pass


    def get_submissions_to_mark(self, course_id, assignment_id):
        query = {'$or': [{'grade_matches_current_submission': False}, {'grade': None}]}
        return self.get_assignment_submissions(course_id, assignment_id, query)

    def get_assignment_submissions(self, course_id, assignment_id, query={}):
        """
        Retrieves submissions for the given course and assignment from the database. Additionally restricts assignments based on query.

        :param course_id: The course to fetch the submissions from.
        :param assignment_id: The assignment to fetch the submissions from.
        :param query: Restricts returned submissions to those matching this query
        :return: the matching submissions in JSON format.
        """
        course_id = str(course_id)
        assignment_id = str(assignment_id)

        return self.client[course_id][assignment_id].find(query)

