#!/usr/bin/env python
# -*- coding: utf- -*-

from marking import canvas_api, mongodb_store
import argparse



if __name__ == "__main__":

    store = mongodb_store.SubmissionStore()

    parser = argparse.ArgumentParser(description='Print user details') 
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-u', '--username', help='CS username', type=str)
    group.add_argument('-n', '--name', help='Real name contains', type=str)
    group.add_argument('-s', '--sis_user_id', help='User id', type=str)

    args = parser.parse_args()     
            
    if args.username:
        print(store.get_user(args.username, 'sis_login_id'))
    elif args.sis_user_id:
        print(store.get_user(args.sis_user_id, 'sis_user_id'))
    elif args.name:
        for name in store.users_collection.find({'name' : {'$regex' : '.*%s.*' % args.name}}):
            print(name)

