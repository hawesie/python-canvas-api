__author__ = 'nah'

from marking import canvas_api, print_assignments, mongodb_store
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

    for team in non_equal_teams:

    	print store.get_group_members(course_id, team_category, team.upper())

    	def to_username(sis_user_id):
    		store.get_username(str(sis_user_id), 'sis_user_id')

    	print map(to_username, store.get_group_members(course_id, team_category, team.upper()))

    	# submissions = get_submissions(store, course_id, assignment_id, team)
    	# print team
    	# members = set()
    	# for submission in submissions:
    	# 	members.add(submission['other_1'])
    	# 	members.add(submission['other_2'])
    	# 	# members.add(submission['other_3'])
    	# print members



