__author__ = 'nah'


def add_comment(mark_dict, comment):
    if 'comment' in mark_dict:
        mark_dict['comment'].append(comment)
    else:
        mark_dict['comment'] = comment


def set_final_mark(mark_dict, final_mark, comment=''):
    mark_dict['final_mark'] = (final_mark, comment)


def add_component_mark(mark_dict, component_mark, comment=''):
    if 'component_marks' not in mark_dict:
        mark_dict['component_marks'] = []

    mark_dict['component_marks'].append((component_mark, comment))
