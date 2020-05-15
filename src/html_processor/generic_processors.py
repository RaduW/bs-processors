""" processors for xml elements

A processor is a function that receives an element and returns a generator of elements.
It may return:
    - a generator with one element (typical case of an element transformer)
    - a generator with 0 elements ( typical case for a filter that returns either one or zero elemeents)
    - a generator with multipel elements ( a flatten function that takes the elements out of an element with embedded
    elms)
"""
import string
from collections import namedtuple
from typing import Any, Callable

from lxml import etree
import functools

import logging

_log = logging.getLogger(__name__)

from html_processor.xml_util import remove_children, set_new_children, generate_new_children, is_empty, join_strings


def filter_gen(should_filter: Callable[[Any], bool], elm):
    """
    Generator for filtering a hierarchical structure.
    It will go deep and apply the filter to the children
    :param should_filter: predicate indicating if an element should be filtered
    :param elm: the element
    :return: an iterator of elements containing either the passed element (potentially with some of
    its children filtered or an empty iterator if the element was filtered

    >>> from lxml import etree
    >>> doc = etree.XML('<root><a><b/></a><c><a/></c><d/><b/></root>')
    >>> should_filter= lambda elm: elm.tag == 'a'
    >>> result = list(filter_gen(should_filter, doc))
    >>> len(result)
    1
    >>> etree.tostring(result[0])
    b'<root><c/><d/><b/></root>'

    """
    if should_filter(elm):
        return []
    new_children = generate_new_children(lambda child: filter_gen(should_filter, child), elm)
    set_new_children(elm, new_children)
    yield elm


def filter_factory(should_filter):
    return functools.partial(filter_gen, should_filter)


def flatten_gen(flatten_children: Callable[[Any], bool], is_internal: Callable[[Any], bool], elm):
    new_children = generate_new_children(lambda child: flatten_gen(flatten_children, is_internal, child), elm)
    remove_children(elm)

    if not flatten_children(elm):
        # all children should go inside
        for child in new_children:
            elm.append(child)
        yield elm
    else:
        # this element pops out external children
        # remember the current parent
        parent = elm

        for child in new_children:
            # decide whether to add the child to the parent of to flatten it
            if is_internal(child):
                if parent is None:
                    # copy the element type
                    parent = etree.Element(elm.tag)
                parent.append(child)
            else:
                # we need to pop it at higher level, return current parent and then child
                if parent is not None:
                    yield parent
                    parent = None  # we returned it so there is no current parent
                # deal with the lxml tail nastiness (the tail of an element belongs to the parent)
                if child.tail is not None:
                    # the child that we want to pop out has a tail, we'll create a new parent to
                    # hang the tail in
                    parent = etree.Element(elm.tag)
                    parent.text = child.tail
                    child.tail = None
                yield child

        #  if we still have a parent (i.e. the last child was not flattened or no children, return the parent)
        if parent is not None:
            yield parent


def flatten_factory(should_flatten, should_flatten_children):
    return functools.partial(flatten_gen, should_flatten, should_flatten_children)


def local_modify_gen(modify_func: Callable[[Any], bool], elm):
    """

    :param modify_func: a function that modifies the current element will be called for
        the element and all children.
    :param elm:  the element to modify
    :return: a generator containing only the passed element

    >>> from lxml import etree
    >>> idx = [0]
    >>> def add_id_to_p( elm):
    ...     if elm.tag == 'p':
    ...         idx[0] += 1
    ...         elm.attrib['id'] = str(idx[0])
    ...
    >>> elm = etree.XML('<root><p><x><p/></x></p><a/><p></p></root>')
    >>> result = list(local_modify_gen(add_id_to_p, elm))
    >>> len(result)
    1
    >>> etree.tostring(result[0])
    b'<root><p id="1"><x><p id="2"/></x></p><a/><p id="3"/></root>'

    """
    modify_func(elm)
    for child in elm:
        for x in local_modify_gen(modify_func, child):
            pass
    yield elm


def local_modify_factory(modify_func):
    return functools.partial(local_modify_gen, modify_func)

def unwrap_gen(should_unwrap: Callable[[Any], bool], elm):
    """
    Removes an element while inserting the children in to the parent (at the position where
    the element used to be)

    :param should_unwrap: true if the current element should be deleted and its children pushed up
    :param elm: the elment to anaylze
    :return: generator yielding either the element or the children of the element

    >>> def should_unwrap_font(elm):
    ...     if elm.tag in ['f', 'font', 'fnt']:
    ...         return True
    ...     return False
    ...
    >>> elm = etree.XML('<root><font><font><p id="1">abc</p><font><p id="2">123</p></font></font></font></root>')
    >>> result = list(unwrap_gen(should_unwrap_font, elm))
    >>> len(result)
    1
    >>> etree.tostring(result[0])
    b'<root><p id="1">abc</p><p id="2">123</p></root>'

    """
    head, elms = _unwrap_internal(should_unwrap, elm)

    if not is_empty(head):
        _log.error(f"unwrap losing text info: '{head}'")

    return iter(elms)


UnwrapResult = namedtuple("UnwrapResult", "head, elms")


def _unwrap_internal(should_unwrap, elm):
    """
    :param shoud_unwrap:
    :param elm:
    :return:
    """

    unwrapped_children = []
    for child in elm:
        unwrapped_children.append(_unwrap_internal(should_unwrap, child))

    if len(unwrapped_children) == 0:
        joined_children = UnwrapResult(None, [])
    elif len(unwrapped_children) == 1:
        joined_children = unwrapped_children[0]
    else:
        joined_children = functools.reduce(_join_unwrapped, unwrapped_children)

    if should_unwrap(elm):
        # get rid of elm ( keeping its text and tail
        new_children = joined_children.elms
        if new_children is None or len(new_children) == 0:
            # we return only text
            head = join_strings(elm.text, join_strings(joined_children.head, elm.tail))
            return UnwrapResult(head, new_children)
        else:
            # we return some children
            new_children[-1].tail = join_strings(new_children[-1].tail, elm.tail)
            head = join_strings(elm.text, joined_children.head)
            return UnwrapResult(head, new_children)
    else:
        # keep elm, join the text of the joined_children to the text of elm
        elm.text = join_strings(elm.text, joined_children.head)
        set_new_children(elm, joined_children.elms)
        return UnwrapResult( None, [elm])


def _join_unwrapped(left, right):
    """

    :param left:
    :param right:
    :return:

    >>> elm = etree.XML("<root>a<x>b</x>c<y>d</y>e</root>")
    >>> x = elm[0]
    >>> y =elm[1]
    >>> l = UnwrapResult('1', [elm[0]])
    >>> r = UnwrapResult('2', [elm[1]])
    >>> result = _join_unwrapped(l,r)
    >>> result.head
    '1'
    >>> len(result.elms)
    2
    >>> etree.tostring(result.elms[0])
    b'<x>b</x>c 2'
    >>> etree.tostring(result.elms[1])
    b'<y>d</y>e'

    >>> elm = etree.XML("<root>a<x>b</x>c<y>d</y>e</root>")
    >>> x = elm[0]
    >>> y =elm[1]
    >>> l = UnwrapResult(None, [elm[0]])
    >>> r = UnwrapResult(None, [elm[1]])
    >>> result = _join_unwrapped(l,r)
    >>> result.head is None
    True
    >>> len(result.elms)
    2
    >>> etree.tostring(result.elms[0])
    b'<x>b</x>c'
    >>> etree.tostring(result.elms[1])
    b'<y>d</y>e'

    >>> elm = etree.XML("<root><x>a</x><y>b</y></root>")
    >>> x = elm[0]
    >>> y =elm[1]
    >>> l = UnwrapResult(None, [elm[0]])
    >>> r = UnwrapResult(None, [elm[1]])
    >>> result = _join_unwrapped(l,r)
    >>> result.head is None
    True
    >>> len(result.elms)
    2
    >>> etree.tostring(result.elms[0])
    b'<x>a</x>'
    >>> etree.tostring(result.elms[1])
    b'<y>b</y>'

    """
    head_l, elms_l = left.head, left.elms
    head_r, elms_r = right.head, right.elms

    if is_empty(head_r):
        return UnwrapResult(head=head_l, elms=elms_l + elms_r)

    if len(elms_l) == 0:
        return UnwrapResult(head=join_strings(head_l, head_r), elms=elms_r)

    elms_l[-1].tail = join_strings(elms_l[-1].tail, head_r)

    return UnwrapResult(head=head_l, elms=elms_l + elms_r)


def unwrap_factory(should_unwrap):
    return functools.partial(unwrap_gen, should_unwrap)


def join_children_gen(join_children: Callable[[Any, Any], Any], elm):
    """
    Joins two elements
    :param join_children: A generator that returns the result of joining (or not) two adjacent children
    :param elm: the element whose children should be joined
    :return: generator that yields the element

    >>> def join(x,y):
    ...     if x.tag == 'p' and y.tag == 'p':
    ...         x.text = x.text + y.text
    ...         yield x
    ...     else:
    ...         yield x
    ...         yield y

    >>> elm = etree.XML('<root><div/><p id="1">abc</p><div/><p id="2">p_2 </p><p id="3">p_3 </p><p id="4">p_4</p></root>')
    >>> result = list(join_children_gen(join, elm))
    >>> len(result)
    1
    >>> etree.tostring(result[0])
    b'<root><div/><p id="1">abc</p><div/><p id="2">p_2 p_3 p_4</p></root>'
    >>> elm = etree.XML('<root><div><p id="1">abc</p><div/><p id="2">p_2 </p><p id="3">p_3 </p><p id="4">p_4</p></div></root>')
    >>> result = list(join_children_gen(join, elm))
    >>> len(result)
    1
    >>> etree.tostring(result[0])
    b'<root><div><p id="1">abc</p><div/><p id="2">p_2 p_3 p_4</p></div></root>'
    """
    new_children = generate_new_children(lambda child: join_children_gen(join_children, child), elm)
    remove_children(elm)

    def reducer(accumulator, new_child):
        if len(accumulator) > 0:
            result = accumulator[:-1] + list(join_children(accumulator[-1], new_child))
        else:
            result = [new_child]
        return result

    joined_children = functools.reduce(reducer, new_children, [])
    set_new_children(elm, joined_children)
    yield elm


def join_children_factory(should_join):
    return functools.partial(join_children_gen, should_join)


def lateral_effect_gen(lateral_effect_func, elm):
    lateral_effect_func()
    yield elm


def lateral_effect_factory(lateral_effect_func):
    return functools.partial(lateral_effect_gen, lateral_effect_func)
