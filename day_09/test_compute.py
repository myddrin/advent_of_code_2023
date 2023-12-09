import os

import pytest

from day_09.compute import (
    DataSeq,
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


class TestData:
    @pytest.mark.parametrize(
        'init_data, exp_last', (([0, 0, 0, 0], 0), ([3, 3, 3, 3, 3], 3), ([0, 3, 6, 9, 12, 15], 18)),
    )
    def test_private_extrapolate(self, init_data, exp_last):
        assert DataSeq._extrapolate(init_data) == exp_last


class TestQ1:
    def test_small_ex(self, small_ex_txt):
        assert q1(DataSeq.from_file(small_ex_txt)) == 114

    def test_input(self, input_txt):
        assert q1(DataSeq.from_file(input_txt)) == 1731106378
