import pytest
from os import path
from lxml import etree


@pytest.fixture
def get_val():
    return 22


@pytest.fixture
def path_resolver():
    def inner(*args):
        return path.abspath(path.join(*args))

    return inner


@pytest.fixture
def html_file_loader():
    def inner(path):
        with open(path, 'r') as f:
            parser = etree.HTMLParser()
            tree = etree.parse(f, parser)
            return tree.getroot()

    return inner


@pytest.fixture
def dump_xml_file():
    def inner(path, elm):
        with open(path, "wb") as f:
            tree = etree.ElementTree(elm)
            tree.write(f, pretty_print=True)

    return inner
