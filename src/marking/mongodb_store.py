

__author__ = 'nah'

import pymongo
from bson import Binary


def content_decode(s):

    decoded = s

    if isinstance(s, str):
        decoded = unicode(s.decode('ascii', 'ignore'))

    return decoded

class SubmissionStore():
    """Stores submissions obtained from the Canvas API."""

    def __init__(self, db_host='localhost', db_port=27017):
        """Construct a submission store working with a mongodb server at the given location."""
        self.client = pymongo.MongoClient(db_host, db_port)
        self.users_collection = self.client['users']['users']
        self.users_collection.ensure_index('user_id')

    def _store_single_submission(self, collection, submission, uid = None, key= None):
        # assumption is that there can only be one submission per user in the collection

        if uid is None or key is None:
            if 'user_id' in submission:
                query = {'user_id': submission['user_id']}
            elif 'id' in submission:
                query = {'id': submission['id']}
            elif 'username' in submission:
                query = {'username': submission['username']}
            else:
                query = {'sis_user_id': submission['sis_user_id']}
        else:
            query = {key: uid}
            submission[key] = uid

        collection.update(query, submission, upsert=True)


    def get_assignment_collection(self, course_id, assignment_id):
        """
        Stores the given submissions in the database.

        :param course_id: The id of the course to store the submissions unders
        :param assignment_id:  The id of the assignment to store the assignments unders
        :returns: The mongodb collection for this assignment
        """
        course_id = str(course_id)
        assignment_id = str(assignment_id)
        return self.client[course_id][assignment_id]

    def store_assignment_submissions(self, course_id, assignment_id, submissions, group_category_id = None):
        """
        Stores the given submissions in the database.

        :param course_id: The id of the course to store the submissions unders
        :param assignment_id:  The id of the assignment to store the assignments unders
        :param submissions: The submissions themselves, in JSON format. Can be a single submission or an iterable
        """
        submissions_collection = self.get_assignment_collection(course_id,assignment_id)

        try:
            for submission in submissions:
                submission['assignment_id'] = assignment_id

                if not group_category_id is None:                    
                    storage_id = self.get_group_from_category(course_id, group_category_id, submission['user_id'], key='user_id')
                    storage_key = 'group'
                    # print 'grouping %s for %s' % (storage_id, submission['user_id'])
                else:
                    storage_id = submission['user_id']
                    storage_key = 'user_id'

                self._store_single_submission(submissions_collection, submission, key=storage_key, uid=storage_id)
        except TypeError, te:
            self._store_single_submission(submissions_collection, submissions)

 

    def store_submission_marks(self, course_id, submission, marks_dict):
        course_id = str(course_id)
        assignment_id = str(submission['assignment_id'])

        submissions_collection = self.client[course_id][assignment_id]
        query = {'user_id': submission['user_id']}

        existing_submission = submissions_collection.find_one(query)

        existing_submission['marks'] = marks_dict

        submissions_collection.update(query, existing_submission)

    def get_submission_attachments(self, course_id, submission):

        existing_submission = self.get_stored_submission(course_id, submission['assignment_id'], submission['user_id'])
        attachments = None
        if existing_submission is not None:
            if 'attachment-files' in existing_submission:
                attachments = {}
                att_dict = existing_submission['attachment-files']
                for attachment in att_dict.values():                    
                    attachments[attachment['filename']] = attachment['contents']        

        return attachments

    def store_submission_attachments(self, course_id, submission, attachments):
        course_id = str(course_id)
        assignment_id = str(submission['assignment_id'])

        submissions_collection = self.client[course_id][assignment_id]
        query = {'user_id': submission['user_id']}

        existing_submission = submissions_collection.find_one(query)

        att_dict = {}
        count = 0

        # keys on mongo can't have . or some special characters, so flatten out a bit
        for (k, v) in attachments.iteritems():
            att_dict[str(count)] = {}
            att_dict[str(count)]['filename'] = k            
            # att_dict[str(count)]['contents'] = content_decode(v)
            att_dict[str(count)]['contents'] = Binary(v)
            count += 1

        existing_submission['attachment-files'] = att_dict
        existing_submission['assignment_id'] = submission['assignment_id']

        submissions_collection.update(query, existing_submission)



    def get_submissions_to_mark(self, course_id, assignment_id):
        query = {'$or': [{'grade_matches_current_submission': False}, {'grade': None}]}
        return self.get_assignment_submissions(course_id, assignment_id, query)

    def get_stored_submission(self, course_id, assignment_id, user_id):
        query = {'user_id': user_id}
        result = self.get_assignment_submissions(course_id, assignment_id, query, as_list=False)
        if result.count() > 0:
            return result[0]
        else:
            return None


    def get_assignment_submissions(self, course_id, assignment_id, query={}, as_list=True):
        """
        Retrieves submissions for the given course and assignment from the database. Additionally restricts assignments based on query.

        :param course_id: The course to fetch the submissions from.
        :param assignment_id: The assignment to fetch the submissions from.
        :param query: Restricts returned submissions to those matching this query
        :param as_list: Returns the results as a list, rather than a pymongo Cursor. 
        :return: the matching submissions in JSON format.
        """
        course_id = str(course_id)
        assignment_id = str(assignment_id)

        result = self.client[course_id][assignment_id].find(query)
        if as_list:
            result = list(result)

        return result

    def store_user(self, user):        
        self.users_collection.update({'id': user['id']}, user, upsert=True)
        return user['login_id']

    def store_users(self, users):
        map(self.store_user, users)

    def get_user(self, uid, key='id'):
        return self.users_collection.find_one({key: uid})

    def get_username(self, uid, key='id'):
        user = self.get_user(uid, key)
        if user is None:
            return None
        else:
            return user['login_id']


    def store_group(self, course_id, group, members=None):
        course_id = str(course_id)
        group_category = 'group_' + str(group['group_category_id'])
        if members is not None:
            group['members'] = members

        query = {'id': group['id']}
        self.client[course_id][group_category].update(query, group, upsert=True)

    def get_course_groups(self, course_id, group_category_id, query={}):
        course_id = str(course_id)
        group_category = 'group_' + str(group_category_id)
        return self.client[course_id][group_category].find(query)

    def get_group(self, course_id, group_category_id, group_name):
        course_id = str(course_id)
        group_category = 'group_' + str(group_category_id)
        return self.client[course_id][group_category].find_one({'name': group_name})
 
    def get_group_members(self, course_id, group_category_id, group_name):
        group = self.get_group(course_id, group_category_id, group_name)
        return [member['user_id'] for member in group['members']]


    def get_group_from_category(self, course_id, group_category_id, uid, key='id'):
        course_id = str(course_id)
        group_category = 'group_' + str(group_category_id)        
        for group in self.client[course_id][group_category].find():                        
            for member in group['members']:                                
                if member[key] == uid:
                    return group['name']

        return None

    def _get_key_document(self):
        return self.client['global']['user_data'].find_one(fields=['key'])


    def store_key(self, key):
        key_doc = self._get_key_document()
        global_collection = self.client['global']['user_data']

        if key_doc is None:
            global_collection.insert({'key': key})
        else:
            if key != key_doc['key']:
                print('Updating key')
                query = {'_id' : key_doc['_id']}
                global_collection.update(query, {'key': key})            
            else:
                print('key unchanged')


    def get_key(self):
        key_doc = self._get_key_document()
        if key_doc is None:
            raise Exception('No key stored.')
        else:
            return key_doc['key']