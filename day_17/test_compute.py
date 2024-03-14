import os

import pytest

from day_17.compute import (
    Ant,
    HeatMap,
    Position,
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


class TestAnt:
    def test_lt(self):
        a = Ant(Position(1, 0), 4, [Position(0, 0), Position(1, 0)])
        b = Ant(
            Position(1, 0),
            9,
            [Position(0, 0), Position(0, 1), Position(1, 1), Position(1, 0)],
        )
        assert a < b


class TestHeatMap:
    def test_mini_map(self):
        heat_map = HeatMap(
            heat_loss=[
                [3, 5],
                [3, 3],
            ],
        )
        heat_map.visit_map()
        assert heat_map.heat_loss_at_end() == 6


class TestQ1:
    def test_small_ex(self, small_ex_txt):
        heatmap = HeatMap.from_file(small_ex_txt)
        heatmap.visit_map()
        assert heatmap.heat_loss_at_end() == 102

    # < 1035
