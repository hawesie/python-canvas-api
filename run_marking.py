__author__ = 'nah'

import canvas_api
import mongodb_store


def print_courses(courses):
    print('Courses:')
    for course in courses:
        print('%s: %s' % (course['id'], course['name']))


def print_assignments(assignments):
    print('Assignments:')
    for assignment in assignments:
        if 'online_quiz' in assignment['submission_types']:
            print('%s: %s (%s, quiz_id: %s)' % (
                assignment['id'], assignment['name'], assignment['submission_types'], assignment['quiz_id']))
        else:
            print('%s: %s (%s)' % (assignment['id'], assignment['name'], assignment['submission_types']))


def print_submissions(submissions):
    print('Submissions:')
    for submission in submissions:
        print('%s: %s - %s' % (submission['user_id'], submission['submitted_at'], submission['workflow_state']))
        # print(submission)


if __name__ == "__main__":
    capi = canvas_api.CanvasAPI("1848~N3mmmxpnXbEchYrRMhHBSVzLY6spgJteMxBhumiOHcMqb2R9CrJoyvB1v9FC0ITt")
    store = mongodb_store.SubmissionStore()

    # courses = capi.get_courses()
    # print_courses(courses)

    course_id = 5769

    # assignments = capi.get_assignments(course_id)
    # print_assignments(assignments)

    assignment_id = 26353

    submissions = capi.get_assignment_submissions(course_id, assignment_id)
    print_submissions(submissions)
    store.store_assignment_submissions(course_id, assignment_id, submissions)
    stored_submissions = store.get_assignment_submissions(course_id, assignment_id)
    print_submissions(submissions)