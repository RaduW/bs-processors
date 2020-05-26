from bs_processor.custom_processors import should_flatten, stays_inside_parent, set_is_block_a
from bs_processor.generic_processors import flatten_factory, local_modify_factory
from bs_processor.processor_util import join_proc
from utils.util import path_resolver
from bs4 import BeautifulSoup


def to_full_name(file_name):
    """
    >>> def to_full_name(file_name):
   '/Users/raduw/dev/examples/clean-html/samples/1.xml'
    """
    return path_resolver(__name__, '../..', "samples", file_name)


flatten_proc = flatten_factory(should_flatten, stays_inside_parent)
mark_block_a = local_modify_factory(set_is_block_a)


def save_elm(elm, file_name):
    soup = BeautifulSoup()
    soup.append(elm)
    html = soup.prettify("utf-8")
    path = to_full_name("output"+file_name)
    with open(path, "wb") as f:
        f.write(html)

def process(file_name):
    path = to_full_name(file_name)

    with open(path, 'r') as f:
        doc = BeautifulSoup(f)

    processor = join_proc([
        mark_block_a,
        flatten_proc,
    ])
    result = processor([doc.html])
    assert len(result) == 1
    result = result[0]
    save_elm(result, file_name)


if __name__ == '__main__':
    process('1.html')
    process('2.html')
