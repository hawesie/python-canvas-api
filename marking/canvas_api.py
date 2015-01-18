__author__ = 'nah'

import requests


class CanvasAPI():
    """"""

    def __init__(self, access_token, base_url='https://canvas.bham.ac.uk', api_prefix='/api/v1'):
        """Construct an object to access the Canvas API. """
        self.access_token = access_token
        self.api_url = base_url + api_prefix

    def get(self, api):
        url = self.api_url + api

        if self.access_token is not None:
            payload = {'access_token': self.access_token}
            r = requests.get(url, params=payload)
        else:
            r = requests.get(url)

        # raises an exception if there was an http error
        r.raise_for_status()

        return r


    def get_courses(self):
        return self.get('/courses').json()

    def get_assignments(self, course_id):
        return self.get('/courses/%s/assignments' % course_id).json()

    def get_quiz_submissions(self, course_id, quiz_id):
        return self.get('/courses/%s/quizzes/%s/submissions' % (course_id, quiz_id))

    def get_assignment_submissions(self, course_id, assignment_id):
        return self.get('/courses/%s/assignments/%s/submissions' % (course_id, assignment_id)).json()
