import pytest
from lxml import etree
from html_processor.generic_processors import flatten_gen, FlattenPolicy


def flatten_policy_p(elm):
    if elm.tag in [ "p", "div"]:
        return FlattenPolicy.Flatten
    else:
        return FlattenPolicy.FlattenChildren

@pytest.mark.parametrize("file_name", (
    ("simple_flatten",)
))
def test_flatten(path_resolver, html_file_loader, file_name):
    input_file_name = file_name+ ".html"
    path = path_resolver(__file__, "../data_fixtures", input_file_name)
    root = html_file_loader(path)

    result = [x for x in flatten_gen(flatten_policy_p, root)]

    assert len(result) == 1

    tree_text = etree.tostring(result[0])

    print(tree_text)


    assert False
