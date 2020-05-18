import pytest
from html_processor.generic_processors import flatten_gen, flatten_factory, filter_factory, unwrap_factory
from html_processor.processor_util import process
from html_processor.xml_util import set_new_children
from utils.pytest.compare_xml import compare_xml


def should_flatten(elm):
    if elm.tag in ["p", "div", "br"]:
        return True
    return False


def is_internal(elm):
    if elm.tag in ["img"]:
        return True
    return False


def should_filter(elm):
    if elm.tag in ["br"]:
        return True
    return False


@pytest.mark.parametrize("file_name", (
    ("simple", "super_simple")
))
def test_flatten(path_resolver, html_file_loader, dump_xml_file, result_file_logger, file_name):
    input_file_name = file_name + ".html"
    output_file_name = "z-flatten-" + file_name + ".result.xml"
    path = path_resolver(__file__, "../data_fixtures", input_file_name)
    output_path = path_resolver(__file__, "../data_fixtures", output_file_name)

    root = html_file_loader(path)

    result = list(flatten_gen(should_flatten, is_internal, root))
    assert len(result) == 1

    result_file_logger(output_path, dump_xml_file, result[0])

    expected_result = html_file_loader(output_path)

    error = compare_xml(expected_result, result[0])
    assert error is None


@pytest.mark.parametrize("file_name", (
    ("simple", "super_simple")
))
def test_flatten_and_filter(path_resolver, html_file_loader, dump_xml_file, result_file_logger, file_name):
    input_file_name = file_name + ".html"
    output_file_name = "z-flatten-filter-" + file_name + ".result.xml"
    path = path_resolver(__file__, "../data_fixtures", input_file_name)
    output_path = path_resolver(__file__, "../data_fixtures", output_file_name)

    root = html_file_loader(path)

    flatten = flatten_factory(should_flatten, is_internal)
    filter_br = filter_factory(should_filter)

    result = list(process(root, (flatten, filter_br)))

    assert len(result) == 1
    result_file_logger(output_path, dump_xml_file, result[0])

    expected_result = html_file_loader(output_path)

    error = compare_xml(expected_result, result[0])
    assert error is None


def should_unwrap(elm):
    return elm.tag in ["font", "fnt"]

@pytest.mark.parametrize("file_name", (
    ("font_simple", "font_complex")
))
def test_unwrap(path_resolver, html_file_loader, dump_xml_file, result_file_logger, file_name):
    input_file_name = file_name + ".html"
    output_file_name = "z-unwrap-" + file_name + ".result.xml"
    path = path_resolver(__file__, "../data_fixtures", input_file_name)
    output_path = path_resolver(__file__, "../data_fixtures", output_file_name)

    root = html_file_loader(path)

    unwrap = unwrap_factory(should_unwrap)
    result = list(unwrap( root))
    assert len(result) == 1

    result_file_logger(output_path, dump_xml_file, result[0])

    expected_result = html_file_loader(output_path)

    error = compare_xml(expected_result, result[0])
    assert error is None
