__author__ = 'nah'

from marking import canvas_api, mongodb_store, print_courses


if __name__ == "__main__":
    access_token = "1848~N3mmmxpnXbEchYrRMhHBSVzLY6spgJteMxBhumiOHcMqb2R9CrJoyvB1v9FC0ITt"
    capi = canvas_api.CanvasAPI(access_token)
    store = mongodb_store.SubmissionStore()

    # courses = capi.get_courses()
    # print_courses(courses)

    rp = 9779
    course_id = rp

    lab_group_category = 2835
    team_category = 2836
    
    # for group in capi.get_course_groups(course_id):
    #    store.store_group(course_id, group, capi.get_group_membership(group['id']))


    # for each group in lab_group_category print out each group with members in team_category
    lab_groups = map(lambda group: (group['name'], set(map(lambda member: member['user_id'], group['members']))), store.get_course_groups(course_id, lab_group_category))
    teams = map(lambda group: (group['name'], set(map(lambda member: member['user_id'], group['members']))), store.get_course_groups(course_id, team_category))

    for team in teams:
        print team[0]
        team_group = None
        for member in team[1]:
            for group in lab_groups:
                if member in group[1]:
                    if team_group is not None and team_group != group[0]:
                        print 'problem team: ', team[0]
                    team_group = group[0]


    # teams = list(store.get_course_groups(course_id, team_category))

    # for team in teams:

