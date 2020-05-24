import functools
import itertools
import re
import string
from typing import Optional, Any, Sequence, List, Iterable


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


def flatten( val: Iterable[Iterable[Any]]) -> List[Any]:
    """
    Flatens a list of list into a list

    >>> flatten( [['abc','def'],[12,34,46],[3.14, 2.22]])
    ['abc', 'def', 12, 34, 46, 3.14, 2.22]
    """
    return list(itertools.chain(*val))

