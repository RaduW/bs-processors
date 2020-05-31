# import pytest
# from lxml_processor.generic_processors import (
#     flatten_gen, flatten_factory, filter_factory, unwrap_factory,
#     join_children_factory,
# )
# from utils.pytest.compare_lxml import compare_xml
#
#
# @pytest.mark.parametrize("file_name", (
#     ("super_simple_ul",)
# ))
# def test_join(path_resolver, html_file_loader, dump_xml_file, result_file_logger, file_name):
#     input_file_name = file_name + ".html"
#     output_file_name = "z-join-" + file_name + ".result.xml"
#     path = path_resolver(__file__, "../data_fixtures", input_file_name)
#     output_path = path_resolver(__file__, "../data_fixtures", output_file_name)
#
#     root = html_file_loader(path)
#
#     unwrap = join_children_factory(_mini_join_p)
#     result = list(unwrap( root))
#     assert len(result) == 1
#
#     result_file_logger(output_path, dump_xml_file, result[0])
#
#     expected_result = html_file_loader(output_path)
#
#     error = compare_xml(expected_result, result[0])
#     assert error is None
#
#
