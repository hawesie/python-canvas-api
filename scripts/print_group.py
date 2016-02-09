#!/usr/bin/env python
# -*- coding: utf- -*-

from marking import canvas_api, mongodb_store
import argparse

if __name__ == "__main__":

    store = mongodb_store.SubmissionStore()

    parser = argparse.ArgumentParser(description='Print group details') 
    group = parser.add_mutually_exclusive_group()

    group.add_argument('-n', '--name', help='Group name', type=str)

    parser.add_argument('course_id', metavar='ID', type=str, nargs=1,
                   help='The Canvas course ID. If unknown you can use list_courses.py')
    parser.add_argument('category_id', metavar='CAT', type=str, nargs=1,
                   help='The Canvas course gruop ID')

    args = parser.parse_args()     
        	
    print(args.course_id, args.category_id, args.name)	
 

    print(store.get_group(args.course_id[0], args.category_id[0], args.name.upper()))

