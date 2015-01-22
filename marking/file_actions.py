__author__ = 'nah'

import os
import shutil

class SubmissionDirectory(object):
    """Directory to work in"""

    def __init__(self, submission, path='/tmp'):
        """Constructor for SubmissionDirectory"""
        self.path = os.path.join(path, str(submission['assignment_id']), str(submission['user_id']))

    def __enter__(self):
        os.makedirs(self.path)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        shutil.rmtree(self.path)


def file_exists(file_path, base_path=None):
    if base_path is not None:
        file_path = os.path.join(base_path, file_path)

    return os.path.isfile(file_path)


def make_empty(file_path, base_path=None):
    if base_path is not None:
        file_path = os.path.join(base_path, file_path)

    if file_exists(file_path):
        shutil.rmtree(file_path)

    return os.makedirs(file_path)
