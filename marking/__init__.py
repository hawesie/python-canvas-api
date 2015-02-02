__author__ = 'nah'


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
        print(submission)



