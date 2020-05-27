from typing import Tuple, Callable, Any

from bs_processor.xml_util import is_tag
from utils.util import is_empty

_remove_empty_elements = frozenset(['p', 'div', 'br'])
_unwrap_elements = frozenset(['font'])
_elements_who_hold_all_children = frozenset(['html', 'body', 'header', 'a', '[document]'])
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
    return True


def is_internal(elm) -> bool:
    """
    Returns True if the element pops out when flatten (if the element is a block element)

    >>> from lxml import etree
    >>> elm = etree.XML('<html><p id="1">abc</p> <span id="2">with text</span></html>')
    >>> p = elm[0]
    >>> is_internal(p)
    False
    >>> span = elm[1]
    >>> is_internal(span)
    True

    """
    if is_tag(elm) and elm.tag in _block_elements_that_pop_out:
        return False
    if elm.name == 'a' and "block_a" in elm.get('class',[]):
        return False
    else:
        return True


def set_is_block_a(elm):
    if not is_tag(elm) or elm.name != 'a':
        return elm
    classes = elm.get('class', [])
    # we have an 'a' check if it has block children
    if contains_block_child(elm) and not ('block_a' in classes):
        # it is an 'a' and it is not already marked as 'block'... do it now
        classes.append('block_a')
        elm['class'] = classes
    return elm


def contains_block_child(elm):
    if not is_tag(elm):
        return False
    for child in elm.children:
        if child.name in _block_elements_that_pop_out:
            return True
        if contains_block_child(child):
            return True
    return False
