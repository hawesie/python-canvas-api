#!/usr/bin/env python
# -*- coding: utf- -*-


from marking import canvas_api, mongodb_store, marking_actions, marks, file_actions, git_actions, java_actions
import requests
from marking.mongodb_store import content_decode
import os
import argparse


def check_files(submission, file_dict):

    if len(file_dict) == 0:
        print('No files found')
        return False
    if len(file_dict) > 1:
        print('More than one file found, but only one should have been submitted. Outcome may be unpredictable.')

    return True

# 
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


if __name__ == "__main__":

    store = mongodb_store.SubmissionStore()
    capi = canvas_api.CanvasAPI(store.get_key())

    parser = argparse.ArgumentParser(description='Export submitted attachments and run the moss plagiarism checker on them. Currently hardcoded to work on Java files.')
    parser.add_argument('course_id', metavar='CID', type=str, nargs=1,
                   help='The Canvas course ID. If unknown you can use list_courses.py')
    parser.add_argument('assignment_id', metavar='AID', type=str, nargs=1,   
                   help='The Canvas assignment ID. If unknown you can use list_assignments.py')
    parser.add_argument('--dir', dest='output_dir', type=str, nargs=1,  default='./output',     
                   help='The directory where the exported attachments will be written.')
    parser.add_argument('-g', '--group', type=int, nargs=1, default=None,
                   help='If this was a group assignment, supply the group category ID. This is visible using list_groups.py')

        

    args = parser.parse_args()     

    # print args

    course_id = args.course_id[0]
    assignment_id = args.assignment_id[0]
    output_dir = args.output_dir
    group = None if args.group is None else args.group[0]
    


    # get all submissions from Canvas
    submissions = capi.get_assignment_submissions(course_id, assignment_id)

    print('%s submissions retrieved from Canvas' % len(submissions))


    def add_user(sub):
        marking_actions.get_username(sub, capi, store)

    # make sure username is available 
    map(add_user, submissions)

    # Store assignments locally for processing -- this allows later processing without Canvas access
    # The submissions do not contain the attachments 
    store.store_assignment_submissions(course_id, assignment_id, submissions, group_category_id=group)

    # Get all assignments back out of the store -- doing this allows string conversion to utf8 
    submissions = store.get_assignment_submissions(course_id, assignment_id)        
    
    print('%s submissions to check' % len(submissions))

    # or select some
    # ids = [68456, 95435, 95761, 96674]
    # submissions = [store.get_stored_submission(course_id, assignment_id, uis) for uis in ids]


    # This object provides access to attatchments etc. 
    marker = marking_actions.Marker(course_id, capi, store)
    submission_files = []
    count = 1

    submission_key = 'username' if group is None else 'group'

    for submission in submissions:
        try:    

            print_key = 'group' if 'group' in submission else 'user_id'

            print ('%s %s/%s' % (submission[print_key], count, len(submissions)))

            attachments = marker.get_attachments(submission)


            if not check_files(submission, attachments):
                continue

            num_files = len(attachments)

            assert num_files > 0

            filename = attachments.keys()[0]
            tokeniser = lambda f: map(content_decode, f.split())

            # print attachments

            # file_tokens = filter(lambda token: token.startswith('git') or token.startswith('http'), tokeniser(attachments[filename]))
            file_tokens = tokeniser(str(attachments[filename]))

            if num_files > 1:
                print('More that one file submitted, using only %s' % filename)


            if not len(file_tokens) % 3 == 0:
                print('Tokens in file should be in multiples of 3. Yours has %s.' % len(file_tokens))
                continue

            repo_tokens = list(chunks(file_tokens,3))




            with file_actions.SubmissionDirectory(submission, output_dir, False, user_key=submission_key) as dir:                
                try:                            
                    for tokens in repo_tokens:
                        # make a new sub directory to clone into. we'll use first 8 chars of commit hash
                        subdir_name = tokens[2][:8]
                        # print subdir_name
                        subdir = file_actions.make_empty(subdir_name, base_path=dir.path)
                        # print subdir
                        if git_actions.clone_repo_at_commit(tokens[0],tokens[1],tokens[2], subdir) is None:
                            print('Failed to clone repo %s.' % tokens[0])


                    submission_files.append([os.path.join(dir.dirname,fn) for fn in file_actions.find_files_matching(dir.path, '*.java')])
                                    
                except ValueError, e:
                    print(str(e))
            count += 1

        except requests.exceptions.ConnectionError, e:
            print e

    cwd = os.path.join(output_dir, str(assignment_id))
    moss_cmd = file_actions.build_moss_command(submission_files, lang='java')

    print 'Calling moss...'
    success, output = file_actions.run_process(moss_cmd, cwd)

    if success:
        print 'Calling moss...'
        print output
        output_file = 'moss_results_%s_%s.txt' % (course_id, assignment_id)
        
        with open(output_file, 'wb') as f:
            f.write(output)
            print 'Written results to %s' % output_file

    else:
        print 'call failed'



