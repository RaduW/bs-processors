import pytest
from lxml import etree
from html_processor.generic_processors import flatten_gen, FlattenPolicy
from utils.pytest.compare_xml import compare_xml


def should_flatten(elm):
    if elm.tag in [ "p", "div", "br"]:
        return True
    return False

def is_internal(elm):
    if elm.tag in ["img"]:
        return True
    return False

@pytest.mark.parametrize("file_name", (
    ("simple_flatten", "super_simple")
))
def test_flatten(path_resolver, html_file_loader, dump_xml_file, result_file_logger, file_name):
    input_file_name = file_name+ ".html"
    output_file_name = file_name+ ".result.xml"
    path = path_resolver(__file__, "../data_fixtures", input_file_name)
    root = html_file_loader(path)

    result = [x for x in flatten_gen(should_flatten, is_internal, root)]
    assert len(result) == 1

    output_path = path_resolver(__file__, "../data_fixtures", output_file_name)
    result_file_logger(output_path,dump_xml_file, result[0])
    expected_result = html_file_loader(output_path)
    error = compare_xml(expected_result, result[0])
    assert error is None
