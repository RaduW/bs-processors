from html_processor.generic_processors import (
    filter_factory, unwrap_factory, flatten_factory, local_modify_factory,
    lateral_effect_factory, join_children_factory,
)
from html_processor.processor_util import process
from html_processor.xml_util import is_empty, set_new_children

_unconditionally_remove = frozenset(['br'])
_remove_empty_elements = frozenset(['p', 'div'])
_unwrap_elements = frozenset(['font'])
_elements_who_hold_all_children = frozenset(['html', 'body', 'header'])
_block_elements_that_pop_out = frozenset(["p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "pre", "hr", "br"])


def _is_unwanted_element(elm):
    # unconditionally remove
    if elm.tag in _unconditionally_remove:
        return True

    if elm.tag in _remove_empty_elements:
        if is_empty(elm.text) and is_empty(elm.tail) and len(elm) == 0:
            return True
    return False


def _should_unwrap_element(elm):
    if elm.tag in _unwrap_elements:
        return True
    return False


def should_flatten(elm):
    if elm.tag in _elements_who_hold_all_children:
        return False
    if elm.tag in _block_elements_that_pop_out:
        return True
    return False


def stays_inside_parent(elm):
    if elm.tag not in _block_elements_that_pop_out:
        return True
    else:
        return False


def _index_generator():
    idx = [1]

    def add_index_to_p(elm):
        if elm.tag == "p":
            elm.attrib['id'] = str(idx[0])
            idx[0] += 1

    def reset_index():
        idx[0] = 1

    return add_index_to_p, reset_index


def join_p_with_ul_inside(elm_l, elm_r):
    """
    Tries to join two elements
    :param elm_l: left child
    :param elm_r: right child
    :return: the result of joining (iterator with either 1 or 2 elm)

    >>> from lxml import etree
    >>> elm = etree.XML("<root><p><ul><li>first</li><li>second</li></ul></p><p><ul><li>third</li><li>fourth</li></ul></p></root>")
    >>> result = list(join_p_with_ul_inside(elm[0],elm[1]))
    >>> len(result)
    1
    >>> etree.tostring(result[0])
    b'<p><li>first</li><li>second</li><li>third</li><li>fourth</li></p>'

    """
    if (
        elm_l.tag == "p" and elm_r.tag == "p" and  # join p elements
        len(elm_l) == 1 and len(elm_r) == 1 and  # that have only one child each
        elm_l[0].tag == 'ul' and elm_r[0].tag == 'ul' and  # and the children are ul
        is_empty(elm_l.tail) and is_empty(elm_r.text) and  # no text between p
        is_empty(elm_l[0].tail) and is_empty(elm_r[0].tail)
    ):
        # put inside ul the children from ul left and ul right
        set_new_children(elm_l, list(elm_l[0]) + list(elm_r[0]))
        # joined left and right, return the joined element (the left elm)
        yield elm_l
    else:
        # do NOT join, just return the existing elements
        yield elm_l
        yield elm_r


unwrap_unwanted_elements = unwrap_factory(_should_unwrap_element)
remove_unwanted_elements = filter_factory(_is_unwanted_element)
flatten_block_elements = flatten_factory(should_flatten, stays_inside_parent)
join_lists = join_children_factory(join_p_with_ul_inside)


def clean_html( elm):
    # defined  inside for thread safety
    add_index_to_p, reset_index = _index_generator()
    add_indexes_to_p = local_modify_factory(add_index_to_p)
    reset_index_counter = lateral_effect_factory(reset_index)

    elms = process(elm, [
        unwrap_unwanted_elements,  # unwrap fonts and stuff
        flatten_block_elements,
        remove_unwanted_elements,  # remove empty or unused tags
        join_lists,  # joins lists on adjacent p
        add_indexes_to_p,  # put increasing indexes on p
        reset_index_counter  # reset index counter so next time we start again from 1
    ])

    elms = list(elms)

    if len(elms) != 1:
        raise ValueError("Processing went wrong expected 1 element got {}", len(elm))

    return elms[0]
