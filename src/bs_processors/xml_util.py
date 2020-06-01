"""
Useful utilities for working with BeautifulSoup trees


"""
from typing import Any, Callable, List

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


def process_children(processor: Callable[[Any], List[Any]], elm):
    """
    Processes the children of an element
    :param processor: A processor that takes an element and returns a list of elements
    :param elm: the element to process
    :return: A list with the joined results of processing each child with the provided processor

    >>> doc = BeautifulSoup("<div>a<span>b</span>c<p>d<span>e</span>f<a/>g</p>h</div>", "html.parser")
    >>> counter = [0]
    >>> def processor(elm):
    ...     counter[0] +=1
    ...     elm['id'] = str(counter[0])
    ...     return [elm]
    >>> process_children(processor, doc.div)
    ['a', <span id="1">b</span>, 'c', <p id="2">d<span>e</span>f<a></a>g</p>, 'h']
    """
    result = []
    for child in elm.children:
        if is_tag(child):
            result += processor(child)
        else:
            result.append(child)
    return result


def is_tag(elm):
    """
    >>> from bs4 import BeautifulSoup as bs
    >>> doc = bs("<span></span><p>bubu</p>", "html.parser")
    >>> span = doc.span
    >>> is_tag(doc.span)
    True
    >>> is_tag(doc.p)
    True
    >>> is_tag(list(doc.p.children)[0])
    False

    :param elm:
    :return:
    """
    return elm is not None and elm.name is not None


_bs = BeautifulSoup("<a/>", "html.parser")


def copy_element_type(elm):
    """
    >>> xml = BeautifulSoup("<root><abc/></root>", "xml")
    >>> copy_element_type(xml.root.abc)
    <abc/>
    """
    return _bs.new_tag(elm.name)
