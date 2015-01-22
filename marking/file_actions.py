__author__ = 'nah'

import os


class SubmissionDirectory(object):
    """Directory to work in"""

    def __init__(self, submission, path='/tmp'):
        """Constructor for SubmissionDirectory"""
        self.path = os.path.join(path, str(submission['assignment_id']), str(submission['user_id']))

    def __enter__(self):
        os.makedirs(self.path)

    def __exit__(self, exc_type, exc_value, traceback):
        os.rmdir(self.path)
    
