__author__ = 'nah'

from git import Repo


def clone_repo(git_url, repo_dir):
    repo = Repo.clone_from(git_url, repo_dir)
    return repo
