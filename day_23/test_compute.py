import os

import pytest

from day_23.compute import (
    HikingMap,
    q1,
)


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
        assert q1(HikingMap.from_file(small_ex_txt)) == 94

    def test_input(self, input_txt):
        assert q1(HikingMap.from_file(input_txt)) == 2310
