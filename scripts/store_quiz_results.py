#!/usr/local/bin/python
# -*- coding: utf- -*-

from marking import canvas_api, mongodb_store, marking_actions
import argparse
from marking.mongodb_store import content_decode
import re
import requests
import csv
import json


def csv_to_dict(csvfile):
    lines = csvfile.split('\n')
    headers = csv.reader(lines, delimiter=',', quotechar='"').next()    
    reader = csv.DictReader(lines[1:], headers, delimiter=',', quotechar='"')
    return [line_dict for line_dict in reader]



if __name__ == "__main__":

    store = mongodb_store.SubmissionStore()
    capi = canvas_api.CanvasAPI(store.get_key())    
    rp15 = 15668
    course_id = rp15
    lab_group = 3854

    # assignments = capi.get_assignments(rp15)
    # print_assignments(assignments)
    #

    
    quiz_id = 25653

    # get the report for this quiz
    post = capi.post('/courses/%s/quizzes/%s/reports' % (course_id, quiz_id), {'quiz_report[report_type]': 'student_analysis', 'include':'file'})
    # print post.text["id"]


    report = post.json()

    print report['file']['url']
    csvfile = content_decode(requests.get(report['file']['url']).content)
    submissions = csv_to_dict(csvfile)
    
    # Need to add username to each submission for later
    for submission in submissions:        
        uid = int(submission['id'])
        submission['username'] = store.get_username(uid)
        submission['lab_group'] = store.get_group_from_category(course_id, lab_group, uid, key='user_id')        
        for key, value in submission.iteritems():
            if key.find('.') != -1:
                del submission[key]
                submission[key.replace('.','_')] = value


    store.store_assignment_submissions(course_id, quiz_id, submissions)


