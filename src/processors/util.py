from bs4 import BeautifulSoup
from os import path

from utils.pytest.fixtures import path_resolver

# todo remove (just a util func to help with running tests in the console)
def load_fixture(fname):
    fname = path.abspath(path.join(__file__, "../../..", "tests/html_processor/data_fixtures", fname + ".html"))
    with open(fname, 'r') as f:
        soup = BeautifulSoup(f)
    return soup
