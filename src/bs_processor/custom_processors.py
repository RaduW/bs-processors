from typing import Tuple, Callable, Any

from bs_processor.xml_util import is_tag
from utils.util import is_empty

_remove_empty_elements = frozenset(['p', 'div', 'br'])
_unwrap_elements = frozenset(['font'])
_elements_who_hold_all_children = frozenset(['html', 'body', 'header', 'a'])
_block_elements_that_pop_out = frozenset(["p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "pre", "hr", "br"])


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
    if elm.name in _elements_who_hold_all_children or not is_tag(elm):
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
    if elm.name == 'a' and "block_a" in elm['class']:
        return False
    else:
        return False


def set_is_block_a(elm):
    if not is_tag(elm) or elm.name != 'a':
        return

    return contains_block_child(elm)


def contains_block_child(elm):
    if not is_tag(elm):
        return False
    for child in elm.children:
        if child.name in _block_elements_that_pop_out:
            return True
        if contains_block_child(child):
            return True
        return False
