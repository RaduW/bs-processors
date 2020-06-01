from bs_processors.custom_processors import should_flatten, is_internal, set_is_block_a
from bs_processors.generic_processors import flatten_factory, local_modify_factory
from bs_processors.processor_util import join
from bs_processors.utils import path_resolver
from bs4 import BeautifulSoup


def _to_full_name(file_name):
    return path_resolver(__name__, '../..', "samples", file_name)


flatten_proc = flatten_factory(flatten_children=should_flatten, is_internal=is_internal)
mark_block_a = local_modify_factory(set_is_block_a)


def save_elm(doc, file_name):
    html = doc.prettify("utf-8")
    path = _to_full_name("output" + file_name)
    with open(path, "wb") as f:
        f.write(html)

def process(file_name):
    path = _to_full_name(file_name)

    with open(path, 'r') as f:
        doc = BeautifulSoup(f, features='html.parser')

    processor = join([
        mark_block_a,
        flatten_proc,
    ])
    # TODO do *NOT* pass the Soup in ... I fixed it to work but it is an ugly hack.
    # Check if the soup has a top level child called <html> and if not create one and
    # add everything else under html... then pass the html tag .
    result = processor([doc])
    assert len(result) == 1
    result = result[0]
    save_elm(result, file_name)


if __name__ == '__main__':
    process('1.html')
    process('2.html')
    process('3.html')
