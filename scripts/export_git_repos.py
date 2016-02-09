#!/usr/bin/env python
# -*- coding: utf- -*-


from marking import canvas_api, mongodb_store, marking_actions, marks, file_actions, git_actions, java_actions
import requests
from marking.mongodb_store import content_decode
import os



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


    course_id = 15668
    assignment_id = 50340

    # # get all submissions from Canvas
    # submissions = capi.get_assignment_submissions(course_id, assignment_id)

    # print('%s submissions retrieved from Canvas' % len(submissions))


    # def add_user(sub):
    #     marking_actions.get_username(sub, capi, store)

    # # make sure username is available 
    # map(add_user, submissions)

    # # Store assignments locally for processing -- this allows later processing without Canvas access
    # # The submissions do not contain the attachments 
    # store.store_assignment_submissions(course_id, assignment_id, submissions)

    # # Get all assignments back out of the store -- doing this allows string conversion to utf8 
    # submissions = store.get_assignment_submissions(course_id, assignment_id)        
    
    # or select some
    ids = [68456, 95435, 95761, 96674, 64912, 92040, 92149, 93299,95012, 95839, 96828, 97107, 97809, 98663, 98786, 99168, 99758]
    submissions = [store.get_stored_submission(course_id, assignment_id, uis) for uis in ids]


    # This object provides access to attatchments etc. 
    marker = marking_actions.Marker(course_id, capi, store)

    count = 1
    for submission in submissions:
        try:    

            print ('%s %s/%s' % (submission['user_id'], count, len(submissions)))

            attachments = marker.get_attachments(submission)


            if not check_files(submission, attachments):
                continue

            num_files = len(attachments)

            assert num_files > 0

            filename = attachments.keys()[0]
            tokeniser = lambda f: f.split()

            # print attachments

            # file_tokens = filter(lambda token: token.startswith('git') or token.startswith('http'), tokeniser(attachments[filename]))
            file_tokens = tokeniser(str(attachments[filename]))

            if num_files > 1:
                print('More that one file submitted, using only %s' % filename)


            if not len(file_tokens) % 3 == 0:
                print('Tokens in file should be in multiples of 3. Yours has %s.' % len(file_tokens))
                continue

            repo_tokens = list(chunks(file_tokens,3))

            with file_actions.SubmissionDirectory(submission, './output', False) as dir:                
                try:                            
                    for tokens in repo_tokens:
                        # make a new sub directory to clone into. we'll use first 8 chars of commit hash
                        subdir_name = tokens[2][:8]
                        # print subdir_name
                        subdir = file_actions.make_empty(subdir_name, base_path=dir.path)
                        # print subdir
                        if git_actions.clone_repo_at_commit(tokens[0],tokens[1],tokens[2], subdir) is None:
                            print('Failed to clone repo %s.' % tokens[0])
                
                except ValueError, e:
                    print(str(e))
            count += 1

        except requests.exceptions.ConnectionError, e:
            print e
