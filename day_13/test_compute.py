import os

import pytest

from day_13.compute import (
    Pattern,
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


class TestPosition:
    # @pytest.mark.parametrize('p, exp_m, exp_r', (
    #     (Position(0, 0), None, None),  # outside mirror
    #     (Position(1, 1), None, Position(1, 1)),
    #     (Position(2, 2), None, Position(2, 2)),
    #     (Position(3, 3), None, Position(3, 3)),
    #     (Position(4, 4), None, Position(4, 4)),
    #     (Position(5, 5), Position(4, 5), None),
    #     (Position(6, 6), Position(3, 6), None),
    #     (Position(7, 5), Position(2, 5), None),
    #     (Position(8, 4), Position(1, 4), None),
    # ))
    # def test_horizontal_mirror_image(self, p, exp_m, exp_r):
    #     mirror = Position(4, 0)
    #     size = Position(9, 7)
    #     mirror, reality = p.mirror_image(mirror, size, Position.mirror_size(mirror, size))
    #     if isinstance(exp_m, Position):
    #         assert mirror == exp_m
    #     else:
    #         assert mirror is exp_m
    #     if isinstance(exp_r, Position):
    #         assert reality == exp_r
    #     else:
    #         assert reality is exp_r
    #
    # @pytest.mark.parametrize('p, exp_m, exp_r', (
    #     (Position(0, 0), None, None),  # outside
    #     (Position(1, 1), None, Position(1, 1)),
    #     (Position(2, 2), None, Position(2, 2)),
    #     (Position(3, 3), None, Position(3, 3)),
    #     (Position(4, 4), Position(4, 3), None),
    #     (Position(5, 5), Position(5, 2), None),
    #     (Position(6, 6), Position(6, 1), None),
    #     (Position(7, 5), Position(7, 2), None),
    #     (Position(8, 4), Position(8, 3), None),  # outside
    # ))
    # def test_vertical_mirror_image(self, p, exp_m, exp_r):
    #     mirror = Position(0, 3)
    #     size = Position(9, 7)
    #     mirror, reality = p.mirror_image(mirror, size, Position.mirror_size(mirror, size))
    #     if isinstance(exp_m, Position):
    #         assert mirror == exp_m
    #     else:
    #         assert mirror is exp_m
    #     if isinstance(exp_r, Position):
    #         assert reality == exp_r
    #     else:
    #         assert reality is exp_r

    @pytest.mark.parametrize(
        'size, mirror, exp',
        (
            (Position(9, 7), Position(5, 0), Position(3, 1)),
            (Position(9, 7), Position(0, 3), Position(1, 3)),
            (Position(9, 7), Position(1, 0), Position(2, 1)),
            (Position(9, 7), Position(0, 4), Position(1, 2)),
        ),
    )
    def test_mirror_size(self, size, mirror, exp):
        assert Position.mirror_size(mirror, size) == exp

    @pytest.mark.parametrize(
        'mirror, exp',
        (
            (Position(4, None), 5),
            (Position(None, 3), 400),
            (Position(0, None), 1),
            (Position(None, 0), 100),
        ),
    )
    def test_score(self, mirror, exp):
        assert mirror.score == exp


class TestPattern:
    @pytest.mark.parametrize(
        'idx, exp_mirror',
        (
            (0, Position(4, None)),
            (1, Position(None, 3)),
        ),
    )
    def test_find_mirror_small_ex(self, small_ex_txt, idx, exp_mirror):
        pattern = Pattern.from_file(small_ex_txt)[idx]
        assert pattern.find_mirror() == exp_mirror

    @pytest.mark.parametrize(
        'idx, exp_mirror',
        (
            (0, Position(1, None)),
            (1, Position(0, None)),
            (99, Position(None, 10)),
        ),
    )
    def test_find_mirror_input(self, input_txt, idx, exp_mirror):
        pattern = Pattern.from_file(input_txt)[idx]
        assert pattern.find_mirror() == exp_mirror


class TestQ1:
    def test_small_ex(self, small_ex_txt):
        assert q1(Pattern.from_file(small_ex_txt)) == 405

    def test_input(self, input_txt):
        assert q1(Pattern.from_file(input_txt)) == 28895
