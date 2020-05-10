import pytest
import main


@pytest.mark.parametrize("x,result",
                         [(1,2),(3,4)])
def test_fn1(x, result):
    assert main.fn1(x) == result


def test_2(get_val):
    assert get_val == 22
