__author__ = 'nah'

from marking import canvas_api, print_assignments, mongodb_store
import argparse
import csv

if __name__ == "__main__":

    store = mongodb_store.SubmissionStore()
    capi = canvas_api.CanvasAPI(store.get_key())    
    
    # parser = argparse.ArgumentParser(description='List assignments for a Canvas course')
    # parser.add_argument('course_id', metavar='CID', type=str, nargs=1,
    #                help='The Canvas course ID. If unknown you can use list_courses.py')
    # parser.add_argument('quiz_id', metavar='QID', type=str, nargs=1,
    #                help='The Canvas quiz ID. If unknown you can use list_assignments.py')

    # args = parser.parse_args() 
    # # print capi.get_assignment_submissions(args.course_id[0], args.quiz_id[0])[0]
    # print capi.get_quiz_submissions(args.course_id[0], 17065)


    with open('/Users/nah/Downloads/Exercise 2_ Team Contributions Survey Student Analysis Report.csv', 'rb') as csvfile:
    	spamreader = csv.reader(csvfile)
     	for row in spamreader:
        	print ', '.join(row)