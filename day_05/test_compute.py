import os
from operator import attrgetter
from typing import List

import pytest

from day_05.compute import (
    Almanac,
    AlmanacEntry,
    Mapping,
    Range,
    Subject,
    q1,
    q2_range,
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


class TestMapping:
    @pytest.mark.parametrize(
        'data, exp_conv, exp_pending',
        (
            (Range(5, 4), Range(7, 4), []),
            (Range(3, 4), Range(6, 3), [Range(3, 1)]),
            (Range(7, 4), Range(9, 3), [Range(10, 1)]),
            (Range(2, 10), Range(6, 6), [Range(2, 2), Range(10, 2)]),
            (Range(0, 2), None, [Range(0, 2)]),
            (Range(12, 2), None, [Range(12, 2)]),
            (Range(9, 2), Range(11, 1), [Range(10, 1)]),
        ),
    )
    def test_convert_range(self, data: Range, exp_conv: List[Range], exp_pending: List[Range]):
        mapping = Mapping(6, 4, 6)  # 4 -> 6 until 9 -> 11

        converted, pending = mapping.convert_range(data)
        if exp_conv is None:
            assert converted is None
        else:
            assert converted == exp_conv, 'converted'
        assert pending == exp_pending, 'pending'


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
        assert almanac_entry.convert_int(seed) == soil

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
        assert almanac_entry.reverse_int(soil) == seed

    def test_original_seed_to_soil(self, small_ex_txt):
        almanac = Almanac.from_file(small_ex_txt)
        soil = [almanac.entries[Subject.Seed].convert_int(seed) for seed in almanac.original_seeds]
        assert soil == [81, 14, 57, 13]

    @pytest.mark.parametrize(
        'data, exp_ranges',
        (
            ([Range(0, 2)], [Range(0, 2)]),
            (
                [Range(0, 2), Range(2, 10)],
                [
                    # 0-11 yields:
                    Range(0, 2),
                    # 2-11 yields:
                    Range(2, 2),
                    Range(6, 6),
                    Range(10, 1),
                    Range(5, 1),
                ],
            ),
            (
                [
                    Range(0, 2),
                    Range(2, 10),
                    Range(3, 3),
                ],
                [
                    # 0-11 yields:
                    Range(0, 2),
                    # 2-11 yields:
                    Range(2, 2),
                    Range(6, 6),
                    Range(10, 1),
                    Range(5, 1),
                    # 3-6 yields:
                    Range(3, 1),
                    Range(6, 2),
                ],
            ),
            (
                [
                    Range(0, 2),
                    Range(2, 10),
                    Range(3, 3),
                    Range(5, 4),
                ],
                [
                    # 0-11 yields:
                    Range(0, 2),
                    # 2-11 yields:
                    Range(2, 2),
                    Range(6, 6),
                    Range(10, 1),
                    Range(5, 1),
                    # 3-6 yields:
                    Range(3, 1),
                    Range(6, 2),
                    # 5-8 yields:
                    Range(7, 4),
                ],
            ),
            (
                [
                    Range(0, 2),
                    Range(2, 10),
                    Range(3, 3),
                    Range(5, 4),
                    Range(7, 4),
                ],
                [
                    # 0-11 yields:
                    Range(0, 2),
                    # 2-11 yields:
                    Range(2, 2),
                    Range(6, 6),
                    Range(10, 1),
                    Range(5, 1),
                    # 3-6 yields:
                    Range(3, 1),
                    Range(6, 2),
                    # 5-8 yields:
                    Range(7, 4),
                    # 7-10 yields
                    Range(9, 3),
                    Range(10, 1),
                ],
            ),
            (
                [
                    Range(0, 2),
                    Range(2, 10),
                    Range(3, 3),
                    Range(5, 4),
                    Range(7, 4),
                    Range(12, 2),
                ],
                [
                    # 0-11 yields:
                    Range(0, 2),
                    # 2-11 yields:
                    Range(2, 2),
                    Range(6, 6),
                    Range(10, 1),
                    Range(5, 1),
                    # 3-6 yields:
                    Range(3, 1),
                    Range(6, 2),
                    # 5-8 yields:
                    Range(7, 4),
                    # 7-10 yields
                    Range(9, 3),
                    Range(10, 1),
                    # 12-13 yields
                    Range(6, 1),
                    Range(13, 1),
                ],
            ),
        ),
    )
    def test_convert_range(self, data, exp_ranges):
        almanac_entry = AlmanacEntry(
            source=Subject.Seed,
            destination=Subject.Soil,
            mappings=[
                Mapping(6, 4, 6),
                Mapping(5, 11, 2),
            ],
        )
        assert almanac_entry.convert_ranges(data) == sorted(set(exp_ranges))


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
        locations = [
            almanac.convert_smallest_range(Range(seed, 1), Subject.Seed).start for seed in almanac.original_seeds
        ]
        assert locations == [
            82,
            43,
            86,
            35,
        ]

    def test_unpack_seed_ranges(self, small_ex_txt):
        almanac = Almanac.from_file(small_ex_txt)
        assert list(almanac.unpack_seed_ranges()) == [
            Range(79, 93 - 79),
            Range(55, 68 - 55),
        ]

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

        st = min((st, min((seed_entry.reverse_int(m.source_start) for m in other_entry.mappings))))
        ed = max((ed, max((seed_entry.reverse_int(m.source_end) for m in other_entry.mappings))))

        assert simpler.destination == other_entry.destination == output_simplify
        if simplify_with == Subject.Soil:
            assert st == 0, 'sanity'
            assert ed == 99, 'sanity'

        for i in range(st, ed + 1):
            v = simpler.convert_int(i) == other_entry.convert_int(seed_entry.convert_int(i))
            if not v:
                assert v, f'For {i}->{simpler.convert_int(i)} vs {i}->{seed_entry.convert_int(i)}->{other_entry.convert_int(seed_entry.convert_int(i))}'


@pytest.mark.parametrize('simplify', (True, False))
class TestQ1:
    def test_small_ex(self, small_ex_txt, simplify):
        assert q1(Almanac.from_file(small_ex_txt, simplify=simplify)) == 35

    def test_input(self, input_txt, simplify):
        assert q1(Almanac.from_file(input_txt, simplify=simplify)) == 388071289


@pytest.mark.parametrize('simplify', (True, False))
class TestQ2:
    def test_small_ex_range(self, small_ex_txt, simplify):
        assert q2_range(Almanac.from_file(small_ex_txt, simplify=simplify)) == 46

    def test_input(self, input_txt, simplify):
        assert q2_range(Almanac.from_file(input_txt, simplify=simplify)) == 84206669
