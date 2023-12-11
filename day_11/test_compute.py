import os
from operator import itemgetter

import pytest

from day_11.compute import (
    GalaxyMap,
    Position,
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


class TestGalaxyMap:
    def test_from_file(self, small_ex_txt):
        data = GalaxyMap.from_file(small_ex_txt)
        assert data.width == 10
        assert data.height == 10
        assert data.universe == {
            Position(3, 0): 0,
            Position(7, 1): 1,
            Position(0, 2): 2,
            Position(6, 4): 3,
            Position(1, 5): 4,
            Position(9, 6): 5,
            Position(7, 8): 6,
            Position(0, 9): 7,
            Position(4, 9): 8,
        }

    def test_expand(self, small_ex_txt):
        data = GalaxyMap.from_file(small_ex_txt).expand()
        assert data.width == 13
        assert data.height == 12
        assert sorted(data.universe.items(), key=itemgetter(1)) == sorted(
            {
                Position(4, 0): 0,  # right once
                Position(9, 1): 1,  # right twice
                Position(0, 2): 2,  # not shifted
                Position(8, 5): 3,  # right twice, down once
                Position(1, 6): 4,  # down once
                Position(12, 7): 5,  # right 3 times, down once
                Position(9, 10): 6,  # right twice, down twice
                Position(0, 11): 7,  # down twice
                Position(5, 11): 8,  # right once, down twice
            }.items(),
            key=itemgetter(1),
        )


class TestQ1:
    def test_small_ex(self, small_ex_txt):
        assert q1(GalaxyMap.from_file(small_ex_txt).expand()) == 374

    def test_input(self, input_txt):
        assert q1(GalaxyMap.from_file(input_txt).expand()) == 9795148
