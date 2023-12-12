import os

import pytest

from day_12.compute import (
    SpringRow,
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


class TestSpringRow:
    @pytest.mark.parametrize(
        'line',
        (
            '#.#.### 1,1,3',
            '.#...#....###. 1,1,3',
            '.#.###.#.###### 1,3,1,6',
            '####.#...#... 4,1,1',
            '#....######..#####. 1,6,5',
            '.###.##....# 3,2,1',
        ),
    )
    def test_build_checksum(self, line: str):
        spring_row = SpringRow.from_line(line)
        assert spring_row.n_unknown == 0
        assert SpringRow.build_checksum(spring_row.map_data) == spring_row.checksum

    def test_load_unknown(self):
        spring_row = SpringRow.from_line('???.### 1,1,3')
        assert spring_row.n_unknown == 3
        assert spring_row.checksum == [1, 1, 3]

    def test_build_checksum_reject_nones(self):
        spring_row = SpringRow.from_line('???.### 1,1,3')
        with pytest.raises(ValueError, match=r'Cannot have None when building checksum: map_data\[0\]'):
            SpringRow.build_checksum(spring_row.map_data)

    @pytest.mark.parametrize(
        'line, expected',
        (
            ('???.### 1,1,3', 1),
            ('.??..??...?##. 1,1,3', 4),
            ('?###???????? 3,2,1', 10),
        ),
    )
    def test_fill_gaps(self, line, expected):
        spring_row = SpringRow.from_line(line)
        assert spring_row.fill_gaps() == expected


class TestQ1:
    def test_small_ex(self, small_ex_txt):
        assert q1(SpringRow.from_file(small_ex_txt)) == 21

    def test_input(self, input_txt):
        assert q1(SpringRow.from_file(input_txt)) == 7350
