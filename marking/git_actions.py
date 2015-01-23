__author__ = 'nah'

from git import Repo


def clone_repo(git_url, repo_dir):
    # print to_ssh_url(git_url)
    try:
        repo = Repo.clone_from(to_ssh_url(git_url), repo_dir)
    except Exception, e:
        return None

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



