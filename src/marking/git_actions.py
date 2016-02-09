__author__ = 'nah'

import os
import threading
from time import sleep

from git import Repo


lock = threading.Lock()

def clone_repo(git_url, repo_dir):
    assert os.path.exists(repo_dir)

    repo = None 

    tries = 0
    tries_limit = 5
    delay_secs = 2


    # delayed retries seem to help with occasional network issues
    while repo is None and tries < tries_limit:
        try:
            lock.acquire()
            tries += 1            
                            
            repo = Repo.clone_from(git_url, repo_dir)
        except Exception, e:
            print e        
            sleep(tries * delay_secs)

            # Gitlab doesn't seem to like you leaving off .git
            if git_url.startswith('http') and not (git_url.endswith('.git') or git_url.endswith('.git/')):
                git_url += '.git'

        finally:
            lock.release()
    return repo
        
def clone_repo_at_commit(git_url, branch, commit, repo_dir):
    repo = clone_repo(git_url, repo_dir)
    if repo is not None:
        repo.create_head('branch_for_testing', commit)
        repo.heads.branch_for_testing.checkout()
        # print repo
    return repo

def get_last_commit(repo):
    head = repo.head  # the head points to the active branch/ref
    master = head.reference  # retrieve the reference the head points to
    return master.commit


# import file_actions
#
# def clone_repo(git_url, repo_dir):
# # print to_ssh_url(git_url)
#     success, output = file_actions.run_process('git clone %s .' % to_ssh_url(git_url), repo_dir)
#     # print success, output
#     return success, output
#
# def get_last_commit(repo_dir):
#     success, output = file_actions.run_process('git log -1')
#     if success:
#         return output.split()[1]
#     else:
#         return ''


def to_ssh_url(url):
    # https://git.cs.bham.ac.uk/mjo405/git-exercise.git
    # git@git.cs.bham.ac.uk:mjo405/git-exercise.git

    if url.startswith('git@'):
        return url

    if url.startswith('https'):
        url = url[8:]
        #         git.cs.bham.ac.uk/mjo405/git-exercise.git
        slash_index = url.find('/')
        git_index = url.find('.git')
        return 'git@' + url[:slash_index] + ':' + url[slash_index + 1:git_index + 4]



