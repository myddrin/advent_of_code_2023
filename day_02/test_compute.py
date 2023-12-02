import os

import pytest

from day_02.compute import (
    Game,
    Record,
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


class TestRecord:
    @pytest.mark.parametrize(
        'line, expected',
        (
            ('3 blue, 4 red, 2 green', [Record(blue=3, red=4, green=2)]),
            ('1 blue, 2 green', [Record(blue=1, green=2)]),
            ('15 blue', [Record(blue=15)]),
            # ('', []),
            (
                '3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green',
                [
                    Record(blue=3, red=4),
                    Record(red=1, green=2, blue=6),
                    Record(green=2),
                ],
            ),
        ),
    )
    def test_from_line(self, line, expected):
        assert Record.from_line(line) == expected


class TestGame:
    @pytest.mark.parametrize(
        'line, expected',
        (
            (
                'Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green',
                Game(1, [Record(blue=3, red=4), Record(red=1, green=2, blue=6), Record(green=2)]),
            ),
            (
                'Game 10: 6 red, 1 blue, 3 green; 2 blue, 1 red, 2 green',
                Game(10, [Record(red=6, blue=1, green=3), Record(blue=2, red=1, green=2)]),
            ),
            # (
            #     'Game 2: ',
            #     Game(2, []),
            # ),
        ),
    )
    def test_from_line(self, line, expected):
        assert Game.from_line(line) == expected


class TestQ1:
    def test_small_ex(self, small_ex_txt):
        data = Game.from_file(small_ex_txt)
        assert q1(data) == 8

    def test_input(self, input_txt):
        data = Game.from_file(input_txt)
        assert q1(data) == 2600
