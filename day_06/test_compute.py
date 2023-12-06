import os

import pytest

from day_06.compute import (
    Record,
    count_points,
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
        'race_duration, race_record, exp',
        (
            # in array of 7: first attempt is 3->12mm that is higher than the record already!
            (7, 9, (1, 3)),
            # in array of 15: first attempt is 7->56mm that is higher than the record already!
            (15, 40, (1, 7)),
            # in array of 30: first attempt is 14->224mm that is higher than the record already!
            (30, 200, (1, 14)),
        ),
    )
    def test_find_some_record_holding_time(self, race_duration, race_record, exp, small_ex_txt):
        record = Record(race_duration, race_record)
        assert record.find_some_record_holding_time() == exp

    @pytest.mark.parametrize(
        'race_duration, race_record, exp_win',
        (
            (7, 9, 4),
            (15, 40, 8),
            (30, 200, 9),
            (42686985, 284100511221341, 26187338),
        ),
    )
    def test_clever_race_plan(self, race_duration, race_record, exp_win):
        record = Record(race_duration, race_record)
        assert record.clever_race_plans() == exp_win


class TestQ1:
    def test_small_ex(self, small_ex_txt):
        assert count_points(Record.from_file(small_ex_txt)) == 288

    def test_input(self, input_txt):
        assert count_points(Record.from_file(input_txt)) == 440000


class TestQ2:
    def test_small_ex(self, small_ex_txt):
        assert count_points(Record.from_file(small_ex_txt, fix_spaces=True)) == 71503

    def test_input(self, input_txt):
        assert count_points(Record.from_file(input_txt, fix_spaces=True)) == 26187338
