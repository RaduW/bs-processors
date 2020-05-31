import pytest

from lxml_processor.custom_processors import clean_html, join_lists
from utils.pytest.compare_lxml import compare_xml


@pytest.mark.parametrize("file_name",  ("super_simple_ul",))
def test_join_custom(path_resolver, html_file_loader, dump_xml_file, result_file_logger, file_name):
    input_file_name = file_name + ".html"
    output_file_name = "z-join-custom-" + file_name + ".result.xml"
    path = path_resolver(__file__, "../data_fixtures", input_file_name)
    output_path = path_resolver(__file__, "../data_fixtures", output_file_name)

    root = html_file_loader(path)

    result = list(join_lists(root))
    assert len(result) == 1

    result_file_logger(output_path, dump_xml_file, result[0])
    expected_result = html_file_loader(output_path)

    error = compare_xml(expected_result, result[0])
    assert error is None



@pytest.mark.parametrize("file_name",
                         ("simple", "super_simple", "with_font", "simple_with_ul", "various_ul")
)
def test_clean_html(path_resolver, html_file_loader, dump_xml_file, result_file_logger, file_name):
    input_file_name = file_name + ".html"
    output_file_name = "z-clean-" + file_name + ".result.xml"
    path = path_resolver(__file__, "../data_fixtures", input_file_name)
    output_path = path_resolver(__file__, "../data_fixtures", output_file_name)

    root = html_file_loader(path)

    result = clean_html(root)

    result_file_logger(output_path, dump_xml_file, result)

    expected_result = html_file_loader(output_path)

    error = compare_xml(expected_result, result)
    assert error is None
