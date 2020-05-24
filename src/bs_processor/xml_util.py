"""
Useful utilities for working with BeautifulSoup trees


"""
from bs4 import BeautifulSoup


def set_new_children(elm, children):
    """
    Sets new children to an element
    :param elm: the element to have its children set
    :param children: a sequence of children
    :return: the element

    >>> xml = BeautifulSoup("<root>X<a/>X<b/>X</root>",'xml')
    >>> xml
    <?xml version="1.0" encoding="utf-8"?>
    <root>X<a/>X<b/>X</root>
    >>> new_children = [xml.new_tag("x"), xml.new_tag("y")]
    >>> set_new_children( xml.root, new_children)
    <root><x/><y/></root>

    """

    new_children = list(children)
    if list(elm.children) == new_children:
        return elm

    elm.clear()
    for child in new_children:
        elm.append(child)

    return elm


def process_children(processor, elm):
    result = []
    for child in elm.children:
        if is_tag(child):
            result += processor(child)
        else:
            result.append(child)
    return result


def is_tag(elm):
    if hasattr(elm, "children"):
        return True
    return False


_bs = BeautifulSoup("<a/>", "xml")


def copy_element_type(elm):
    """
    >>> xml = BeautifulSoup("<root><abc/></root>", "xml")
    >>> copy_element_type(xml.root.abc)
    <abc/>
    """
    return _bs.new_tag(elm.name)
