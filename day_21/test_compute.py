import os

import pytest

from day_21.compute import Garden


@pytest.fixture(scope='session')
def small_ex_txt():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'small_ex.txt',
    )


@pytest.fixture(scope='session')
def input_txt():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'input.txt',
    )


class TestQ1:
    def test_small_ex(self, small_ex_txt):
        assert Garden.from_file(small_ex_txt).visit(6) == 16

    def test_input(self, input_txt):
        assert Garden.from_file(input_txt).visit(64) == 3740
