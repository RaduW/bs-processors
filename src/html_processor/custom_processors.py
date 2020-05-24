from typing import Tuple, Callable, Any

from html_processor.generic_processors import (
    filter_factory, unwrap_factory, flatten_factory, local_modify_factory,
    lateral_effect_factory, join_children_factory,
)
from html_processor.processor_util import process
from html_processor.xml_util import is_empty, set_new_children, join_children, collect_children

_remove_empty_elements = frozenset(['p', 'div', 'br'])
_unwrap_elements = frozenset(['font'])
_elements_who_hold_all_children = frozenset(['html', 'body', 'header'])
_block_elements_that_pop_out = frozenset(["p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "pre", "hr", "br"])


def _is_unwanted_element(elm) -> bool:
    """
    Returns True if the elment is unwanted (i.e. should be removed from output).

    >>> from lxml import etree
    >>> elm = etree.XML('<root><br id="1"/>abc <p id="2">with text</p><p id="3"><span>with child</span></p>' +
    ... '<p id="4"></p>with tail<p id="5"></p></root>')
    >>> br = elm[0]
    >>> br.attrib['id']
    '1'
    >>> _is_unwanted_element(br)  # can't remove, non empty tail
    False
    >>> p2 = elm[1]
    >>> _is_unwanted_element(p2) # can't remove, non empty text
    False
    >>> p3 = elm[2]
    >>> _is_unwanted_element(p3) # can't remove, contains children
    False
    >>> p4 = elm[3]
    >>> _is_unwanted_element(p4) # can't remove, non empty tails
    False
    >>> p5 = elm[4]  # can remove, empty with no tail
    >>> _is_unwanted_element(p5)
    True
    """
    if elm.tag in _remove_empty_elements:
        if is_empty(elm.text) and is_empty(elm.tail) and len(elm) == 0:
            return True
    return False


def _should_unwrap_element(elm) -> bool:
    """
    Returns True if the elment should be remove and its contents pushed into the parent

    >>> from lxml import etree
    >>> elm = etree.XML('<root><br id="1"/>abc <font id="2">with text</font></root>')
    >>> br = elm[0]
    >>> _should_unwrap_element(br)
    False
    >>> font = elm[1]
    >>> _should_unwrap_element(font)
    True

    """
    if elm.tag in _unwrap_elements:
        return True
    return False


def should_flatten(elm) -> bool:
    """
    Returns True if the element should be flattened (i.e. the children should be pulled out)

    >>> from lxml import etree
    >>> elm = etree.XML('<html><p id="1">abc</p> <span id="2">with text</span></html>')
    >>> html = elm
    >>> should_flatten(html)
    False
    >>> p = elm[0]
    >>> should_flatten(p)
    True
    >>> span = elm[1]
    >>> should_flatten(span)
    False
    """
    if elm.tag in _elements_who_hold_all_children:
        return False
    if elm.tag in _block_elements_that_pop_out:
        return True
    return False


def stays_inside_parent(elm) -> bool:
    """
    Returns True if the element pops out when flatten (if the element is a block element)

    >>> from lxml import etree
    >>> elm = etree.XML('<html><p id="1">abc</p> <span id="2">with text</span></html>')
    >>> p = elm[0]
    >>> stays_inside_parent(p)
    False
    >>> span = elm[1]
    >>> stays_inside_parent(span)
    True

    """
    if elm.tag not in _block_elements_that_pop_out:
        return True
    else:
        return False


def _index_generator() -> Tuple[Callable[[Any], int], Callable[[], None]]:
    """
    Returns a double containing a function that sets increasing ids to elements
    and a reset function for the counter

    >>> from lxml import etree
    >>> add_idx, reset_idx = _index_generator()
    >>> elm = etree.XML("<root><p>hello</p></root>")
    >>> p = elm[0]
    >>> etree.tostring(p)
    b'<p>hello</p>'
    >>> add_idx(p)
    >>> etree.tostring(p)
    b'<p id="1">hello</p>'
    >>> add_idx(p)
    >>> etree.tostring(p)
    b'<p id="2">hello</p>'
    >>> add_idx(p)
    >>> etree.tostring(p)
    b'<p id="3">hello</p>'
    >>> reset_idx()  # resetting id back to 1
    >>> add_idx(p)
    >>> etree.tostring(p)
    b'<p id="1">hello</p>'
    """
    idx = [1]

    def add_index_to_p(elm):
        if elm.tag == "p":
            elm.attrib['id'] = str(idx[0])
            idx[0] += 1

    def reset_index():
        idx[0] = 1

    return add_index_to_p, reset_index


def join_div_with_ul_inside(elm_l, elm_r):
    """
    Tries to join two elements
    :param elm_l: left child
    :param elm_r: right child
    :return: the result of joining (iterator with either 1 or 2 elm)

    >>> from lxml import etree
    >>> elm = etree.XML("<root><div id='1'><ul id='2'><li>first</li><li>second</li></ul></div>" +
    ... "<div id='11'><ul id='12'><li>third</li><li>fourth</li></ul></div></root>")
    >>> result = list(join_div_with_ul_inside(elm[0],elm[1]))
    >>> len(result)
    1
    >>> etree.tostring(result[0])
    b'<div id="1"><ul id="2"><li>first</li><li>second</li><li>third</li><li>fourth</li></ul></div>'
    >>> etree.tostring(elm)
    b'<root><div id="1"><ul id="2"><li>first</li><li>second</li><li>third</li><li>fourth</li></ul></div>\
<div id="11"><ul id="12"/></div></root>'
    """
    if (
        elm_l.tag == "div" and elm_r.tag == "div" and  # join p elements
        len(elm_l) == 1 and len(elm_r) == 1 and  # that have only one child each
        elm_l[0].tag == 'ul' and elm_r[0].tag == 'ul' and  # and the children are ul
        is_empty(elm_l.tail) and is_empty(elm_r.text) and  # no text between p
        is_empty(elm_l[0].tail) and is_empty(elm_r[0].tail)
    ):
        p_l = elm_l
        p_r = elm_r
        ul_l = elm_l[0]
        # get the li elements
        li_elms = list(collect_children([p_l,p_r], 2))
        # set all the li elements inside the ul left element
        set_new_children(ul_l, li_elms)
        # joined left and right, return the joined element (the left elm)
        yield p_l
    else:
        # do NOT join, just return the existing elements
        yield elm_l
        yield elm_r


unwrap_unwanted_elements = unwrap_factory(_should_unwrap_element)
remove_unwanted_elements = filter_factory(_is_unwanted_element)
flatten_block_elements = flatten_factory(should_flatten, stays_inside_parent)
join_lists = join_children_factory(join_div_with_ul_inside)


def clean_html(elm):
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
