__author__ = 'nah'


def set_part(mark_dict, part):
    # if current part exists, need to track

    if 'parts_order' not in mark_dict:
        mark_dict['parts_order'] = [part]
    else:
        mark_dict['parts_order'].append(part)


    mark_dict['current_part'] = part

    mark_dict['parts'][part] = {}


def current_part(mark_dict):
    if 'parts' not in mark_dict:
        mark_dict['parts'] = {}

    if 'current_part' not in mark_dict:
        set_part(mark_dict, '')

    return mark_dict['parts'][mark_dict['current_part']]



def add_comment(mark_dict, comment):
    if 'comment' in current_part(mark_dict):
        current_part(mark_dict)['comment'] += comment
    else:
        current_part(mark_dict)['comment'] = comment


def set_final_mark(mark_dict, final_mark, comment=''):
    current_part(mark_dict)['final_mark'] = (final_mark, comment)


def add_component_mark(mark_dict, component_mark, comment=''):
    if 'component_marks' not in current_part(mark_dict):
        current_part(mark_dict)['component_marks'] = []

    current_part(mark_dict)['component_marks'].append((component_mark, comment))

    # def apply_mark_fn(mark_fn, mark_dict, component_mark, success_comment='', failure_comment=''):
    #
    # success = mark_fn(mark_dict, component_mark)
    #     if success:
    #         add_component_mark(mark_dict, component_mark, success_comment)
    #     else:
    #         add_component_mark(mark_dict, 0, failure_comment)
    #
    #     return success