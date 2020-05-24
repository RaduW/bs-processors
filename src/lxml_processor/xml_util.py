"""
Utilities for working with lxml Elements
"""
import string
from typing import Optional
import functools
import re


def add_text(elm, text):
    """
    Adds a text to the end of an element
    :param elm: the element
    :param text: the text
    :return: the original with the text added

    >>> from lxml import etree
    >>> elm = etree.XML("<root><a></a></root>")
    >>> _ = add_text(elm[0], "XXX")
    >>> etree.tostring(elm)
    b'<root><a>XXX</a></root>'
    >>> elm = etree.XML("<root><a>ABC_</a></root>")
    >>> _ = add_text(elm[0], "XXX")
    >>> etree.tostring(elm)
    b'<root><a>ABC_XXX</a></root>'
    >>> elm = etree.XML("<root><a>ABC<b/></a></root>")
    >>> _ = add_text(elm[0], "XXX")
    >>> etree.tostring(elm)
    b'<root><a>ABC<b/>XXX</a></root>'
    >>> elm = etree.XML("<root><a>ABC<b/>DEF_</a></root>")
    >>> _ = add_text(elm[0], "XXX")
    >>> etree.tostring(elm)
    b'<root><a>ABC<b/>DEF_XXX</a></root>'
    """

    if len(elm) == 0:
        # no children append to text
        if elm.text is None:
            elm.text = text
        else:
            elm.text += text
    else:
        last_child = elm[len(elm) - 1]
        if last_child.tail is None:
            last_child.tail = text
        else:
            last_child.tail += text
    return elm


def is_empty(s):
    return s is None or len(s) == 0 or s.isspace()


def join_strings(left: Optional[str], right: Optional[str]) -> Optional[str]:
    """
    :param left:
    :param right:
    :return:

    >>> join_strings( None , 'abc')
    'abc'
    >>> join_strings( None , None) is None
    True
    >>> join_strings( 'abc' , None)
    'abc'
    >>> join_strings( 'abc' , 'cde')
    'abc cde'
    """
    if left is None and right is None:
        return None
    if right is None:
        return left
    if left is None:
        return right
    return left + " " + right


def join_children(left_parent, right_parent, level):
    """
    Joins the ancestors of two nodes placing them in the left node.
    The ancestors are joined at the specified level (1 = children, 2 grand_children...)
    :return: a generator containing the left parent
    """
    children = collect_children([left_parent, right_parent], level)
    set_new_children(left_parent, children)
    yield left_parent


def collect_children(elms, level: int = 1):
    """
    Collects the children at the specified depth.

    level: the specified child level ( 1: children of elms, 2: grand children of elms,...)

    >>> from lxml import etree
    >>> from pprint import pprint
    >>> elm = etree.XML("<root><a><b><c>1</c><c>2</c></b><b><c>3</c><c>4</c></b></a>"+
    ... "<a><b><c>5</c><c>6</c></b><b><c>7</c><c>8</c></b></a></root>")

    >>> c = list(collect_children(([elm]), 1))
    >>> pprint([etree.tostring(x) for x in c])
    [b'<a><b><c>1</c><c>2</c></b><b><c>3</c><c>4</c></b></a>',
     b'<a><b><c>5</c><c>6</c></b><b><c>7</c><c>8</c></b></a>']

    >>> c = list(collect_children((elm[0], elm[1]), 1))
    >>> pprint([etree.tostring(x) for x in c])
    [b'<b><c>1</c><c>2</c></b>',
     b'<b><c>3</c><c>4</c></b>',
     b'<b><c>5</c><c>6</c></b>',
     b'<b><c>7</c><c>8</c></b>']

    >>> c = list(collect_children((elm[0], elm[1]), 2))
    >>> pprint([etree.tostring(x) for x in c])
    [b'<c>1</c>',
     b'<c>2</c>',
     b'<c>3</c>',
     b'<c>4</c>',
     b'<c>5</c>',
     b'<c>6</c>',
     b'<c>7</c>',
     b'<c>8</c>']
    """
    if level < 1:
        raise ValueError("Collect children called with invalid level. Level must be grater than 0", level)
    if level == 1:
        for elm in elms:
            yield from elm
    else:
        for elm in elms:
            yield from collect_children(elm, level - 1)


def set_new_children(elm, new_children):
    remove_children(elm)
    for child in new_children:
        elm.append(child)


def generate_new_children(new_children_generator: object, elm: object) -> object:
    """
    Applies a transformer to the children of an element and returns the result as a  list

    >>> new_gen = lambda x: [x+1]
    >>> generate_new_children(new_gen , [1,2,3])
    [2, 3, 4]
    >>> new_gen = lambda x: [x,x]
    >>> generate_new_children(new_gen , [1,2,3])
    [1, 1, 2, 2, 3, 3]
    """
    new_children = []
    for child in elm:
        new_children += list(new_children_generator(child))
    return new_children


def remove_children(elm):
    """
    Removes all children from an element (maintaining everything else)
    :param elm: the element
    :return:
    >>> from lxml import etree
    >>> elm = etree.XML("<root><a><b/><c/><d/></a></root>")
    >>> _ = remove_children(elm[0] )
    >>> etree.tostring(elm)
    b'<root><a/></root>'
    >>> elm = etree.XML("<root><a>ABC_<b/><c/><d/>XYZ</a></root>")
    >>> _ = remove_children(elm[0] )
    >>> etree.tostring(elm)
    b'<root><a>ABC_</a></root>'
    >>> elm = etree.XML("<root><a></a></root>")
    >>> _ = remove_children(elm[0] )
    >>> etree.tostring(elm)
    b'<root><a/></root>'
    >>> elm = etree.XML("<root><a>ABC</a></root>")
    >>> _ = remove_children(elm[0] )
    >>> etree.tostring(elm)
    b'<root><a>ABC</a></root>'
    """
    children = elm.getchildren()
    for child in children:
        elm.remove(child)
    return elm


def _whitespace_regex():
    """
    >>> _whitespace_regex()
    '( |\\t|\\n|\\r|\\x0b|\\x0c)+'
    """
    all_white_spaces = [f'{x}' for x in string.whitespace]
    regex_string = functools.reduce(lambda acc, x: f"{acc}|{x}", all_white_spaces)
    return f"({regex_string})+"


_whitespace = re.compile(_whitespace_regex())


def normalize_string(val: Optional[str]):
    """
    Creates a string that is stripped of any white spaces at beg and end and
    has all sequences of whitespaces reduced to one single space

    >>> normalize_string('   this   is    \\t a very  \\n \\r spacy   string ')
    ' this is a very spacy string '
    """
    if val is None:
        return ""

    return _whitespace.sub(' ', val)
