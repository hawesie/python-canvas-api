
import urllib
import requests
import os 

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

	submissions = get('/courses/%s/quizzes/%s/submissions' % (course_id, quiz_id), access_token)
	for submission in submissions:
		print submission


def get_assignment_submissions(access_token, course_id, assignment_id, save_files=True, save_prefix='/tmp'):

	file_saver = urllib.URLopener()
	
	submissions = get('/courses/%s/assignments/%s/submissions' % (course_id, assignment_id), access_token).json()

	assignment_path = os.path.join(os.path.join(save_prefix, course_id), assignment_id)

	if save_files:
		try:
			print('Saving to %s' % assignment_path)
			os.makedirs(assignment_path)
		except Exception, e:
			print(e)
		
	for submission in submissions:
		print submission
		for attachment in submission['attachments']:
			r = requests.get(attachment['url'], params={'access_token': access_token})
			with open(os.path.join(assignment_path, attachment['filename']), 'w') as f:
				f.write(r.text)
			

if __name__ == "__main__":
	# print out the names of courses
	# get_courses(access_token)
	test_module_id = '5769'
	get_assignments(access_token, test_module_id)
	test_assignment_id = '26001'
	get_assignment_submissions(access_token, test_module_id, test_assignment_id)

	# todo
	# to get the contents of a quiz you need to generate a report then download the csv report file
	# test_quiz_id = '16929'
	# get_quiz_submissions(access_token, test_module_id, test_quiz_id)



