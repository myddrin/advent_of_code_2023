import os

import pytest

from day_20.compute import System


@pytest.fixture(scope='session')
def small_ex1_txt():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'small_ex1.txt',
    )


@pytest.fixture(scope='session')
def small_ex2_txt():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'small_ex2.txt',
    )


@pytest.fixture(scope='session')
def input_txt():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'input.txt',
    )


class TestQ1:
    def test_small_ex1(self, small_ex1_txt):
        assert System.from_file(small_ex1_txt).cycle() == 32000000

    def test_small_ex2(self, small_ex2_txt):
        assert System.from_file(small_ex2_txt).cycle() == 11687500

    def test_input(self, input_txt):
        assert System.from_file(input_txt).cycle() == 929810733
