import os

import pytest

from day_08.compute import (
    NodeMap,
    q1,
)


@pytest.fixture(scope='session')
def small_ex_txt():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'small_ex.txt',
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
    def test_small_ex(self, small_ex_txt):
        assert q1(NodeMap.from_file(small_ex_txt)) == 2

    def test_small_ex2(self, small_ex2_txt):
        assert q1(NodeMap.from_file(small_ex2_txt)) == 6

    def test_input_txt(self, input_txt):
        assert q1(NodeMap.from_file(input_txt)) == 15989
