"""
Utilities for applying processors to files
"""
import shutil
from fnmatch import fnmatch
from typing import Callable, List, Any, Sequence
from bs4 import BeautifulSoup
import os
from os import path, walk
import logging
import re

_log = logging.getLogger("bs-processors")


def process_directory(processor: Callable[[List[Any]], List[Any]], parser_type: str,
                      input_dir: str, output_dir: str,
                      file_selector):
    """
    Processes a directory with the specified processor

    * **processor**: a file processor
    * **parser_type**: processor 'html.parser', 'html', 'xml' ( BeautifulSoup parser)
    * **input_dir**: the input directory
    * **output_dir**: the output directory
    * **file_selector**: something that can be transformed into a file_name predicate
        if the predicate is true than the file will be processed if not the file will be
        copied from input dir to output dir, see `to_file_selector_predicate` for details
        about the file selector.
    """
    file_selector = to_file_selector_predicate(file_selector)
    for dirpath, dirnames, filenames in walk(input_dir):
        rel_path = dirpath[len(input_dir):]
        if len(rel_path) > 0 and rel_path[0] == path.sep:
            rel_path= rel_path[1:]  # remove start '/'

        current_output_dir = path.join(output_dir, rel_path)

        if not path.exists(current_output_dir):
            os.makedirs(current_output_dir)

        for fname in filenames:
            input_fname = path.join(dirpath, fname)
            output_fname = path.join(current_output_dir, fname)
            if file_selector(input_fname):
                _log.debug(f"processing '{input_fname}' into '{output_fname}'")
                process_file(processor, parser_type, input_fname, output_fname)
            else:
                _log.debug(f"copying '{input_fname}' into '{output_fname}'")
                shutil.copy(input_fname, output_fname)


def process_file(processor: Callable[[List[Any]], List[Any]], parser_type: str, input_file: str, output_file: str):
    """
    Processes a file with the passed processor and saves the result in the output file

    * **processor**: the processor to be applied
    * **parser_type**: BeautifulSoup parser type ( 'html', 'xml', 'html.parser', etc)
    * **input_file**: the input file name
    * **output_file**: the result file name

    """
    with open(input_file, "rt") as f:
        soup = BeautifulSoup(f, parser_type)

    result = processor([soup])

    output_len = len(result)

    if output_len == 0:
        _log.warning(f"processing '{input_file}' did NOT generate any output")
        return

    if output_len > 1:
        _log.warning(f"processing '{input_file}' generated multiple output elements saving only the first one")

    result = result[0]

    if result.name != '[document]':
        _log.warning(f"processing '{input_file}' did not yield a beautiful soup element creating one")
        soup = BeautifulSoup(features=parser_type)
        result = soup.append(result)

    directory_name, f_name = path.split(output_file)

    if not path.exists(directory_name):
        os.makedirs(directory_name)

    with open(output_file, "wt") as f:
        f.write(result.prettify())


def process_html_file(processor: Callable[[List[Any]], List[Any]], input_file: str, output_file: str):
    process_file(processor, 'html.parser', input_file, output_file)


def to_file_selector_predicate(pred):
    """
    Creates a file selector predicate from a variety of arguments

    * **pred**: something that can be transformed in a file name predicate
         * None: will match everything
         * a str: will be interpreted as a unix file pattern (e.g. *.txt )
         * a sequence: will be interpreted as a sequence of unix file patterns
                (e.g. [*.txt, *.py]
         * a regular expression, will create a predicate with re.fullmath (i.e. full match
            of the full file name)
         * a predicate that takes a string (the full file name)

    * **return**: a file name predicate

    >>> pm = to_file_selector_predicate('*.txt')
    >>> pm('abc/def.txt')
    True
    >>> pm('abc/def.doc')
    False
    >>> pm = to_file_selector_predicate(['*.txt', '*.doc'])
    >>> pm('abc/def.doc')
    True
    >>> pm('abc/def.txt')
    True
    >>> pm('abc/def.tt')
    False
    >>> pm = to_file_selector_predicate(re.compile("(abc)|(def+)"))
    >>> pm("abc")
    True
    >>> pm("abcd")
    False
    >>> pm("def")
    True
    >>> pm("deffff")
    True
    >>> pm("something")
    False
    >>> pm = to_file_selector_predicate(lambda x: x.endswith("txt"))
    >>> pm("abc.txt")
    True
    >>> pm("abc.tt")
    False

    """
    if pred is None:
        return True  # select everything

    # pred is a string
    if isinstance(pred, str):
        return pattern_match_pred([pred])

    # pred is a list like object
    elif isinstance(pred, (tuple, list, set, frozenset)):
        return pattern_match_pred(pred)
    # pred is a regex
    elif isinstance(pred, re.Pattern):
        return lambda fname: pred.fullmatch(fname) is not None
    # pred must be a predicate, use it as is
    else:
        return pred


def pattern_match_pred(patterns: Sequence[str]) -> Callable[[str], bool]:
    """
    Creates a unix file pattern match predicate from a sequence of patterns

    * **patterns**: sequence of patterns
    * **return**: predicate

    >>> pm = pattern_match_pred(["*.exe", "*.txt", "*.do?"])
    >>> pm( "abc.txt")
    True
    >>> pm( "User/bubu/xyz.txt")
    True
    >>> pm( "abc.txta")
    False
    >>> pm('abc.exe')
    True
    >>> pm('abc.ex')
    False
    >>> pm('abc.doc')
    True
    """
    def inner(file_name: str) -> bool:
        for pattern in patterns:
            if fnmatch(file_name, pattern):
                return True
        return False

    return inner
