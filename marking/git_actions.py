__author__ = 'nah'

from git import Repo


def clone_repo(git_url, repo_dir):
    repo = Repo.clone_from(git_url, repo_dir)
    return repo


def get_last_commit(repo):
    head = repo.head  # the head points to the active branch/ref
    master = head.reference  # retrieve the reference the head points to
    return master.commit

def get_commit_log(repo):
    head = repo.head
    master = head.reference
    log = master.log()
    return log
