__author__ = 'nah'

import pymongo


class SubmissionStore():
    """Stores submissions obtained from the Canvas API."""

    def __init__(self, db_host='localhost', db_port=27017):
        """Construct a submission store working with a mongodb server at the given location."""
        self.client = pymongo.MongoClient(db_host, db_port)
        self.users_collection = self.client['users']['users']
        self.users_collection.ensure_index('user_id')

    def _store_single_submission(self, collection, submission):
        # assumption is that there can only be one submission per user in the collection
        collection.update({'user_id': submission['user_id']}, submission, upsert=True)


    def store_assignment_submissions(self, course_id, assignment_id, submissions):
        """
        Stores the given submissions in the database.

        :param course_id: The id of the course to store the submissions unders
        :param assignment_id:  The id of the assignment to store the assignments unders
        :param submissions: The submissions themselves, in JSON format. Can be a single submission or an iterable
        """
        course_id = str(course_id)
        assignment_id = str(assignment_id)
        submissions_collection = self.client[course_id][assignment_id]

        try:
            for submission in submissions:
                self._store_single_submission(submissions_collection, submission)
        except TypeError, te:
            self._store_single_submission(submissions_collection, submissions)



    def store_submission_attachments(self, course_id, submission, attachments):
        course_id = str(course_id)
        assignment_id = str(submission['assignment_id'])


    def get_submissions_to_mark(self, course_id, assignment_id):
        query = {'$or': [{'grade_matches_current_submission': False}, {'grade': None}]}
        return self.get_assignment_submissions(course_id, assignment_id, query)

    def get_stored_submission(self, course_id, assignment_id, user_id):
        query = {'user_id': user_id}
        result = self.get_assignment_submissions(course_id, assignment_id, query)
        if result.count() > 0:
            return result[0]
        else:
            return None


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

    def store_user(self, user):
        self.users_collection.update({'id': user['id']}, user, upsert=True)

    def get_username(self, uid):
        user = self.users_collection.find_one({'id': uid})
        if user is None:
            return None
        else:
            return user['login_id']