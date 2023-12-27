import os

import pytest

from day_24.compute import (
    DEF_ZONE,
    Hailstone,
)
from day_24.compute import Position as P
from day_24.compute import q1


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


class TestHailstone:
    @pytest.mark.parametrize(
        'line, exp_start, exp_velocity',
        (
            ('19, 13, 30 @ -2, 1, -2', P(19.0, 13.0, 30.0), P(-2.0, 1.0, -2.0)),
            ('18, 19, 22 @ -1, -1, -2', P(18.0, 19.0, 22.0), P(-1.0, -1.0, -2.0)),
            ('20, 25, 34 @ -2, -2, -4', P(20.0, 25.0, 34.0), P(-2.0, -2.0, -4.0)),
            ('12, 31, 28 @ -1, -2, -1', P(12.0, 31.0, 28.0), P(-1.0, -2.0, -1.0)),
            ('20, 19, 15 @  1, -5, -3', P(20.0, 19.0, 15.0), P(1.0, -5.0, -3.0)),
        ),
    )
    def test_trajectory(self, line, exp_start, exp_velocity):
        hail = Hailstone.from_line(line)
        assert hail.start == exp_start
        assert hail.velocity == exp_velocity

        next_point = exp_start + exp_velocity
        next_point = P(
            next_point.x,
            next_point.y,
            hail.start.z,
        )
        build_next_point = hail.make_point_at(next_point.x)

        assert str(next_point) == str(build_next_point)

    def test_intersection(self, small_ex_txt):
        hailstorm = Hailstone.from_file(small_ex_txt)
        intersection = []
        for i, hailstone in enumerate(hailstorm):
            for other_hailstone in hailstorm[i + 1:]:
                intersection.append(
                    str(hailstone.intersection(other_hailstone)),
                )
        assert intersection == [
            '(14.33, 15.33, 30.00)',
            '(11.67, 16.67, 30.00)',
            '(6.20, 19.40, 30.00)',
            'None',  # in past
            'None',  # parallels
            '(-6.00, -5.00, 22.00)',
            'None',  # in past
            '(-2.00, 3.00, 34.00)',
            'None',  # in past
            'None',  # in past
        ]


class TestQ1:
    def test_small_ex(self, small_ex_txt):
        assert q1(Hailstone.from_file(small_ex_txt), (7.0, 27.0)) == 2

    def test_input(self, input_txt):
        assert q1(Hailstone.from_file(input_txt), DEF_ZONE) == 14046
