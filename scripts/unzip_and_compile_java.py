#!/usr/bin/env python
# -*- coding: utf- -*-


from marking import canvas_api, mongodb_store, marking_actions, marks, file_actions, git_actions, java_actions
import requests
from marking.mongodb_store import content_decode
import os
import argparse
from zipfile import ZipFile
if __name__ == "__main__":

    store = mongodb_store.SubmissionStore()
    capi = canvas_api.CanvasAPI(store.get_key())

    parser = argparse.ArgumentParser(description='Fetch, store then export submitted attachments for an assignment')
    parser.add_argument('course_id', metavar='CID', type=str, nargs=1,
                   help='The Canvas course ID. If unknown you can use list_courses.py')
    parser.add_argument('assignment_id', metavar='AID', type=str, nargs=1,   
                   help='The Canvas assignment ID. If unknown you can use list_assignments.py')
    parser.add_argument('--dir', dest='output_dir', type=str, default='/tmp',     
                   help='The directory where the exported attachments will be written.')
    parser.add_argument('-l', '--leave', action='store_true', 
                   help='Leave exported attachments on disk.')

    args = parser.parse_args()     

    course_id = args.course_id[0]
    assignment_id = args.assignment_id[0]
    output_dir = args.output_dir
    clean = not args.leave

    # get all submissions from Canvas
    # submissions = capi.get_assignment_submissions(course_id, assignment_id)
    # print('%s submissions retrieved from Canvas' % len(submissions))

    # def add_user(sub):
    #     marking_actions.get_username(sub, capi, store)

    # # make sure username is available in the submission document, as this is useful for marking scripts
    # map(add_user, submissions)

    # Store assignments locally for processing -- this allows later processing without Canvas access
    # The submissions do not contain the attachments 
    # store.store_assignment_submissions(course_id, assignment_id, submissions)

    # Get all assignments back out of the store (not strictly necessary)
    # submissions = store.get_assignment_submissions(course_id, assignment_id)        
    
    # or select some
    ids = [94545]
    # ids = [94545, 95200]
    submissions = [store.get_stored_submission(course_id, assignment_id, uis) for uis in ids]

    # This object provides access to attachments etc. 
    marker = marking_actions.Marker(course_id, capi, store)

    count = 1
    for submission in submissions:
        try:    

            print ('%s %s/%s' % (submission['user_id'], count, len(submissions)))
            
            # this creates an empty directory where we can work with the attachment files 
            with file_actions.SubmissionDirectory(submission, output_dir, clean) as sub_dir:

                # this creates a dictionary we'll use to store the output of marking 
                # you may not want to manage the marking in python, but this allows feedback about compilation etc.
                mark_dict = marker.create_mark_dict(submission)

                # get the attachments for the submission
                # this returns a dictionary mapping from filename to binary contents
                attachments = marker.get_attachments(submission)

                attachment_names = attachments.keys()

                # let's assume we asked for a single zip file, we could update the marks as follows
                if len(attachments) > 1 or not attachment_names[0].endswith('.zip'):
                    marks.set_final_mark(mark_dict, 0, 'You were supposed to provide a single zip file for the attachment.')
                    
                else:

                    # Let's pretend we had two parts to this assignment. The first assumes we can get zip file and extract the files.
                    # You don't need to have separate parts if you don't want to.

                    marks.set_part(mark_dict, 'Part 1')

                    filename = attachment_names[0]
                    content = attachments[filename]
                        
                    # absolute path to zip file
                    filename = os.path.join(sub_dir.path, filename)

                    # write it out to disk 
                    with open(filename, 'wb') as f:
                        f.write(content)

                    # and extract its contents to a 'src' subdirectory
                    with ZipFile(filename, 'r') as zipfile:
                        zipfile.extractall(path=os.path.join(sub_dir.path, 'src'))

                    # ok, we got this far, so let's give the student a mark
                    marks.add_component_mark(mark_dict, 1, 'Successfully extracted files from your zip file.')

                    # on to the next part then
                    marks.set_part(mark_dict, 'Part 2')

                    # next let's try to compile all the java files we got from the zip file 
                    # we pass in the mark_dict as this method also marks whether or not the compilation succeeds (you can ignore if you want)
                    mark_for_successful_compilation = 1
                    compiled, output, java_filenames = java_actions.compile_dirs(sub_dir.path, mark_dict, mark_for_successful_compilation)            

                    # if you wanted to run something as a result you could do...
                    # if compiled: 
                        # success, output = java_actions.run_java_class_live('Ex1Marking %s %s %s' % (15668, 50340, submission['id']), 'rp.assignments.individual.ex1', sub_dir.path, marks_dict, 0, classpath='/Users/nah/code/eclipse-workspace/rp-marking/lib/bson-3.0.4.jar:/Users/nah/code/eclipse-workspace/rp-marking/lib/mongo-java-driver-3.0.4.jar:/Applications/eclipse/plugins/org.junit_4.11.0.v201303080030/junit.jar:/Applications/eclipse/plugins/org.hamcrest.core_1.3.0.v201303031735.jar:/Users/nah/code/lejos/lib/nxt/classes.jar:/Users/nah/code/eclipse-workspace/rp-shared/bin:/Users/nah/code/eclipse-workspace/rp-pc/bin:/Users/nah/code/eclipse-workspace/rp-marking/bin')


                # now we can store the marks to process or upload later
                store.store_submission_marks(course_id, submission, mark_dict)

                # and/or we can get a final mark and text comment from the mark_dict
                grade, comment = marks.aggregate_marks(mark_dict)
                print 'Comment:\n', comment
                print 'Final Grade:', grade
                
                # And this is how to send a comment and a grade up to Canvas
                # capi.grade_assignment_submission(course_id, assignment_id, submission['user_id'], grade, comment)

            count += 1

        except requests.exceptions.ConnectionError, e:
            print e
