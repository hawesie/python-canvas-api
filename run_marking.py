__author__ = 'nah'

from marking import canvas_api, mongodb_store, print_submissions




# def mark(submission):
# need to specialise to different marking workflows



if __name__ == "__main__":
    capi = canvas_api.CanvasAPI("1848~N3mmmxpnXbEchYrRMhHBSVzLY6spgJteMxBhumiOHcMqb2R9CrJoyvB1v9FC0ITt")
    store = mongodb_store.SubmissionStore()

    # courses = capi.get_courses()
    # print_courses(courses)

    # course_id = 5769
    sww1 = 10065

    # assignments = capi.get_assignments(sww1)
    # print_assignments(assignments)
    #
    # assignment_id = 26353

    git_assignment = 26165

    submissions = capi.get_assignment_submissions(sww1, git_assignment)


    # store.store_assignment_submissions(course_id, assignment_id, submissions)
    # stored_submissions = store.get_assignment_submissions(course_id, assignment_id)
    print_submissions(submissions)
    # print capi.get_submission_attachments(submissions[0])

    # with futures.ThreadPoolExecutor(max_workers=5) as executor:
    # fs = [executor.submit(mark, submission) for submission in submissions]
    #
    #     for future in futures.as_completed(fs):
    #         print future.result()