__author__ = 'nah'

import os
import fnmatch

import marks
import file_actions


def compile_java_class(class_name, package, cwd, marks_dict, component_mark, src_dir='src', bin_dir='bin'):
    file_actions.make_empty(bin_dir, cwd)

    to_find = class_name + '.java'

    # find filenames which match the required class
    matches = []
    for root, dirnames, filenames in os.walk(cwd):
        for filename in fnmatch.filter(filenames, to_find):
            full_path = os.path.join(root, filename)
            rel_from_root = full_path[len(cwd) + 1:]
            matches.append(rel_from_root)

    if len(matches) == 0:
        marks.add_component_mark(marks_dict, -1, 'No file %s found in repository' % to_find)
        return False, ''
    else:
        java_file = matches[0]

        expected_file_path = os.path.join(src_dir, package.replace('.', os.sep), class_name + '.java')

        if java_file != expected_file_path:
            marks.add_component_mark(marks_dict, -0.5,
                                     'Incorrect file structure. I was expecting your code to be layed out as ./%s but yours was ./%s' % (
                                     expected_file_path, java_file))

        compile = 'javac -d bin %s' % java_file

        return file_actions.mark_process(compile, cwd, marks_dict, component_mark), java_file


def run_java_class(class_name, package, cwd, compiled_file, marks_dict, component_mark, src_dir='src', bin_dir='bin',
                   expected_output=None):
    command = 'java -classpath ' + bin_dir + ' ' + package + '.' + class_name

    if expected_output is not None:
        success, output = file_actions.mark_process_output(command, cwd, expected_output, marks_dict, component_mark)
    else:
        success, output = file_actions.mark_process(command, cwd, marks_dict, component_mark)

    if not success:
        # if the specified class failed, try to infer class from compiled file

        # strip src prefix
        compiled_file = compiled_file[len(src_dir) + 1:]
        compiled_file.replace(os.sep, '.')
        compiled_file.replace('.java', '')
        command = 'java -classpath ' + bin_dir + ' ' + compiled_file

        if expected_output is not None:
            success, output = file_actions.mark_process_output(command, cwd, expected_output, marks_dict,
                                                               component_mark,
                                                               success_comment='Mismatch between file structure and package structure, hence previous failure.')
        else:
            success, output = file_actions.mark_process(command, cwd, marks_dict, component_mark,
                                                        success_comment='Mismatch between file structure and package structure, hence previous failure.')

    return success, output