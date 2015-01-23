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
    mark_dict['final_mark'] = (final_mark, comment)


def add_component_mark(mark_dict, component_mark, comment=''):
    if 'component_marks' not in current_part(mark_dict):
        current_part(mark_dict)['component_marks'] = []

    current_part(mark_dict)['component_marks'].append((component_mark, comment))

def aggregate_marks(mark_dict):
    if 'final_mark' in mark_dict:
        return mark_dict['final_mark'][0], mark_dict['final_mark'][1]

    parts = mark_dict['parts_order']
    comment = ''
    mark = 0
    for part in parts:
        comment += part + '\n'
        
        part_components = mark_dict['parts'][part]

        

        if 'comment' in part_components:
            comment += part_components['comment'] + '\n'

        if 'component_marks' in part_components:
            # print part_components
            for component in part_components['component_marks']:
                mark += component[0]
                try:
                    comment += component[1] + '\n'
                except UnicodeDecodeError, e:
                    print 'failed to concat comment, ', component[1]


    return mark, comment