#!/usr/bin/env python
# -*- coding: utf- -*-

from marking import canvas_api, print_assignments, mongodb_store
import argparse

if __name__ == "__main__":

    store = mongodb_store.SubmissionStore()
    capi = canvas_api.CanvasAPI(store.get_key())    
    
    parser = argparse.ArgumentParser(description='List assignments for a Canvas course')
    parser.add_argument('course_id', metavar='ID', type=str, nargs=1,
                   help='The Canvas course ID. If unknown you can use list_courses.py')

    args = parser.parse_args()     
    assignments = capi.get_assignments(args.course_id[0])
    print_assignments(assignments)

