__author__ = 'nah'

from marking import canvas_api, print_courses, mongodb_store

if __name__ == "__main__":

    store = mongodb_store.SubmissionStore()
    capi = canvas_api.CanvasAPI(store.get_key())    

    courses = capi.get_courses()
    print_courses(courses)

