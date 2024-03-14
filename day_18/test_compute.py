import os

import pytest

from day_18.compute import (
    DigPlan,
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


class TestDigPlan:
    def test_edge_area(self, small_ex_txt):
        dig_plan = DigPlan.from_file(small_ex_txt)
        assert dig_plan.edge_area() == 38


class TestQ1:
    def test_small_ex(self, small_ex_txt):
        assert q1(DigPlan.from_file(small_ex_txt)) == 62
