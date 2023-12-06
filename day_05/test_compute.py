import os

import pytest

from day_05.compute import (
    Almanac,
    AlmanacEntry,
    Mapping,
    Subject,
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


class TestAlmanacEntry:
    @pytest.mark.parametrize(
        'seed, soil',
        (
            (0, 0),
            (1, 1),
            (48, 48),
            (49, 49),
            (50, 52),
            (51, 53),
            (96, 98),
            (97, 99),
            (98, 50),
            (99, 51),
        ),
    )
    def test_convert(self, seed, soil):
        almanac_entry = AlmanacEntry(
            source=Subject.Seed,
            destination=Subject.Soil,
            mappings=[
                Mapping(50, 98, 2),
                Mapping(52, 50, 48),
            ],
        )
        assert almanac_entry.convert(seed) == soil

    def test_original_seed_to_soil(self, small_ex_txt):
        almanac = Almanac.from_file(small_ex_txt)
        soil = [almanac.entries[Subject.Seed].convert(seed) for seed in almanac.original_seeds]
        assert soil == [81, 14, 57, 13]


class TestAlmanac:
    def test_load(self, small_ex_txt):
        almanac = Almanac.from_file(small_ex_txt)

        assert almanac.original_seeds == [79, 14, 55, 13]

        for s in Subject:
            if s != Subject.Location:
                assert almanac.entries[s].source == s
                assert almanac.entries[s].destination == Subject(s.value + 1)
            else:
                assert s not in almanac.entries

        assert almanac.entries[Subject.Seed].mappings == [
            Mapping(52, 50, 48),
            Mapping(50, 98, 2),
        ]
        # ...
        assert almanac.entries[Subject.Humidity].mappings == [
            Mapping(60, 56, 37),
            Mapping(56, 93, 4),
        ]

    def test_convert(self, small_ex_txt):
        almanac = Almanac.from_file(small_ex_txt)
        locations = [almanac.convert(seed, Subject.Seed) for seed in almanac.original_seeds]
        assert locations == [
            82,
            43,
            86,
            35,
        ]

    def test_unpack_seed_ranges(self, small_ex_txt):
        almanac = Almanac.from_file(small_ex_txt)
        assert list(almanac.unpack_seed_ranges()) == [
            list(range(79, 93)),
            list(range(55, 68)),
        ]


class TestQ1:
    def test_small_ex(self, small_ex_txt):
        assert q1(Almanac.from_file(small_ex_txt)) == 35

    def test_input(self, input_txt):
        assert q1(Almanac.from_file(input_txt)) == 388071289


class TestQ2:
    def test_small_ex(self, small_ex_txt):
        assert q2(Almanac.from_file(small_ex_txt)) == 46
