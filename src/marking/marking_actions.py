__author__ = 'nah'
import re

import marks
import itertools

def get_username(submission, capi, store):
    uid = submission['user_id']
    username = store.get_username(uid)
    if username is None:
        user = capi.get_user(uid)
        # print user
        username = store.store_user(user)

    if username is not None:
        submission['username'] = username
        
    return username

def hamming(u1, u2):
    
    diffs = 0
    for ch1, ch2 in itertools.izip_longest(u1, u2):
        if ch1 != ch2:
            diffs += 1
    return diffs


def align_username_sets(target, given, threshold=1):
    # elements of given which are not in target
    extra_in_given = given - target
    extra_in_target = target - given
    mappings = dict()

    # if they match return target
    if len(extra_in_target) > 0 or len(extra_in_given) > 0:

        # now match the extra_in_given list to see if we can map to target
        for extra in extra_in_given:
            for targ in target:
                similarity_score = hamming(extra, targ)
                if similarity_score <= threshold:
                    mappings[extra] = targ
                    print('mapping %s to %s: %s' % (extra, targ, similarity_score))

        
        extra_in_given -= set(mappings.keys())
        extra_in_target -= set(mappings.values())

    return mappings, extra_in_target, extra_in_given


class Marker(object):
    """"""

    def __init__(self, course_id, canvas_api, submission_store):
        """Constructor for Marker"""
        self.course_id = course_id
        self.canvas_api = canvas_api
        self.submission_store = submission_store

    def create_mark_dict(self, submission):
        mark_dict = {}
        mark_dict['username'] = submission['username']
        mark_dict['user_id'] = submission['user_id']
        return mark_dict

    def get_username(self, submission):
        return get_username(submission, self.canvas_api, self.submission_store)

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

            # fetch from canvas
            attachments = self.canvas_api.get_submission_attachments(submission, as_bytes=True)

            # print attachments
            
            if attachments is not None:
    

                # add to the store
                self.submission_store.store_submission_attachments(self.course_id, submission, attachments)

                # the retrieve again, as this allows string processing and a consistent return format
                attachments = self.submission_store.get_submission_attachments(self.course_id, submission)

                # print attachments

        return attachments


    def mark(self, submission):
        return {}


username_pattern = re.compile('[a-z]{3}[0-9]{3,4}$', re.IGNORECASE)


def is_username(un):
    """
        Returns true if un is the of the form of a student username (6 characters, 3 letters then 3 numbers)
    :param un:
    :return:
    """
    return un is not None and username_pattern.match(un) is not None


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
        
        
        # print('marking %s, %s' % (submission['username'], submission['user_id']))

        mark_dict = self.create_mark_dict(submission)

        if attachments is not None:
            self.attachments_marker_fn(submission, attachments, mark_dict)
        else:
            marks.set_final_mark(mark_dict, 0, 'No attachment files found')

        return mark_dict


