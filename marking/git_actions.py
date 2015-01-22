__author__ = 'nah'

from git import Repo


def clone_repo(git_url, repo_dir):
    repo = Repo.clone_from(git_url, repo_dir)
    return repo


def get_commit_log(repo):
    # head = repo.head
    # master = head.reference
    # log = master.log()
    # print log
    # return log
    for commit in repo.iter_commits('master'):
        print commit.author.name
        print commit.author.email
        print commit.committer
        print commit.message