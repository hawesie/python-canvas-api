__author__ = 'nah'

from marking import canvas_api, print_groups, mongodb_store
import argparse

if __name__ == "__main__":

    store = mongodb_store.SubmissionStore()
    capi = canvas_api.CanvasAPI(store.get_key())    
    
    parser = argparse.ArgumentParser(description='List groups for a Canvas course')
    parser.add_argument('course_id', metavar='ID', type=str, nargs=1,
                   help='The Canvas course ID. If unknown you can use list_courses.py')

    args = parser.parse_args()     
    groups = capi.get_course_groups(args.course_id[0])
    print_groups(groups)

