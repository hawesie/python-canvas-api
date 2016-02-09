#!/usr/bin/env python
# -*- coding: utf- -*-


from marking import canvas_api, mongodb_store, marking_actions, marks, file_actions, git_actions, java_actions
import requests
from marking.mongodb_store import content_decode
import os
import argparse

if __name__ == "__main__":

    store = mongodb_store.SubmissionStore()
    capi = canvas_api.CanvasAPI(store.get_key())

    parser = argparse.ArgumentParser(description='Fetch, store then export submitted attachments for an assignment')
    parser.add_argument('course_id', metavar='CID', type=str, nargs=1,
                   help='The Canvas course ID. If unknown you can use list_courses.py')
    parser.add_argument('assignment_id', metavar='AID', type=str, nargs=1,   
                   help='The Canvas assignment ID. If unknown you can use list_assignments.py')
    parser.add_argument('--dir', dest='output_dir', type=str, nargs=1,  default='./output',     
                   help='The directory where the exported attachments will be written.')

    args = parser.parse_args()     

    course_id = args.course_id[0]
    assignment_id = args.assignment_id[0]
    output_dir = args.output_dir

    print args
    print output_dir

    # get all submissions from Canvas
    submissions = capi.get_assignment_submissions(course_id, assignment_id)
    print('%s submissions retrieved from Canvas' % len(submissions))

    def add_user(sub):
        marking_actions.get_username(sub, capi, store)

    # make sure username is available in the submission document, as this is useful for marking scripts
    map(add_user, submissions)

    # Store assignments locally for processing -- this allows later processing without Canvas access
    # The submissions do not contain the attachments 
    store.store_assignment_submissions(course_id, assignment_id, submissions)

    # Get all assignments back out of the store (not strictly necessary)
    # submissions = store.get_assignment_submissions(course_id, assignment_id)        
    
    # or select some
    # ids = [94545, 95200]
    # submissions = [store.get_stored_submission(course_id, assignment_id, uis) for uis in ids]

    # This object provides access to attatchments etc. 
    marker = marking_actions.Marker(course_id, capi, store)

    count = 1
    for submission in submissions:
        try:    

            print ('%s %s/%s' % (submission['user_id'], count, len(submissions)))
            with file_actions.SubmissionDirectory(submission, output_dir, False) as dir:
                attachments = marker.get_attachments(submission)
                for filename, content in attachments.iteritems():
                    with open(os.path.join(dir.path,filename), 'wb') as f:
                        f.write(content)

            count += 1

        except requests.exceptions.ConnectionError, e:
            print e
