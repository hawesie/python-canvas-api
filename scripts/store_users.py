__author__ = 'nah'

from marking import canvas_api, mongodb_store
import argparse

if __name__ == "__main__":

    store = mongodb_store.SubmissionStore()
    capi = canvas_api.CanvasAPI(store.get_key())    
    
    parser = argparse.ArgumentParser(description='Fetch and store users for Canvas course')
    parser.add_argument('course_id', metavar='ID', type=str, nargs=1,
                   help='The Canvas course ID. If unknown you can use list_courses.py')

    args = parser.parse_args()     
    users = capi.get_users(args.course_id[0])
    store.store_users(users) 
    print('Stored %s users' % len(users))

