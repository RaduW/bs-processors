"""
# Utilities used by examples

All the examples use the utility functions in this file.

{{ NO_PROCESSING }}
"""

from typing import List, Any
import logging
from os import path

from bs4 import BeautifulSoup

_log = logging.getLogger("bs-processors")

SOUP_NAME = '[document]'


def save_result(elms: List[Any], file_name: str) -> None:
    """
    Save processor result to file

    * **elms**: an array of elements (results of processing) to be saved
    * **file_name**: the full path for the result file
    """
    if len(elms) == 0:
        _log.error(f"0 elements passed to save_results file {file_name} not created.")

    if len(elms) > 1:
        _log.warning(f"{len(elms)} passed to save_result, only first saved to {file_name}")

    elm = elms[0]

    with open(file_name, "wt") as f:
        text = str(elm)
        f.write(text)


def save_relative_result(elms: List[Any], relative: str, file_name: str):
    """
    Save processor result to file

    * **elms**: an array of elements (results of processing) to be saved
    * **relative**: the path of a module (passed as __file__)
    * **file_name**: a relative file name to that module
    """
    return save_result(elms, relative_to_absolute_path_name(relative, file_name))


def load_html_file(file_name: str):
    """
    Loads html file in a BeautifulSoup object

    * **file_name**: the file name
    * **return** a BeautifulSoup object loaded with the file content
    """
    with open(file_name, "rt") as f:
        soup = BeautifulSoup(f, "html.parser")
    return soup


def load_relative_html_file(relative: str, file_name: str):
    """
    Loads an html file in a BeautifulSoup object

    * **relative**: the path of a module (passed as __file__)
    * **file_name**: a relative file name to that module
    * **return** a BeautifulSoup object loaded with the file content
    """
    return load_html_file(relative_to_absolute_path_name(relative, file_name))


def relative_to_absolute_path_name(relative: str, file_name: str) -> str:
    """
    Gets a file full path name relative to a module

    * **relative**: the path of a module (passed as __file__)
    * **file_name**: a relative file name to that module
    * **return**: an absolute file path name
    """
    return path.abspath(path.join(relative, '..', file_name))
