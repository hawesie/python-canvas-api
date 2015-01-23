__author__ = 'nah'

import os
import shutil

import subprocess32

import marks


class SubmissionDirectory(object):
    """Directory to work in"""

    def __init__(self, submission, path='/tmp'):
        """Constructor for SubmissionDirectory"""
        self.path = os.path.join(path, str(submission['assignment_id']), str(submission['user_id']))

    def __enter__(self):
        os.makedirs(self.path)
        assert os.path.exists(self.path)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            shutil.rmtree(self.path)
        except OSError, e:
            pass

def file_exists(file_path, base_path=None):
    if base_path is not None:
        file_path = os.path.join(base_path, file_path)

    return os.path.exists(file_path)


def make_empty(file_path, base_path=None):
    """
    Creates an emptu directory. If the specified directory exists, it removes it before making it again (so use with caution).
    :param file_path:
    :param base_path:
    :return:
    """
    if base_path is not None:
        file_path = os.path.join(base_path, file_path)

    if file_exists(file_path):
        shutil.rmtree(file_path)

    assert not file_exists(file_path)

    return os.makedirs(file_path)


def run_process(cmd, cwd):
    try:
        output = subprocess32.check_output(cmd, cwd=cwd, stderr=subprocess32.STDOUT, shell=True)
        success = True
    except subprocess32.CalledProcessError, e:
        output = e.output
        success = False

    return success, output.strip()


def mark_process(cmd, cwd, mark_dict, component_mark, success_comment='', failure_comment=''):

    success, output = run_process(cmd, cwd)

    if success:
        marks.add_component_mark(mark_dict, component_mark, 'Successfully ran "%s". %s' % (cmd, success_comment))

    else:
        marks.add_component_mark(mark_dict, 0,
                                 'Could not run "%s". Output was "%s". %s' % (cmd, output, failure_comment))

    return success, output


def mark_process_output(cmd, cwd, expected_output, mark_dict, component_mark, success_comment='', failure_comment=''):
    success, output = mark_process(cmd, cwd, mark_dict, 0, success_comment, failure_comment)

    if success:

        if expected_output.lower() == output.lower():
            marks.add_component_mark(mark_dict, component_mark,
                                     'Output of "%s" matched "%s". %s' % (cmd, expected_output, success_comment))
        else:
            marks.add_component_mark(mark_dict, component_mark,
                                     'Output of "%s" was "%s" which does not match expected output "%s". %s' % (
                                     cmd, output, expected_output, failure_comment))

    else:
        marks.add_component_mark(mark_dict, 0,
                                 'Could not run "%s" so could not test output. %s' % (cmd, failure_comment))

    return success, output


def mark_file(file_path, base_path, mark_dict, component_mark, mark_fn):
    if base_path is not None:
        file_path = os.path.join(base_path, file_path)

    try:
        with open(file_path, 'r') as f:
            mark_fn(f, mark_dict)

    except IOError, e:
        marks.add_component_mark(mark_dict, 0, 'File "%s" could not be opened for marking.' % file_path)


def match_file_line(f, get_line_fn, line_match_fn, mark_dict, component_mark, pattern_str=None):
    line = get_line_fn(f)

    if line is None:
        marks.add_component_mark(mark_dict, 0, 'An appropriate line could not be found in your file.')
    else:
        if line_match_fn(line):
            mk = component_mark
            comment = 'File line "%s" matches expected pattern.' % line

        else:
            mk = 0
            comment = 'File line "%s" does not match the expected pattern.' % line

        if pattern_str is not None:
            comment += ' Expected pattern was "%s"' % pattern_str

        marks.add_component_mark(mark_dict, component_mark, comment)


