import os

import pytest

from day_03.compute import (
    Gear,
    Position,
    Schematic,
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
def input_txt():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'input.txt',
    )


class TestPosition:
    def test_neighbours(self):
        assert list(Position(1, 0).neighbours) == [
            Position(0, -1),
            Position(1, -1),
            Position(2, -1),
            Position(0, 0),
            Position(2, 0),
            Position(0, 1),
            Position(1, 1),
            Position(2, 1),
        ]


class TestGear:
    @pytest.mark.parametrize(
        'first, second',
        (
            (467, 35),
            (598, 755),
        ),
    )
    def test_gear_ratio(self, first, second):
        assert Gear(Position(0, 0), first, second).gear_ratio == first * second


class TestSchematic:
    def test_from_file(self, small_ex_txt):
        schematic = Schematic.from_file(small_ex_txt)
        assert set(schematic.symbols) == {
            Position(3, 1),  # '*'
            Position(6, 3),  # '#'
            Position(3, 4),  # '*'
            Position(5, 5),  # '+'
            Position(3, 8),  # '$'
            Position(5, 8),  # '*'
        }
        assert schematic.data == [
            '467..114..',
            '...*......',
            '..35..633.',
            '......#...',
            '617*......',
            '.....+.58.',
            '..592.....',
            '......755.',
            '...$.*....',
            '.664.598..',
        ]

    @pytest.mark.parametrize(
        'position, expected',
        (
            (Position(0, 0), True),  # '4'
            (Position(3, 1), False),  # '*'
            (Position(0, 1), False),  # '.'
        ),
    )
    def test_is_didit(self, small_ex_txt, position: Position, expected: bool):
        schematic = Schematic.from_file(small_ex_txt)
        assert schematic.is_digit(position) is expected

    @pytest.mark.parametrize(
        'position, expected',
        (
            (Position(0, 0), 467),  # at start of number + start of line
            (Position(2, 6), 592),  # at start of number but not start of line
            (Position(3, 2), 35),  # at end of number
            (Position(7, 2), 633),  # in the middle
            (Position(0, 4), 617),  # not next to a .
            (Position(9, 5), 589),  # at end of number + end of line
        ),
    )
    def test_extract_number_at(self, small_ex_txt, position: Position, expected: int):
        schematic = Schematic.from_file(small_ex_txt)
        schematic.data[5] = '.....+.589'  # change 58 to 589 and it finishes at the edge
        assert schematic.is_digit(position), 'sanity'
        assert schematic.extract_number_at(position) == expected

    def test_find_numbers_adjacent_to_symbols(self, small_ex_txt):
        schematic = Schematic.from_file(small_ex_txt)
        result = schematic.find_numbers_adjacent_to_symbols()
        # TODO(tr) not a good test if a piece number is repeated
        assert set(result) == {
            467,
            # 114,  # not adjacent
            35,
            633,
            617,
            # 58,  # not adjacent
            592,
            755,
            664,
            598,
        }

    def test_find_fears(self, small_ex_txt):
        schematic = Schematic.from_file(small_ex_txt)
        assert schematic.find_gears() == [
            Gear(Position(3, 1), 35, 467),
            Gear(Position(5, 8), 598, 755),
        ]


class TestQ1:
    def test_small_ex(self, small_ex_txt):
        assert q1(Schematic.from_file(small_ex_txt)) == 4361

    def test_input(self, input_txt):
        assert q1(Schematic.from_file(input_txt)) == 546563


class TestQ2:
    def test_small_ex(self, small_ex_txt):
        assert q2(Schematic.from_file(small_ex_txt)) == 467835

    def test_input(self, input_txt):
        assert q2(Schematic.from_file(input_txt)) == 91031374
