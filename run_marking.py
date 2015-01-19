__author__ = 'nah'

from concurrent import futures

from marking import canvas_api, mongodb_store, marking_actions, marks

def mark(submission, marker_fn):
    marker = marker_fn()
    return marker.mark(submission)

if __name__ == "__main__":
    capi = canvas_api.CanvasAPI("1848~N3mmmxpnXbEchYrRMhHBSVzLY6spgJteMxBhumiOHcMqb2R9CrJoyvB1v9FC0ITt")
    store = mongodb_store.SubmissionStore()

    # courses = capi.get_courses()
    # print_courses(courses)

    sww1 = 10065
    course_id = sww1

    # assignments = capi.get_assignments(sww1)
    # print_assignments(assignments)
    #

    git_assignment = 26165
    # assignment_id = 26353
    assignment_id = git_assignment

    # get all submissions
    # submissions = capi.get_assignment_submissions(course_id, assignment_id)

    # print('%s submissions retrieved from Canvas' % len(submissions))

    # store them locally for processing -- may not be necessary, but it allows more complex queries to be made
    # store.store_assignment_submissions(course_id, assignment_id, submissions)

    # the assignments that still need marking
    submissions = store.get_submissions_to_mark(course_id, assignment_id)

    print('%s submissions to mark' % submissions.count())

    def check_files(submission, file_dict, marks_dict):
        if len(file_dict) == 0:
            marks.set_final_mark(marks_dict, 0, 'No files found')
            return False
        if len(file_dict) > 1:
            marks.add_comment(marks_dict,
                              'More than one file found, but only one should have been submitted. Outcome may be unpredictable.')

        for filename in file_dict:
            tokens = filename.split('.')
            if marking_actions.is_username(tokens[0]) and tokens[0].lower() == submission['username'].lower():
                marks.add_comment(marks_dict, 'Filename %s is correct.' % filename)
            else:
                marks.add_component_mark(marks_dict, -0.5, 'Filename %s is not a username' % tokens[0])

        return True

    new_marker_fun = lambda: marking_actions.FileTokenMarker(capi, store, file_checker_fn=check_files)

    n_workers = 1

    with futures.ThreadPoolExecutor(max_workers=n_workers) as executor:

        fs = [executor.submit(mark, submission, new_marker_fun) for submission in submissions]

        for future in futures.as_completed(fs):
            try:
                print future.result()
            except StopIteration, e:
                pass
