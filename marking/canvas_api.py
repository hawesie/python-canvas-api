__author__ = 'nah'

import itertools

import requests


class CanvasAPI():
    """"""

    def __init__(self, access_token, base_url='https://canvas.bham.ac.uk', api_prefix='/api/v1'):
        """Construct an object to access the Canvas API. """
        self.access_token = access_token
        self.api_url = base_url + api_prefix

    def get_response(self, url):
        if self.access_token is not None:
            payload = {'access_token': self.access_token}
            r = requests.get(url, params=payload)
        else:
            r = requests.get(url)

        # raises an exception if there was an http error
        r.raise_for_status()
        return r

    def get_responses(self, api):
        url = self.api_url + api

        responses = []
        while True:

            r = self.get_response(url)
            responses.append(r)

            if 'next' in r.links:
                url = r.links['next']['url']
            else:
                break

        return responses


    def get(self, api, to_json=True):

        responses = self.get_responses(api)
        if to_json:
            responses = [r.json() for r in responses]

        return reduce(lambda x, y: itertools.chain(x, y), responses)


    def get_courses(self):
        return self.get('/courses')

    def get_assignments(self, course_id):
        return self.get('/courses/%s/assignments' % course_id)

    def get_quiz_submissions(self, course_id, quiz_id):
        return self.get('/courses/%s/quizzes/%s/submissions' % (course_id, quiz_id))

    def get_assignment_submissions(self, course_id, assignment_id):
        """
        Only returns those submissions that have actually been submitted, rather than potential submissions.
        :param course_id:
        :param assignment_id:
        :return:
        """
        return filter(lambda sub: sub['workflow_state'] == 'submitted',
                      self.get('/courses/%s/assignments/%s/submissions' % (course_id, assignment_id)))


    def get_submission_attachments(self, submission, as_bytes=False):
        """
        Get a dictionary containing the attachment files for this submission.
        :param submission: A JSON submission object.
        :param as_bytes: If True, get the file as bytes, else it will be returned as text.
        :return: A dictionary mapping filename to file contents.
        """
        attachments = {}

        for attachment in submission['attachments']:
            r = requests.get(attachment['url'], params={'access_token': self.access_token})
            if as_bytes:
                attachments[attachment['filename']] = r.content
            else:
                attachments[attachment['filename']] = r.text
        return attachments

