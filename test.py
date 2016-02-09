#!/usr/local/bin/python
# -*- coding: utf- -*-

from marking import canvas_api, mongodb_store, marking_actions
import argparse
from marking.mongodb_store import content_decode
import re
import requests
import csv
import json
import random

from pyevolve import G1DList
from pyevolve import GSimpleGA
from pyevolve import Selectors
from pyevolve import Statistics
from pyevolve import DBAdapters
import pyevolve







store = mongodb_store.SubmissionStore()
capi = canvas_api.CanvasAPI(store.get_key())    

course_id = 15668
quiz_id = 25653
lab_group_category_id = 3854

lab_group = 'Lab Group 3'
# get all the students that are in the lab group


# user names in ascending order
group_members = sorted(store.get_username(uid) for uid in store.get_group_members(course_id, lab_group_category_id, lab_group))

print len(group_members)

# quiz_responses = store.get_assignment_submissions(course_id, quiz_id, query={'username': group_members[0]})

username1_key = '543742: Please enter the CS username of a person in your Lab Group that you would prefer to be in a team with, or leave blank_'
username2_key = '543743: Please enter anotherCS username of a person in your Lab Group that you would prefer to be in a team with, or leave blank_'
second_pref_key = '543554: In my team, mysecondpreference would be to work on the following (please refer to the assignmentfor more details)'
first_pref_key = '543551: In my team, myfirst preference would be to work on the following (please refer to the assignmentfor more details)'
third_pref_key = '543555: In my team, mythirdpreference would be to work on the following (please refer to the assignmentfor more details)'
ability_key = '543556: On a scale of 1 to 5, how do you rate your own coding ability? 5 means that have confidently solved every problem put in front of you this term, 1 means that you often need help to get solutions written, including the basics_'
non_respond_key = 'non_respond'
friends_key = 'friends'
size_key = 'group_size'
no_preference_key = 'No preference'

first_choice_score = 10
second_choice_score = 5
third_choice_score = 1

# Lab Group 1, 55 students
group_count = 5
target_size = 11

# build the list of subproblems
subproblems = set()
for quiz_response in store.get_assignment_submissions(course_id, quiz_id):
    subproblems.add(quiz_response[first_pref_key])
    subproblems.add(quiz_response[second_pref_key])
    subproblems.add(quiz_response[third_pref_key])
# subproblems.remove('No preference')

# score
# for each subproblem: first pref 10, second pref 5, third pref 1
# for each person: 5 per friend match
# team size 10 - abs(11 - size)





def update_subproblem_score(score_dict, subproblem, score, weight):
    score_dict[subproblem] = max(score_dict[subproblem], score * weight)

def update_friend_score(score_dict, friend, score, grouping, my_assignment):                     
    try:
        index = group_members.index(friend.lower())
        if grouping[index] == my_assignment:            
            score_dict[friends_key] += score
    except ValueError, e:
        pass


# This function is the evaluation function, we want
# to give high score to more zero'ed chromosomes
def score_grouping(grouping):

  
    # the dirctionary structure for storing scores for teams
    score_dict = {subproblem: 0 for subproblem in subproblems}
    score_dict[non_respond_key] = 0
    score_dict[friends_key] = 0
    score_dict[size_key] = 0

    group_scores = {group: score_dict.copy() for group in range(1, group_count+1)}
    # print group_scores

    for i in range(len(grouping)):
        assignment = grouping[i]
        username = group_members[i]
        subproblem_scores = group_scores[assignment]            
        subproblem_scores[size_key] += 1

        # print group_members

        quiz_response = store.get_assignment_submissions(course_id, quiz_id, query={'username': username})
        if len(quiz_response) == 0:
            # penalise multiple non responders in a group
            subproblem_scores[non_respond_key] += 1
        else:
            quiz_response = quiz_response[0]
            coding_ability = int(quiz_response[ability_key])
            update_subproblem_score(subproblem_scores, quiz_response[first_pref_key], first_choice_score, coding_ability)
            update_subproblem_score(subproblem_scores, quiz_response[second_pref_key], second_choice_score, coding_ability)
            update_subproblem_score(subproblem_scores, quiz_response[third_pref_key], third_choice_score, coding_ability)
            update_friend_score(subproblem_scores, quiz_response[username1_key], second_choice_score, grouping, assignment)
            update_friend_score(subproblem_scores, quiz_response[username2_key], second_choice_score, grouping, assignment)
            

    # determine size score
    for group, subproblem_scores in group_scores.iteritems():
        size_score = target_size * (first_choice_score + first_choice_score)
        assigned_size = subproblem_scores[size_key] * (first_choice_score + first_choice_score)
        subproblem_scores[size_key] = size_score - abs(size_score - assigned_size)
        # print subproblem_scores[size_key]

    # compute final scores -- 
    final_score = 0
    for group, subproblem_scores in group_scores.iteritems():
        group_score =  0
        for subproblem, subproblem_score in subproblem_scores.iteritems():
            if subproblem == non_respond_key:                
                # We want to penalise the number of non-respondents who are grouped together
                group_score -= pow(subproblem_score * second_choice_score, 2)
            else:
                group_score += subproblem_score
        # print 'group %s score %s' % (group, group_score)
        final_score += group_score
    
    if  final_score < 0:
        final_score = 0

    # print final_score

    return final_score


def make_grouping(grouping):
    groupings = []
    for i in range(group_count):
        groupings.append([])
    
    for i in range(len(grouping)):
        assignment = grouping[i]
        username = group_members[i]
        groupings[assignment-1].append(username)
        
    return groupings


def make_annotated_group(group):
    annotated_group = {subproblem: [[],[],[]] for subproblem in subproblems}

    for username in group:
        quiz_response = store.get_assignment_submissions(course_id, quiz_id, query={'username': username})
        if len(quiz_response) == 1:
            quiz_response = quiz_response[0]
            annotated_group[quiz_response[first_pref_key]][0].append(username)
            annotated_group[quiz_response[second_pref_key]][1].append(username)
            annotated_group[quiz_response[third_pref_key]][2].append(username)            
    return annotated_group




def print_annotated_group(members, group):

    print 'Members: %s\n' % ', '.join(members)

    for subproblem, choices in group.iteritems():   
        if not subproblem == no_preference_key:
            print '### %s' % subproblem
            print ' 1. %s' % (', '.join(choices[0]))
            print ' 2. %s' % (', '.join(choices[1]))
            print ' 3. %s' % (', '.join(choices[2]))

    print '\n'

# example = [random.randint(1,group_count) for num in range(len(group_members))]



# Enable the pyevolve logging system
pyevolve.logEnable()

genome = G1DList.G1DList(len(group_members))

genome.setParams(rangemin=1, rangemax=5)

genome.evaluator.set(score_grouping)

ga = GSimpleGA.GSimpleGA(genome)

# Set the Roulette Wheel selector method, the number of generations and
# the termination criteria
ga.selector.set(Selectors.GRouletteWheel)
ga.setGenerations(5000)
ga.terminationCriteria.set(GSimpleGA.ConvergenceCriteria)

# Sets the DB Adapter, the resetDB flag will make the Adapter recreate
# the database and erase all data every run, you should use this flag
# just in the first time, after the pyevolve.db was created, you can
# omit it.
sqlite_adapter = DBAdapters.DBSQLite(identify="ex1")
ga.setDBAdapter(sqlite_adapter)

# Do the evolution, with stats dump
# frequency of 20 generations
ga.evolve(freq_stats=10)

print ga.bestIndividual() # Best individual
groupings = make_grouping(ga.bestIndividual())
annotated_groups = map(make_annotated_group, groupings)

print '# Groupings for %s\n' % lab_group
for i in range(len(groupings)):
    print '## Group: %s.%s\n' % (lab_group,i+1)
    print_annotated_group(groupings[i], annotated_groups[i])

