import os
import sys

import pytest


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

pytest_plugins= (
    "bs_processors.utils.pytest.fixtures"
)

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # set a report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"

    setattr(item, "rep_" + rep.when, rep)
