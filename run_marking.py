__author__ = 'nah'

from concurrent import futures

from marking import canvas_api, mongodb_store


def mark(submissions, canvas_api, submission_store):
    # get the
    submission = next(submissions)
    attachments = capi.get_submission_attachments(submission, as_bytes=True)

# todo this is where a class and hierarchy should start, the object should have the submission, api and store and have the specialised subclasses and parts to do the different things


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
    submissions = capi.get_assignment_submissions(course_id, assignment_id)

    # store them locally for processing -- may not be necessary, but it allows more complex queries to be made
    store.store_assignment_submissions(course_id, assignment_id, submissions)

    # the assignments that still need marking
    submissions = store.get_submissions_to_mark(course_id, assignment_id)


    # print_submissions(submissions)

    # print capi.get_submission_attachments(submissions[0])

    # using iter explicitly to avoid retrieving all submissions from db
    submission_iter = iter(submissions)

    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        fs = [executor.submit(mark, submission_iter, capi, store) for submission in submissions]

        for future in futures.as_completed(fs):
            try:
                print future.result()
            except StopIteration, e:
                pass
