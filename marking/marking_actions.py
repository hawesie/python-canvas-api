__author__ = 'nah'
import re


class Marker(object):
    """"""

    def __init__(self, canvas_api, submission_store):
        """Constructor for Marker"""
        self.canvas_api = canvas_api
        self.submission_store = submission_store


    def get_username(self, submission):
        uid = submission['user_id']
        username = self.submission_store.get_username(uid)
        if username is None:
            user = self.canvas_api.get_user(uid)
            print user
            username = self.submission_store.store_user(user)
        return username

    def get_attachments(self, submission):
        """

        Args:
            :param submission: The submission to get the attachments for

        Returns:
            A dictionary mapping filenames to their contents.
        """

        # get the submission from the store
        self.submission_store.

        return self.canvas_api.get_submission_attachments(submission, as_bytes=True)


    def mark(self, submission):
        return {}


username_pattern = re.compile('[a-z][a-z][a-z][0-9][0-9][0-9]', re.IGNORECASE)


def is_username(un):
    """
        Returns true if un is the of the form of a student username (6 characters, 3 letters then 3 numbers)
    :param un:
    :return:
    """
    return un is not None and len(un) == 6 and username_pattern.match(un) is not None


def split_and_check(filename, split_on='.'):
    tokens = filename.split(sep=split_on)
    print tokens
    print len(tokens)


class FileTokenMarker(Marker):
    """
        Marks the submission based on tokens in the attachments, but does not write attachments to disk.
    """

    def __init__(self, canvas_api, submission_store, file_checker_fn=None, file_tokeniser_fn=None,
                 token_marker_fn=None):
        """Constructor for FileTokenMarker"""
        super(FileTokenMarker, self).__init__(canvas_api, submission_store)
        self.file_checker_fn = file_checker_fn
        self.file_tokeniser_fn = file_tokeniser_fn
        self.token_marker_fn = token_marker_fn


    def mark(self, submission):
        # get attachments for sumission
        attachments = self.get_attachments(submission)

        # add username into submission for convenience later
        submission['username'] = self.get_username(submission)

        marks = {}

        if self.file_checker_fn is not None:
            if not self.file_checker_fn(submission, attachments, marks):
                return marks

        return marks