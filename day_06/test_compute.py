import os

import pytest

from day_06.compute import (
    Record,
    count_points,
    threaded_count_points,
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
        assert count_points(Record.from_file(small_ex_txt)) == 288

    def test_input(self, input_txt):
        assert count_points(Record.from_file(input_txt)) == 440000


class TestQ2:
    def test_small_ex(self, small_ex_txt):
        assert threaded_count_points(Record.from_file(small_ex_txt, fix_spaces=True)) == 71503

    @pytest.mark.slow
    def test_input(self, input_txt):
        assert threaded_count_points(Record.from_file(input_txt, fix_spaces=True)) == 26187338
