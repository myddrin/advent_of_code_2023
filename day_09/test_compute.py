import os

import pytest

from day_09.compute import (
    DataSeq,
    q1,
    q2,
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
        'init_data, exp_first, exp_last',
        (([0, 0, 0, 0], 0, 0), ([3, 3, 3, 3, 3], 3, 3), ([0, 3, 6, 9, 12, 15], -3, 18)),
    )
    def test_private_extrapolate(self, init_data, exp_first, exp_last):
        assert DataSeq._extrapolate(init_data) == (exp_first, exp_last)

    def test_extrapolate_adds_new_data(self):
        data = DataSeq.from_line('10 13 16 21 30 45')
        assert len(data.data) == 6
        data.extrapolate()
        assert len(data.data) == 8
        assert data.data == [
            5,
            10,
            13,
            16,
            21,
            30,
            45,
            68,
        ]


class TestQ1:
    def test_small_ex(self, small_ex_txt):
        extrapolated = [d.extrapolate() for d in DataSeq.from_file(small_ex_txt)]
        assert q1(extrapolated) == 114

    def test_input(self, input_txt):
        extrapolated = [d.extrapolate() for d in DataSeq.from_file(input_txt)]
        assert q1(extrapolated) == 1731106378


class TestQ2:
    def test_small_ex(self, small_ex_txt):
        extrapolated = [d.extrapolate() for d in DataSeq.from_file(small_ex_txt)]
        assert q2(extrapolated) == 2

    def test_input(self, input_txt):
        extrapolated = [d.extrapolate() for d in DataSeq.from_file(input_txt)]
        assert q2(extrapolated) == 1087
