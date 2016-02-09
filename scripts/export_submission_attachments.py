#!/usr/bin/env python

__author__ = 'nah'

from marking import canvas_api, mongodb_store, marking_actions, marks, file_actions, git_actions, java_actions
import requests
from marking.mongodb_store import content_decode
import os


if __name__ == "__main__":

    store = mongodb_store.SubmissionStore()
    capi = canvas_api.CanvasAPI(store.get_key())


    course_id = 15668
    assignment_id = 50340

    # get all submissions from Canvas
    submissions = capi.get_assignment_submissions(course_id, assignment_id)

    print('%s submissions retrieved from Canvas' % len(submissions))


    def add_user(sub):
        marking_actions.get_username(sub, capi, store)

    # make sure username is available 
    map(add_user, submissions)

    # Store assignments locally for processing -- this allows later processing without Canvas access
    # The submissions do not contain the attachments 
    store.store_assignment_submissions(course_id, assignment_id, submissions)

    # Get all assignments back out of the store -- doing this allows string conversion to utf8 
    submissions = store.get_assignment_submissions(course_id, assignment_id)        
    
    # or select some
    # ids = [68456, 95435, 95761, 96674, 64912, 92040, 92149, 93299,95012, 95839, 96828, 97107, 97809, 98663, 98786, 99168, 99758]
    # submissions = [store.get_stored_submission(course_id, assignment_id, uis) for uis in ids]


    # This object provides access to attatchments etc. 
    marker = marking_actions.Marker(course_id, capi, store)

    count = 1
    for submission in submissions:
        try:    

            print ('%s %s/%s' % (submission['user_id'], count, len(submissions)))
            with file_actions.SubmissionDirectory(submission, './output', False) as dir:
                attachments = marker.get_attachments(submission)
                for filename, content in attachments.iteritems():
                    with open(os.path.join(dir.path,filename), 'wb') as f:
                        f.write(content)

            count += 1

        except requests.exceptions.ConnectionError, e:
            print e
