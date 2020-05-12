""" processors for xml elements

A processor is a function that receives an element and returns a generator of elements.
It may return:
    - a generator with one element (typical case of an element transformer)
    - a generator with 0 elements ( typical case for a filter that returns either one or zero elemeents)
    - a generator with multipel elements ( a flatten function that takes the elements out of an element with embedded
    elms)
"""
from typing import Any, Callable

from lxml import etree
import functools

from html_processor.xml_util import remove_children, set_new_children, generate_new_children


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
    >>> result = [x for x in filter_gen(should_filter, doc)]
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
    >>> result = [x for x in local_modify_gen(add_id_to_p, elm)]
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


def unwrap_gen( should_unwrap: Callable[[Any], bool], elm):
    """
    Removes an element while inserting the children in to the parent (at the position where
    the element used to be)

    :param should_unwrap: true if the current element should be deleted and its children pushed up
    :param elm: the elment to anaylze
    :return: generator yielding either the element or the children of the element
    """
    new_children = generate_new_children(lambda child: filter_gen(should_unwrap, child), elm)
    if not should_unwrap(elm):
        set_new_children(elm,new_children)
        yield elm
    else:
        for child in new_children:
            yield child


def unwrap_factory(should_unwrap):
    return functools.partial(unwrap_gen, should_unwrap)


def join_children_gen(should_join: Callable[[Any, Any], bool], elm):
    """
    Joins to elements
    :param should_join:
    :param elm:
    :return:
    """
    #TODO implement
    raise NotImplementedError("TODO implement join_children_gen")


def join_chidren_factory(should_join):
    return functools.partial(join_children_gen, should_join)
