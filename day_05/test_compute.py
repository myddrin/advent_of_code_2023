import os
from operator import attrgetter

import pytest

from day_05.compute import (
    Almanac,
    AlmanacEntry,
    Mapping,
    Subject,
    q1,
    q2_brute,
    q2_threaded,
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
    seed_to_soil = (
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
    )

    @pytest.mark.parametrize(
        'seed, soil',
        seed_to_soil,
    )
    def test_convert(self, seed, soil):
        almanac_entry = AlmanacEntry(
            source=Subject.Seed,
            destination=Subject.Soil,
            mappings=sorted(
                [
                    Mapping(50, 98, 2),
                    Mapping(52, 50, 48),
                ],
                key=attrgetter('source_start'),
            ),
        )
        assert almanac_entry._dumb_convert(seed) == almanac_entry.convert(seed) == soil

    @pytest.mark.parametrize('seed, soil', seed_to_soil)
    def test_revert(self, seed, soil):
        almanac_entry = AlmanacEntry(
            source=Subject.Seed,
            destination=Subject.Soil,
            mappings=[
                Mapping(50, 98, 2),
                Mapping(52, 50, 48),
            ],
        )
        assert almanac_entry.reverse(soil) == seed

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
            (79, 93 - 79),
            (55, 68 - 55),
        ]

    def test_unpack_seeds(self, small_ex_txt):
        almanac = Almanac.from_file(small_ex_txt)
        assert list(almanac.unpack_seeds()) == list(range(79, 93)) + list(range(55, 68))

    @pytest.mark.parametrize('input_simplify, simplify_with', ((Subject.Seed, Subject.Soil),))
    def test_simplify(self, small_ex_txt, input_simplify, simplify_with):
        almanac = Almanac.from_file(small_ex_txt)
        seed_entry = almanac.entries[input_simplify]
        st = min((m.source_start for m in seed_entry.mappings))
        ed = max((m.source_end for m in seed_entry.mappings))

        other_entry = almanac.entries[simplify_with]
        output_simplify = other_entry.destination

        print(
            f'Simplifying from {seed_entry.source}->{seed_entry.destination} with {other_entry.source}->{other_entry.destination}',
        )
        simpler = seed_entry.simplify(other_entry)
        assert simpler.source == seed_entry.source == input_simplify
        assert simpler.destination == other_entry.destination == output_simplify

        st = min((st, min((seed_entry.reverse(m.source_start) for m in other_entry.mappings))))
        ed = max((ed, max((seed_entry.reverse(m.source_end) for m in other_entry.mappings))))

        assert simpler.destination == other_entry.destination == output_simplify
        if simplify_with == Subject.Soil:
            assert st == 0, 'sanity'
            assert ed == 99, 'sanity'

        for i in range(st, ed + 1):
            v = simpler.convert(i) == other_entry.convert(seed_entry.convert(i))
            if not v:
                assert v, f'For {i}->{simpler.convert(i)} vs {i}->{seed_entry.convert(i)}->{other_entry.convert(seed_entry.convert(i))}'


class TestQ1:
    def test_small_ex(self, small_ex_txt):
        assert q1(Almanac.from_file(small_ex_txt)) == 35

    def test_input(self, input_txt):
        assert q1(Almanac.from_file(input_txt)) == 388071289


class TestQ2:
    def test_small_ex_brute(self, small_ex_txt):
        assert q2_brute(Almanac.from_file(small_ex_txt)) == 46

    def test_small_ex_threaded(self, small_ex_txt):
        assert q2_threaded(Almanac.from_file(small_ex_txt)) == 46
