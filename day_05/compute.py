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

    def convert(self, value: int) -> Optional[int]:
        if self.in_forward(value):
            step = value - self.source_start
            return self.destination_start + step

        return None


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
                    destination_start=other.convert(self.convert(sorted_sources[i])),
                    length=next_one - current,
                ),
            )

        last = sorted_sources[-1]
        m = self.get_mapping_for(last)
        if m:
            new_mappings.append(
                Mapping(
                    source_start=last,
                    destination_start=other.convert(self.convert(last)),
                    length=(m.length - last + m.source_start),
                ),
            )
        else:
            new_mappings.append(
                Mapping(
                    source_start=last,
                    destination_start=other.convert(self.convert(last)),
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
            new_value = mapping.convert(value)
            if new_value is not None:
                return new_value
        # if not in mapping, return the value as is
        return value

    def convert(self, value: int) -> int:
        # binary search
        low = 0
        high = len(self.mappings) - 1

        while low <= high:
            mid = (high + low) // 2
            current = self.mappings[mid]

            if (conv_value := current.convert(value)) is not None:
                return conv_value
            elif current.source_start < value:
                low = mid + 1
            else:
                high = mid - 1

        return value  # not found so not transformed


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

    def unpack_seed_ranges(self, max_size: int = 10000000) -> Iterable[Tuple[int, int]]:
        if len(self.original_seeds) % 2 != 0:
            raise ValueError('Need an even number of seeds')
        left_seeds = list(self.original_seeds)
        while left_seeds:
            start = left_seeds.pop(0)
            n = left_seeds.pop(0)
            while n > 0:
                yield start, min(n, max_size)
                n -= max_size
                start += max_size

    def unpack_seeds(self) -> Iterable[int]:
        if len(self.original_seeds) % 2 != 0:
            raise ValueError('Need an even number of seeds')
        left_seeds = list(self.original_seeds)
        while left_seeds:
            start = left_seeds.pop(0)
            n = left_seeds.pop(0)
            yield from range(start, start + n)

    def convert(self, value: int, source: Subject, destination: Subject = Subject.Location) -> int:
        if destination == source:
            return value
        if destination.value < source.value:
            raise ValueError(f'Cannot convert backward from {source} to {destination}')

        current_value = value
        current_source = source

        while current_source in self.entries:
            entry = self.entries[current_source]
            current_value = entry.convert(current_value)
            current_source = entry.destination

            if current_source == destination:
                break  # we found it

        if current_source != destination:
            raise RuntimeError(f'Failed to convert {source} to {destination}')
        return current_value

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
    return min((almanac.convert(seed, Subject.Seed, Subject.Location) for seed in almanac.original_seeds))


def q2_brute(almanac: Almanac, print_at: int = 1000000) -> int:
    almanac = almanac.simplify()  # make things slower...

    current_min = None
    unpacked_seeds_size = sum((almanac.original_seeds[2 * i + 1] for i in range(len(almanac.original_seeds) // 2)))
    print(f'Unpacked {len(almanac.original_seeds)} to {unpacked_seeds_size} seeds')
    start_time = last_time = time.time()
    for i, seed in enumerate(almanac.unpack_seeds(), start=1):
        location = almanac.convert(seed, Subject.Seed, Subject.Location)
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


class ThreadedCompute:
    def __init__(self, *, almanac: Almanac, seed_range: Tuple[int, int], name: str):
        self.almanac = almanac
        self.seed_range = seed_range
        # self.found_min = None
        self.name = name
        self.print_at = 1000000
        # super().__init__(*args, **kwargs)

    def run(self) -> Optional[int]:
        found_min = None
        start_time = last_time = time.time()
        seed_start, unpacked_seeds_size = self.seed_range

        print(f' {self.name} is running for {unpacked_seeds_size} seeds')
        for i, seed in enumerate(range(seed_start, seed_start + unpacked_seeds_size), start=1):
            location = self.almanac.convert(seed, Subject.Seed, Subject.Location)
            if found_min is None or location < found_min:
                found_min = location
            if i % self.print_at == 0:
                new_time = time.time()
                current_duration = new_time - last_time
                estimate = timedelta(seconds=(unpacked_seeds_size - i) * (current_duration / self.print_at))
                print(
                    f' {self.name} after {i}/{unpacked_seeds_size} current_min={found_min} in {current_duration:0.2f}s -> estimate {estimate} left',
                )
                last_time = new_time

        print(f' {self.name} completed in {time.time() - start_time:0.2f}s')
        return found_min


def q2_threaded(almanac: Almanac, max_workers: int = None):
    # passing None runs with number of CPUs
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        wip = []
        total_seeds = 0
        for i, seed_batch in enumerate(almanac.unpack_seed_ranges()):  # type: int, Tuple[int, int]
            total_seeds += seed_batch[1]
            t = ThreadedCompute(
                almanac=almanac,
                seed_range=seed_batch,
                name=f'compute_{i:03d}',
            )
            wip.append(executor.submit(t.run))
        print(f'Created {len(wip)} tasks handled by {max_workers} workers to compute {total_seeds} seeds')
        return min((f.result() for f in wip))


def main(filename: str):
    almanac = Almanac.from_file(filename, simplify=True)

    print(f'Q1: closest location is {q1(almanac)}')
    print(f'Q2: closest location with range {q2_threaded(almanac)}')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    main(args.input)
