import os

import pytest

from day_22.compute import (
    Brick,
    BrickMap,
)
from day_22.compute import Position as P


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


class TestPosition:
    @pytest.mark.parametrize(
        'a, b, exp',
        (
            (P(1, 0, 1), P(1, 2, 1), 3),
            (P(0, 0, 2), P(2, 0, 2), 3),
            # not seen in example - multiple axis bricks
            (P(1, 1, 8), P(2, 1, 9), 4),
        ),
    )
    def test_volume(self, a, b, exp):
        assert a.volume(b) == exp


@pytest.fixture(autouse=True, scope='function')
def reset_bricks():
    Brick.all_bricks = 0


class TestBrickMap:
    small_ex_content = {
        'b0000': '1,0,1~1,2,1',  # A
        'b0001': '0,0,2~2,0,2',  # B
        'b0002': '0,2,3~2,2,3',  # C
        'b0003': '0,0,4~0,2,4',  # D
        'b0004': '2,0,5~2,2,5',  # E
        'b0005': '0,1,6~2,1,6',  # F
        'b0006': '1,1,8~1,1,9',  # G
    }

    def test_fall(self, small_ex_txt):
        brick_map = BrickMap.from_file(small_ex_txt)
        assert len(brick_map.bricks_in_air) == 7
        assert len(brick_map.bricks_on_ground) == 0

        brick_map.fall()
        assert len(brick_map.bricks_in_air) == 0
        assert len(brick_map.bricks_on_ground) == 7

        initial_content = {k: Brick.from_line(v, name=k) for k, v in self.small_ex_content.items()}
        assert set(initial_content.keys()) == set(brick_map.bricks_on_ground.keys())

        a = brick_map.bricks_on_ground['b0000']
        assert a == initial_content[a.name], 'unchanged - already on ground at start'

        b = brick_map.bricks_on_ground['b0001']
        assert b == initial_content[b.name]  # already on "a"
        c = brick_map.bricks_on_ground['b0002']
        assert c == initial_content[c.name].translate(P(0, 0, -1))  # down until it reaches "a"
        assert set(a.supports) == {b.name, c.name}
        assert b.lies_on == [a.name]
        assert c.lies_on == [a.name]

        d = brick_map.bricks_on_ground['b0003']
        assert d == initial_content[d.name].translate(P(0, 0, -1))
        e = brick_map.bricks_on_ground['b0004']
        assert e == initial_content[e.name].translate(P(0, 0, -2))
        assert set(b.supports) == {d.name, e.name}
        assert set(d.lies_on) == {b.name, c.name}
        assert set(c.supports) == {d.name, e.name}

        f = brick_map.bricks_on_ground['b0005']
        assert f == initial_content[f.name].translate(P(0, 0, -2))
        assert d.supports == [f.name]
        assert set(f.lies_on) == {d.name, e.name}
        assert e.supports == [f.name]

        g = brick_map.bricks_on_ground['b0006']
        assert g == initial_content[g.name].translate(P(0, 0, -3))
        assert f.supports == [g.name]
        assert g.lies_on == [f.name]

        assert g.supports == []


class TestQ1:
    def test_small_ex(self, small_ex_txt):
        brick_map = BrickMap.from_file(small_ex_txt)
        brick_map.fall()
        assert len(brick_map.destruction_candidates()) == 5

    @pytest.mark.slow
    def test_input(self, input_txt):
        # take ~40s
        brick_map = BrickMap.from_file(input_txt)
        brick_map.fall()
        assert len(brick_map.destruction_candidates()) == 497
