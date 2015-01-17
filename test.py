

import requests

access_token="1848~N3mmmxpnXbEchYrRMhHBSVzLY6spgJteMxBhumiOHcMqb2R9CrJoyvB1v9FC0ITt"

def get(api, access_token, base_url='https://canvas.bham.ac.uk', api_prefix='/api/v1'):

	url = base_url + api_prefix + api

	if access_token is not None:
		payload = {'access_token': access_token}	
		return requests.get(url, params=payload)
	else:
		return requests.get(url)

def get_courses(access_token):
	courses = get('/courses', access_token).json()
	for course in courses:
		print('%s: %s' % (course['id'], course['name']))

def get_assignments(access_token, course_id):
	assignments = get('/courses/%s/assignments' % course_id, access_token).json()

	for assignment in assignments:
		if 'online_quiz' in assignment['submission_types']:
			print('%s: %s (%s, quiz_id: %s)' % (assignment['id'], assignment['name'], assignment['submission_types'], assignment['quiz_id']))		
		else:
			print('%s: %s (%s)' % (assignment['id'], assignment['name'], assignment['submission_types']))		
		
		# print assignment

def get_quiz_submissions(access_token, course_id, quiz_id):

	submissions = get('/courses/%s/assignments/%s/submissions' % (course_id, quiz_id), access_token).json()
	for submission in submissions:
		print submission


if __name__ == "__main__":
	# print out the names of courses
	# get_courses(access_token)
	test_module_id = '5769'
	get_assignments(access_token, test_module_id)
	# test_quiz_id = '25976'
	# get_quiz_submissions(access_token, test_module_id, test_quiz_id)



