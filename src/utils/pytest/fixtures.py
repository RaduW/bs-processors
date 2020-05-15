import pytest
from os import path, remove
from lxml import etree


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


@pytest.fixture
def result_file_logger(request):
    params = {}

    def inner(file_name, file_generator, *args, **kwargs):
        # if we don't yet have a result create one
        if not path.exists(file_name):
            file_generator(file_name, *args, **kwargs)

        dir, f_name = path.split(file_name)
        components = f_name.split('.', 1)
        if len(components) > 1:
            f_name = components[0] + "_." + components[1]
        else:
            f_name += "_"
        error_file_name = path.join(dir, f_name)

        if path.exists(error_file_name):
            # we have an old error result, delete it
            remove(error_file_name)
        params['error_file_name'] = error_file_name
        params['file_generator'] = file_generator
        params['args'] = args
        params['kwargs'] = kwargs

    yield inner
    if request.node.rep_setup.passed and request.node.rep_call.failed:
        # we have a failed test
        fun = params.get('file_generator')
        if fun is not None:
            args = params['args']
            kwargs = params['kwargs']
            error_file_name = params['error_file_name']
            fun(error_file_name, *args, **kwargs)
