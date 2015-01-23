__author__ = 'nah'

import time
import shutil
import os

from concurrent import futures
from git import Repo


def wait_then_return(i):
    print('called: %s', i)
    time.sleep(2)
    return i


def clone_then_return(i):
    print('called: %s', i)
    path = os.path.join('/tmp', str(i))
    os.mkdir(path)
    # clone some arbitrary repo
    Repo.clone_from('https://github.com/ros/rosdistro', path)
    shutil.rmtree(path)
    return i


if __name__ == "__main__":

    tasks = 20
    workers = 4

    with futures.ThreadPoolExecutor(max_workers=workers) as executor:

        # this works as expected... delaying work until a thread is available
        # fs = [executor.submit(wait_then_return, i) for i in range(0, tasks)]
        # this doesn't... all 20
        fs = [executor.submit(clone_then_return, i) for i in range(0, tasks)]

        for future in futures.as_completed(fs):
            print('result: %s', future.result())

