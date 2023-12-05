import dataclasses
import re
from argparse import ArgumentParser
from enum import Enum
from operator import attrgetter
from typing import (
    IO,
    Dict,
    Iterable,
    List,
    Optional,
    Self,
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
        return self.source_start + self.length

    @property
    def destination_end(self) -> int:
        return self.destination_start + self.length

    def __contains__(self, item: int) -> bool:
        return self.source_start <= item < self.source_end

    def convert(self, value: int) -> Optional[int]:
        if value in self:
            step = value - self.source_start
            return self.destination_start + step
        return None


@dataclasses.dataclass
class AlmanacEntry:
    source: Subject
    destination: Subject

    mappings: List[Mapping]

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
                        mappings=sorted(current_mappings, key=attrgetter('source_start')),
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
                mappings=sorted(current_mappings, key=attrgetter('source_start')),
            )

    def convert(self, value: int) -> int:
        # TODO(tr) if too slow we could do binary search there as our mappings are
        #  sorted by source_start
        for mapping in self.mappings:
            new_value = mapping.convert(value)
            if new_value is not None:
                return new_value
        # if not in mapping, return the value as is
        return value


@dataclasses.dataclass
class Almanac:
    original_seeds: List[int]
    entries: Dict[Subject, AlmanacEntry]

    @classmethod
    def from_file(cls, filename: str) -> Self:
        print(f'Loading {filename}')
        with open(filename, 'r') as fin:
            # first line are seeds
            # r"seeds:(\s\d+)+"
            line = fin.readline()
            seeds_line = line.split(': ')[-1]
            original_seeds = list(map(int, seeds_line.split(' ')))

            entries = {entry.source: entry for entry in AlmanacEntry.from_file(fin)}

        return cls(original_seeds=original_seeds, entries=entries)

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


def q1(almanac: Almanac) -> int:
    return min((almanac.convert(seed, Subject.Seed, Subject.Location) for seed in almanac.original_seeds))


def main(filename: str):
    almanac = Almanac.from_file(filename)

    print(f'Q1: closest location is {q1(almanac)}')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    main(args.input)
