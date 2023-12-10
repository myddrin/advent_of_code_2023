import dataclasses
import re
import time
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from enum import Enum
from operator import attrgetter
from typing import (
    IO,
    Dict,
    Iterable,
    List,
    Optional,
    Self,
    Tuple,
)


class Subject(Enum):
    Seed = 1
    Soil = 2
    Fertilizer = 3
    Water = 4
    Light = 5
    Temperature = 6
    Humidity = 7
    Location = 8


@dataclasses.dataclass(frozen=True)
class Range:
    start: int
    length: int

    @property
    def end(self) -> int:
        return self.start + self.length - 1

    def __lt__(self, other: Self) -> bool:
        return self.start < other.start

    def contains(self, value: int) -> bool:
        return self.start <= value <= self.end

    def merge(self, other: Self) -> List[Self]:
        if self.end == other.start:
            return [Range(self.start, self.length + other.length)]
        elif self.start == other.end:
            return [Range(other.start, other.length + self.length)]
        return [self, other]

    def generate(self) -> Iterable[int]:
        return range(self.start, self.start + self.length)


@dataclasses.dataclass(frozen=True)
class Mapping:
    destination_start: int
    source_start: int
    length: int

    @classmethod
    def from_line(cls, line: str) -> Self:
        dest, src, length = list(map(int, line.split(' ')))
        return cls(source_start=src, destination_start=dest, length=length)

    @property
    def source_end(self) -> int:
        return self.source_start + self.length - 1

    @property
    def destination_end(self) -> int:
        return self.destination_start + self.length - 1

    def in_forward(self, item: int) -> bool:
        return self.source_start <= item <= self.source_end

    def in_backward(self, item: int) -> bool:
        return self.destination_start <= item <= self.destination_end

    def reverse(self, value: int) -> Optional[int]:
        if self.in_backward(value):
            step = value - self.destination_start
            return self.source_start + step

        return None

    def convert_int(self, value: int) -> Optional[int]:
        if self.in_forward(value):
            step = value - self.source_start
            return self.destination_start + step

        return None

    def convert_range(self, range: Range) -> Tuple[Optional[Range], List[Range]]:
        """
        :param range:
        :return: tuple of (converted range, not converted ranges)
        The converted range can be None if nothing was converted.
        The not converted ranges can be an empty list if the range was fully converted
        """

        start_present = self.in_forward(range.start)
        end_present = self.in_forward(range.end)

        if start_present:
            if end_present:
                # easy case: translate the range and done!
                converted = Range(self.convert_int(range.start), range.length)
                pending = []
            else:
                new_length = range.length - (range.end - self.source_end)
                converted = Range(self.convert_int(range.start), new_length)
                pending = [Range(self.source_end + 1, range.length - new_length)]
        elif end_present:
            # no start but end only
            new_length = range.length - (self.source_start - range.start)
            converted = Range(self.destination_start, new_length)
            pending = [Range(range.start, range.length - new_length)]
        elif range.contains(self.source_start) and range.contains(self.source_end):
            # the range is not within this Mapping, but may be around it
            converted = Range(self.destination_start, self.length)
            new_length_left = self.source_start - range.start
            new_length_right = range.end - self.source_end
            pending = [
                Range(range.start, new_length_left),
                Range(self.source_start + self.length, new_length_right),
            ]
        else:
            converted = None
            pending = [range]

        return converted, pending


@dataclasses.dataclass
class AlmanacEntry:
    source: Subject
    destination: Subject

    mappings: List[Mapping]

    def __post_init__(self):
        self.mappings = sorted(self.mappings, key=attrgetter('source_start'))
        all_mappings = sum((m.length for m in self.mappings))
        start_mapping = min((m.source_start for m in self.mappings))
        end_mapping = max((m.source_end for m in self.mappings))
        print(
            f'  Loaded Mapping({self.source.name} -> {self.destination.name}) of {all_mappings} data '
            f'from {start_mapping} until {end_mapping} (with {len(self.mappings)} mappings)',
        )

    @classmethod
    def from_file(cls, fileio: IO) -> Iterable[Self]:
        title_re = re.compile(r'(.*)-to-(.*) map:')

        current_source = None
        current_destination = None
        current_mappings = []

        for line in fileio:
            line = line.replace('\n', '')
            if not line:
                continue

            if title_match := title_re.match(line):
                if current_source is not None:
                    yield cls(
                        source=current_source,
                        destination=current_destination,
                        # sort it by source_start in case we want to do a binary
                        # search later, and to help testing
                        mappings=current_mappings,
                    )
                current_mappings = []  # make a new one!
                current_source = Subject[title_match.group(1).title()]
                current_destination = Subject[title_match.group(2).title()]
            else:
                current_mappings.append(Mapping.from_line(line))

        if current_source is not None:
            yield cls(
                source=current_source,
                destination=current_destination,
                # sort it by source_start in case we want to do a binary
                # search later, and to help testing
                mappings=current_mappings,
            )

    def get_mapping_for(self, value: int) -> Optional[Mapping]:
        for mapping in self.mappings:
            if mapping.in_forward(value):
                return mapping
        return None

    def simplify(self, other: Self) -> Self:
        if self.destination != other.source:
            raise ValueError('Cannot simplify')

        new_mappings = []
        all_sources = set()
        for mapping in self.mappings:
            all_sources.add(mapping.source_start - 1)
            all_sources.add(mapping.source_start)
            all_sources.add(mapping.source_end)
            all_sources.add(mapping.source_end + 1)

        for mapping in other.mappings:
            all_sources.add(self.reverse(mapping.source_start - 1))
            all_sources.add(self.reverse(mapping.source_start))
            all_sources.add(self.reverse(mapping.source_end))
            all_sources.add(self.reverse(mapping.source_end + 1))

        sorted_sources = sorted(all_sources)
        for i in range(len(sorted_sources) - 1):
            current = sorted_sources[i]
            next_one = sorted_sources[i + 1]
            new_mappings.append(
                Mapping(
                    source_start=current,
                    destination_start=other.convert_int(self.convert_int(sorted_sources[i])),
                    length=next_one - current,
                ),
            )

        last = sorted_sources[-1]
        m = self.get_mapping_for(last)
        if m:
            new_mappings.append(
                Mapping(
                    source_start=last,
                    destination_start=other.convert_int(self.convert_int(last)),
                    length=(m.length - last + m.source_start),
                ),
            )
        else:
            new_mappings.append(
                Mapping(
                    source_start=last,
                    destination_start=other.convert_int(self.convert_int(last)),
                    length=1,
                ),
            )

        # simplify: remove mappings that use default
        new_mappings = sorted(
            [mapping for mapping in new_mappings if mapping.source_start != mapping.destination_start],
            key=attrgetter('source_start'),
        )
        # simplify: remove consecutive
        new_idx = 1
        final_mappings = [new_mappings[0]]
        while new_idx < len(new_mappings):
            current = new_mappings[new_idx]
            if final_mappings[-1].source_end == current.source_start:
                final_mappings[-1].length += current.length
            else:
                final_mappings.append(current)
            new_idx += 1

        return AlmanacEntry(
            source=self.source,
            destination=other.destination,
            mappings=final_mappings,
        )

    def reverse(self, value: int) -> int:
        # brute slow conversion - not used for critical path
        for mapping in self.mappings:
            new_value = mapping.reverse(value)
            if new_value is not None:
                return new_value
        # if not in mapping, return the value as is
        return value

    def _dumb_convert(self, value: int) -> int:
        # boring slow conversion - when it's too small to use binary search
        for mapping in self.mappings:
            new_value = mapping.convert_int(value)
            if new_value is not None:
                return new_value
        # if not in mapping, return the value as is
        return value

    def convert_int(self, value: int) -> int:
        # binary search
        low = 0
        high = len(self.mappings) - 1

        while low <= high:
            mid = (high + low) // 2
            current = self.mappings[mid]

            if (conv_value := current.convert_int(value)) is not None:
                return conv_value
            elif current.source_start < value:
                low = mid + 1
            else:
                high = mid - 1

        return value  # not found so not transformed

    def convert_ranges(self, data: List[Range]) -> List[Range]:
        converted = []
        convert_to_id = []
        left_to_convert = sorted(data)

        for m in self.mappings:
            pending = []
            for current in left_to_convert:
                new_conv, new_pending = m.convert_range(current)
                if new_conv is not None:
                    converted.append(new_conv)
                pending.extend(new_pending)
            left_to_convert = []
            for p in sorted(pending):  # smallest range first
                if p.start < m.source_start:
                    convert_to_id.append(p)
                else:
                    left_to_convert.append(p)

        return sorted(set(converted + convert_to_id + left_to_convert))


@dataclasses.dataclass
class Almanac:
    original_seeds: List[int]
    entries: Dict[Subject, AlmanacEntry]

    @classmethod
    def from_file(cls, filename: str, *, simplify: bool = False) -> Self:
        print(f'Loading {filename}')
        with open(filename, 'r') as fin:
            # first line are seeds
            # r"seeds:(\s\d+)+"
            line = fin.readline()
            seeds_line = line.split(': ')[-1]
            original_seeds = list(map(int, seeds_line.split(' ')))

            entries = {entry.source: entry for entry in AlmanacEntry.from_file(fin)}

        obj = cls(original_seeds=original_seeds, entries=entries)
        if simplify:
            obj = obj.simplify()
        return obj

    def unpack_seed_ranges(self) -> Iterable[Range]:
        if len(self.original_seeds) % 2 != 0:
            raise ValueError('Need an even number of seeds')
        left_seeds = list(self.original_seeds)
        while left_seeds:
            start = left_seeds.pop(0)
            n = left_seeds.pop(0)
            yield Range(start, n)

    def unpack_seeds(self) -> Iterable[int]:
        if len(self.original_seeds) % 2 != 0:
            raise ValueError('Need an even number of seeds')
        left_seeds = list(self.original_seeds)
        while left_seeds:
            start = left_seeds.pop(0)
            n = left_seeds.pop(0)
            yield from range(start, start + n)

    def convert_int(self, value: int, source: Subject, destination: Subject = Subject.Location) -> int:
        if destination == source:
            return value
        if destination.value < source.value:
            raise ValueError(f'Cannot convert backward from {source} to {destination}')

        current_value = value
        current_source = source

        while current_source in self.entries:
            entry = self.entries[current_source]
            current_value = entry.convert_int(current_value)
            current_source = entry.destination

            if current_source == destination:
                break  # we found it

        if current_source != destination:
            raise RuntimeError(f'Failed to convert {source} to {destination}')
        return current_value

    def convert_smallest_range(self, data: Range, source: Subject, destination: Subject = Subject.Location) -> Range:
        if destination == source:
            return data
        if destination.value < source.value:
            raise ValueError(f'Cannot convert backward from {source} to {destination}')

        current_values = [data]
        current_source = source

        while current_source in self.entries:
            entry = self.entries[current_source]
            current_values = entry.convert_ranges(current_values)
            current_source = entry.destination

            if current_source == destination:
                break  # we found it

        if current_source != destination:
            raise RuntimeError(f'Failed to convert {source} to {destination}')
        return current_values[0]

    def simplify(self) -> Self:
        current = self.entries[Subject.Seed]
        while next_step := self.entries.get(current.destination):
            print(f'Simplifying {current.source.name}->{current.destination.name}->{next_step.destination.name}')
            current = current.simplify(next_step)

        return Almanac(
            self.original_seeds,
            entries={current.source: current},
        )


def q1(almanac: Almanac) -> int:
    return min((almanac.convert_int(seed, Subject.Seed, Subject.Location) for seed in almanac.original_seeds))


def q2_brute(almanac: Almanac, print_at: int = 1000000) -> int:
    current_min = None
    unpacked_seeds_size = sum((almanac.original_seeds[2 * i + 1] for i in range(len(almanac.original_seeds) // 2)))
    print(f'Unpacked {len(almanac.original_seeds)} to {unpacked_seeds_size} seeds')
    start_time = last_time = time.time()
    for i, seed in enumerate(almanac.unpack_seeds(), start=1):
        location = almanac.convert_int(seed, Subject.Seed, Subject.Location)
        if current_min is None or location < current_min:
            current_min = location
        if i % print_at == 0:
            new_time = time.time()
            current_duration = new_time - last_time
            estimate = timedelta(seconds=(unpacked_seeds_size - i) * (current_duration / print_at))
            print(
                f'  after {i}/{unpacked_seeds_size} current_min={current_min} in {current_duration:0.2f}s -> estimate {estimate} left',
            )
            last_time = new_time
    print(f'Computed in {time.time() - start_time:0.2f} seconds')
    return current_min


def q2_range(almanac: Almanac) -> int:
    start_time = time.time()

    current_min = None
    for data in almanac.unpack_seed_ranges():
        location = almanac.convert_smallest_range(data, Subject.Seed, Subject.Location)
        if current_min is None or location < current_min:
            current_min = location

    print(f'Computed in {time.time() - start_time:0.2f} seconds')
    return current_min.start


def main(filename: str, simplify: bool):
    almanac = Almanac.from_file(filename, simplify=simplify)

    print(f'Q1: closest location is {q1(almanac)}')
    print(f'Q2: closest location with range {q2_range(almanac)}')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    parser.add_argument('--simplify-input', action='store_true', default=False)
    args = parser.parse_args()

    main(args.input, args.simplify_input)
