import os

import pytest

from day_01.compute import (
    Line,
    load_data,
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
def small_ex2_txt():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'small_ex_2.txt',
    )


@pytest.fixture(scope='session')
def input_txt():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'input.txt',
    )


class TestLine:
    @pytest.mark.parametrize(
        'line, exp_extended_digits',
        (
            ('two1nine', [2, 1, 9]),
            ('eightwothree', [8, 2, 3]),  # links letters
            ('two1ninetwo1nine', [2, 1, 9, 2, 1, 9]),  # finds them all
        ),
    )
    def test_from_line_extends_digits(self, line, exp_extended_digits):
        assert Line.from_line(line).extended_digits == exp_extended_digits


class TestQ1:
    def test_small_ex(self, small_ex_txt):
        dat = load_data(small_ex_txt)
        assert q1(dat) == 142

    def test_input(self, input_txt):
        dat = load_data(input_txt)
        assert q1(dat) == 54630


class TestQ2:
    def test_small_ex(self, small_ex2_txt):
        dat = load_data(small_ex2_txt)
        assert q2(dat) == 281

    def test_input(self, input_txt):
        dat = load_data(input_txt)
        assert q2(dat) == 54770
