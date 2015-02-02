__author__ = 'nah'

from marking import canvas_api, print_assignments, mongodb_store, marking_actions
import argparse
import csv

def store_team_contributions_submissions(store, course_id, assignment_id, submissions):
    store.store_assignment_submissions(course_id, assignment_id, submissions)
    teams = [sub['team'] for sub in submissions]
    store.get_assignment_collection(course_id, assignment_id).insert({'teams': teams})


def get_teams(store, course_id, assignment_id):
    return store.get_assignment_collection(course_id, assignment_id).find_one({'teams': {'$exists': True}})['teams']


def get_non_equal(store, course_id, assignment_id):
    query = {'$or': [{'part_1_equal': False}, {'part_2_equal': False} , {'part_3_equal': False}]}

    return store.get_assignment_collection(course_id, assignment_id).find(query)


def get_submissions(store, course_id, assignment_id, team):
    query = {'team': team}

    return store.get_assignment_collection(course_id, assignment_id).find(query)

def quiz_row_to_doc(row):

    # print row

    doc = dict()
    doc['name'] = row[0]
    doc['quiz_submission_id'] = row[1]  
    doc['sis_user_id'] = str(row[2])
    team_list = row[8].split(',')
    doc['team'] = team_list[0].lower()
    for i in range(1,len(team_list)):
        doc['other_%s' % i] = team_list[i].lower()


    part_splits = [row[n].split(',') for n in [10, 12, 14]]

    for n in range(0, len(part_splits)):

        part_n = n + 1
        # print part_splits[n]
        if len(part_splits[n]) == 2:
            doc['part_%s_attempted' % part_n] = part_splits[n][0] == 'Yes'
            doc['part_%s_equal' % part_n] = part_splits[n][1] == 'Yes'
        elif len(part_splits[n]) < 2:
            doc['part_%s_attempted' % part_n] =  False
            doc['part_%s_equal' % part_n] = True
        else:
            doc['part_%s_attempted' % part_n] = part_splits[n][1] == 'Yes'
            doc['part_%s_equal' % part_n] = part_splits[n][2] == 'Yes'

            doc['part_%s_self' % (part_n)] = int(part_splits[n][0])

            for m in range(3, len(part_splits[n])):
                doc['part_%s_other_%s' % (part_n, m-2)] = int(part_splits[n][m])

    return doc


def add_if_exists(k, d, container):
    if k in d and len(d[k]) > 0:
        container.add(d[k])

def get_if_exists(keys, d):
    vals = set()
    for k in keys:
        if k in d:
            vals.add(d[k])
    return vals

def replace_usernames(mappings, submission):
    """
    Replaces all mappings.key with mappings.value in other_* fields of submission
    """
    for key, value in mappings.iteritems():
        if 'other_1' in submission and submission['other_1'] == key:
            submission['other_1'] = value            
        if 'other_2' in submission and submission['other_1'] == key:
            submission['other_1'] = value            
        if 'other_3' in submission and submission['other_1'] == key:
            submission['other_1'] = value            


def print_part(part_n, submissions):
    print('\n-------- PART %s --------\n' % part_n)

    for submission in submissions:
        # print submission

        print submission['name']
        attempted = submission['part_%s_attempted' % part_n]
        if attempted:
            
            equal = submission['part_%s_equal' % part_n]
            
            if not equal:
                # print 'Part 1'
                # print('Attempted: %s' % attempted)
                # print('Equal: %s' % submission['part_%s_equal' % part_n])
                if 'other_1' in submission:
                    print 'Rated ' + submission['other_1'] + ' at ' + str(submission['part_%s_other_1' % part_n])
                if 'other_2' in submission and 'part_%s_other_2' % part_n in submission:
                    print 'Rated ' + submission['other_2'] + ' at ' + str(submission['part_%s_other_2' % part_n])
                if 'other_3' in submission:
                    print 'Rated ' + submission['other_3'] + ' at ' + str(submission['part_%s_other_3' % part_n])

if __name__ == "__main__":

    store = mongodb_store.SubmissionStore()
    capi = canvas_api.CanvasAPI(store.get_key())    
    
    course_id = 9779
    assignment_id = 26621
    team_category = 2836

    with open('/Users/nah/Downloads/Exercise 2_ Team Contributions Survey Student Analysis Report.csv', 'rb') as csvfile:
        csv_file_reader = csv.reader(csvfile)

        # get past the header
        for row in csv_file_reader: 
            if row[-1] == 'score':
                break

        docs = map(quiz_row_to_doc, csv_file_reader)


    store_team_contributions_submissions(store, course_id, assignment_id, docs)
    teams = set(get_teams(store, course_id, assignment_id))

    non_equal_teams = {submission['team'] for submission in get_non_equal(store, course_id, assignment_id)}
        
    # team_submissions = {team: get_submissions(store, course_id, assignment_id,team) for team in non_equal_teams}

    manual_inspection = []

    non_equal_teams = ['i3']

    for team in non_equal_teams:        

        print('\n         TEAM %s         \n=========================\n' % team)

        target_names = set(map(store.get_username, store.get_group_members(course_id, team_category, team.upper())))

        print target_names

        submissions = list(get_submissions(store, course_id, assignment_id, team))
        print submissions
 
        members = set()
        for submission in submissions:
            add_if_exists('other_1', submission, members)
            add_if_exists('other_2', submission, members)
            add_if_exists('other_3', submission, members)           

        # print members
        mappings, target_missing, extra_listed = marking_actions.align_username_sets(target_names, members) 

        # print target_missing
        # print extra_listed


        if len(mappings) > 0:           
            for submission in submissions:
                replace_usernames(mappings, submission)

        if len(target_missing) > 0:
            print('Team %s missing expected teammates %s' % (team, target_missing))
            continue 

        if len(extra_listed) > 0:
            print('Team %s has extra teammates listed: %s' % (team, extra_listed))
            continue         


        print_part(1, submissions)
        print_part(2, submissions)
        print_part(3, submissions)


        # if len(extra_listed) > 0 or len(target_missing) > 0:
        #     print('Process team %s manually' % team)
        #     manual_inspection.append(team)
        # else:
        #     # in here all the usernames in the team should be represented

        #     # produce a 
        #     print('Team %s Part 1' % team)
        #     print('Attempted: %s' % ([submission['part_1_attempted'] for submission in submissions]))
        #     print('Equal: %s' % ([submission['part_1_equal'] for submission in submissions]))
        #     out = ''
        #     for member in target_names:
        #         # super ugly way for doing this, but running short of time                
        #         out += 'For Part 1 %s was weighted' % member

        #         for submission in submissions:
        #             # collect others
        #             others = get_if_exists(['other_1', 'other_2', 'other_3'], submission)                    
                    
        #             if member in others:                        
        #                 # this was not mine so can report rating

        #                 # who did the rating?
        #                 rater = (target_names - others).pop()

        #                 if submission['part_1_equal']:
        #                     out += ', equal by ' + rater
        #                 elif 'other_1' in submission and submission['other_1'] == member:
        #                     out += ', ' + str(submission['part_1_other_1']) + ' by ' + rater
        #                 elif 'other_2' in submission and submission['other_2'] == member:
        #                     out += ', ' + str(submission['part_1_other_2']) + ' by ' + rater
        #                 elif 'other_3' in submission and submission['other_3'] == member:
        #                     out += ', ' + str(submission['part_1_other_3']) + ' by ' + rater
        #         out += '\n'
        #     print out 



        #     print('Team %s Part 2' % team)
        #     print('Attempted: %s' % ([submission['part_2_attempted'] for submission in submissions]))
        #     print('Equal: %s' % ([submission['part_2_equal'] for submission in submissions]))

        #     print('Team %s Part 3' % team)
        #     print('Attempted: %s' % ([submission['part_3_attempted'] for submission in submissions]))
        #     print('Equal: %s' % ([submission['part_3_equal'] for submission in submissions]))


