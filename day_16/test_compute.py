import os

import pytest

from day_16.compute import Map


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
        assert Map.from_file(small_ex_txt).trigger_beam() == 46

    def test_input(self, input_txt):
        assert Map.from_file(input_txt).trigger_beam() == 8249


class TestQ2:
    def test_small_ex(self, small_ex_txt):
        assert Map.from_file(small_ex_txt).best_beam() == 51

    def test_input(self, input_txt):
        assert Map.from_file(input_txt).best_beam() == 8444
