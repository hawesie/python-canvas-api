__author__ = 'nah'

from marking import canvas_api, mongodb_store, marking_actions, marks, file_actions, git_actions, java_actions
import requests
from marking.mongodb_store import content_decode



def mark(submission, marker_fn):
    marker = marker_fn()
    return marker.mark(submission)
    # print(submission)
    # print('\n')
    # time.sleep(random.randrange(4,10))
    # return something


# def mark(something, other):
# print(something)
#     print('\n')
#     time.sleep(random.randrange(4,10))
#     return something

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


def git_file_marker(submission, attachments, marks_dict):
    if not check_files(submission, attachments, marks_dict):
        return marks_dict

    num_files = len(attachments)

    assert num_files > 0

    filename = attachments.keys()[0]
    tokeniser = lambda f: f.split()

    # print attachments

    # file_tokens = filter(lambda token: token.startswith('git') or token.startswith('http'), tokeniser(attachments[filename]))
    file_tokens = tokeniser(str(attachments[filename]))

    if num_files > 1:
        marks.add_comment(marks_dict, 'More that one file submitted, using only %s' % filename)



    if len(file_tokens) > 3:
        file_tokens = file_tokens[0:2]
        marks.add_comment(marks_dict, 'More than three tokens in submitted file, using first three')

    print file_tokens            

    marks.set_part(marks_dict, 'Part 1')
    with file_actions.SubmissionDirectory(submission) as dir:
        if git_actions.clone_repo(file_tokens[0], dir.path) is not None:

            marks.add_component_mark(marks_dict, 1, 'Cloned %s successfully' % file_tokens[0])

            # whether compilation completed successful, and what file was used for compilation
            compiled, filename = java_actions.compile_java_class('WhoAmI', 'git.part1', dir.path, marks_dict, 0)
            if compiled:
                success, output = java_actions.run_java_class('WhoAmI', 'git.part1', dir.path, filename, marks_dict, 1,
                                                              expected_output=submission['username'])
            else:
                marks.add_component_mark(marks_dict, 0, 'Unable to run class as it did not compile. ')
        else:
            marks.add_component_mark(marks_dict, 0,
                                     'Could not clone repo %s. Did you add Nick as a member?' % file_tokens[0])


    if len(file_tokens) > 1:
        marks.set_part(marks_dict, 'Part 2')
        with file_actions.SubmissionDirectory(submission) as dir:

            if git_actions.clone_repo(file_tokens[1], dir.path) is not None:
                marks.add_component_mark(marks_dict, 0.5, 'Cloned %s successfully' % file_tokens[1])

                def get_line_fn(f):
                    # this is a big hack to get around the fact I didn't specify the exercise well enough
                    already = ['nah', 'jxh373', 'jxr227', 'sdb123', 'fxj345']
                    for l in f:
                        tokens = l.split(':')
                        if len(tokens) > 1 and tokens[0] not in already:
                            return l
                    return None

                def mark_file_fn(f, mark_dict):
                    def line_match_fn(l):
                        l = content_decode(l)
                        return l.lower().startswith('%s:' % submission['username'].lower())

                    file_actions.match_file_line(f, get_line_fn, line_match_fn, mark_dict, 0.5)

                file_actions.mark_file('edit-me.md', dir.path, marks_dict, 0.5, mark_file_fn)
            else:
                marks.add_component_mark(marks_dict, 0, 'Could not clone repo %s' % file_tokens[1])

    marks.set_part(marks_dict, 'Extension')
    with file_actions.SubmissionDirectory(submission) as dir:
        repo = git_actions.clone_repo(file_tokens[0], dir.path)
        if repo is not None:
            marks.add_component_mark(marks_dict, 0, 'Cloned %s successfully' % file_tokens[0])

            # whether compilation completed successful, and what file was used for compilation
            compiled, filename = java_actions.compile_java_class('LastCommit', 'git.extension', dir.path, marks_dict, 0)
            if compiled:
                success, output = java_actions.run_java_class('LastCommit', 'git.extension', dir.path, filename,
                                                              marks_dict,
                                                              1,
                                                              expected_output=git_actions.get_last_commit(
                                                                  repo).__str__())
                # success is whether program ran, not whether it did the right thing
                # if success:
                #         marks.add_component_mark(marks_dict, 0, 'Kudos for successfully completing the extension.')
                # else:
                #     marks.add_component_mark(marks_dict, 0,
                #                              'Well done for attempting the extension, but the output was not correct. Please check "git log" for your last commit hash.')

            else:
                marks.add_component_mark(marks_dict, 0,
                                         'Unable to run class as it did not compile. This is probably because you didn\'t attempt the extension.')
        else:
            marks.add_component_mark(marks_dict, 0,
                                     'Could not clone repo %s. Did you add Nick as a member?' % file_tokens[0])

    return marks_dict

if __name__ == "__main__":
    access_token = "1848~N3mmmxpnXbEchYrRMhHBSVzLY6spgJteMxBhumiOHcMqb2R9CrJoyvB1v9FC0ITt"
    capi = canvas_api.CanvasAPI(access_token)
    store = mongodb_store.SubmissionStore()

    # courses = capi.get_courses()
    # print_courses(courses)

    sww1 = 16318
    course_id = sww1

    # assignments = capi.get_assignments(sww1)
    # print_assignments(assignments)
    #

    git_assignment = 49819
    assignment_id = git_assignment

    # get all submissions
    # submissions = capi.get_assignment_submissions(course_id, assignment_id)

    # print('%s submissions retrieved from Canvas' % len(submissions))


    # def add_user(sub):
    #     marking_actions.get_username(sub, capi, store)

    # # make sure username is available
    # map(add_user, submissions)

    # store them locally for processing -- may not be necessary, but it allows more complex queries to be made
    # store.store_assignment_submissions(course_id, assignment_id, submissions)

    # get just the assignments that still need marking
    # submissions = store.get_submissions_to_mark(course_id, assignment_id)    

    # get all assignments
    submissions = store.get_assignment_submissions(course_id, assignment_id)        
    submissions = filter(lambda sub: len(sub['username']) > 0, submissions)


    # test_ids = [95534]
    # submissions = [store.get_stored_submission(course_id, assignment_id, uis) for uis in test_ids]

    new_marker_fun = lambda: marking_actions.FileTokenMarker(course_id, capi, store,
                                                             attachments_marker_fn=git_file_marker)

    print('%s submissions to mark' % len(submissions))

    count = 1
    for submission in submissions:
        print ('%s %s/%s' % (submission['user_id'], count, len(submissions)))
        mark_dict = mark(submission, new_marker_fun)
        store.store_submission_marks(course_id, submission, mark_dict)
        grade, comment = marks.aggregate_marks(mark_dict)
        print comment
        # capi.grade_assignment_submission(course_id, assignment_id, submission['user_id'], grade, comment)
        count += 1
        # break

    # # for submission in submissions:
    # #     grade, comment = marks.aggregate_marks(submission['marks'])       
    # #     canvas_api.grade_assignment_submission(course_id, assignment_id, submission['user_id'], grade, comment)

    #     # n_workers = 10
    #     #
    #     # with futures.ThreadPoolExecutor(max_workers=n_workers) as executor:
    #     #
    #     # fs = [executor.submit(mark, submission, new_marker_fun) for submission in submissions]
    #     #
    #     #     # futures.wait(fs)
    #     #
    #     #     for future in futures.as_completed(fs):
    #     #         print('done: %s' % future.result())


