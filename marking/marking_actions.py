__author__ = 'nah'
import re

import marks


class Marker(object):
    """"""

    def __init__(self, course_id, canvas_api, submission_store):
        """Constructor for Marker"""
        self.course_id = course_id
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

        # first try database retrieval
        attachments = self.submission_store.get_submission_attachments(self.course_id, submission)

        if attachments is None:
            attachments = self.canvas_api.get_submission_attachments(submission, as_bytes=True)

            # get the submission from the store
            self.submission_store.store_submission_attachments(self.course_id, submission, attachments)

        return attachments


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

    def __init__(self, course_id, canvas_api, submission_store, attachments_marker_fn=None):
        """Constructor for FileTokenMarker"""
        super(FileTokenMarker, self).__init__(course_id, canvas_api, submission_store)
        self.attachments_marker_fn = attachments_marker_fn


    def mark(self, submission):

        # get attachments for submission
        attachments = self.get_attachments(submission)
        #
        # add username into submission for convenience later
        submission['username'] = self.get_username(submission)
        #
        # print('marking %s, %s' % (submission['username'], submission['user_id']))

        mark_dict = {}
        mark_dict['username'] = submission['username']
        mark_dict['user_id'] = submission['user_id']

        if attachments is not None:
            self.attachments_marker_fn(submission, attachments, mark_dict)
        else:
            marks.set_final_mark(mark_dict, 0, 'No attachment files found')

        return mark_dict


