import functools
import itertools
import re
from os import path
import string
from typing import Optional, Any, List, Iterable


def is_empty(s):
    """
    >>> is_empty(None)
    True
    >>> is_empty("hello")
    False
    >>> is_empty("  \t  ")
    True
    """
    return s is None or len(s) == 0 or s.isspace()


def is_non_empty_child(elm):
    """
    Returns true if the child is an non empty Navigable string or an Tag,Soup...
    :param elm: a Beautiful soup element
    :return: True if the element is not an empty string

    >>> from bs4 import BeautifulSoup as bs
    >>> doc = bs("<html><div>   <span>hello</span> <p></p></div></html>", "html.parser")
    >>> div = doc.html.div
    >>> span = doc.html.div.span
    >>> p = doc.html.div.p
    >>> is_non_empty_child(div)
    True
    >>> is_non_empty_child(span)
    True
    >>> is_non_empty_child(p)
    True
    >>> children = list(div.children)
    >>> children[0]
    ' '
    >>> is_non_empty_child(children[0])
    False
    >>> children[1]
    <span>hello</span>
    >>> is_non_empty_child(children[1])
    True
    >>> children[2]
    ' '
    >>> is_non_empty_child(children[2])
    False
    >>> children[3]
    <p></p>
    >>> is_non_empty_child(children[3])
    True
    """
    if elm is None:
        return False
    if elm.name is not None:
        return True
    return not is_empty(elm)


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


def flatten(val: Iterable[Iterable[Any]]) -> List[Any]:
    """
    Flatens a list of list into a list

    >>> flatten( [['abc','def'],[12,34,46],[3.14, 2.22]])
    ['abc', 'def', 12, 34, 46, 3.14, 2.22]
    """
    return list(itertools.chain(*val))


def path_resolver(*args):
    return path.abspath(path.join(*args))
