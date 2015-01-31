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


    # update groups from Canvas
    # for group in capi.get_course_groups(course_id):
    #    store.store_group(course_id, group, capi.get_group_membership(group['id']))


    # for each group in lab_group_category print out each group with members in team_category
    lab_groups = map(lambda group: (group['name'], set(map(lambda member: member['user_id'], group['members']))), store.get_course_groups(course_id, lab_group_category))
    teams = map(lambda group: (group['name'], set(map(lambda member: member['user_id'], group['members']))), store.get_course_groups(course_id, team_category))

    team_groups = []
    for team in teams:
        # print team[0]
        team_group = set()
        for member in team[1]:
            for group in lab_groups:
                if member in group[1]:
                    team_group.add(group[0])
        team_groups.append((team[0], team_group))

    problem_teams = [tg for tg in team_groups if len(tg[1]) != 1]
    if len(problem_teams) > 0 or len(problem_teams) == 1:
        print('problem teams: %s' % problem_teams)
    else:

        print team_groups

        lab_teams = dict()
        for tg in team_groups:
            lab = tg[1].pop()
            if lab not in lab_teams:
                lab_teams[lab] = set()
            lab_teams[lab].add(tg[0])


        for k, v in lab_teams.iteritems():
            print k
            for team in v:
                print team


