import dataclasses
import re
from argparse import ArgumentParser
from typing import (
    ClassVar,
    Iterable,
    List,
    Self,
)


@dataclasses.dataclass(frozen=True)
class Position:
    x: int
    y: int

    @property
    def neighbours(self) -> Iterable[Self]:
        for y in range(self.y - 1, self.y + 2):
            for x in range(self.x - 1, self.x + 2):
                if x != self.x or y != self.y:
                    yield Position(x, y)

    def __str__(self):
        return f'({self.x}, {self.y})'


@dataclasses.dataclass
class Gear:
    """A gear is any '*' adjacent to exactly two parts"""

    symbol: ClassVar[str] = '*'

    position: Position
    first_part: int
    second_part: int

    @property
    def gear_ratio(self) -> int:
        return self.first_part * self.second_part


@dataclasses.dataclass
class Schematic:
    # digits and '.' are not symbols
    symbols_re: ClassVar = re.compile(r'[^\d.]')

    data: List[str]  # 2D array of data, the rows are the strings
    symbols: List[Position]

    @classmethod
    def from_file(cls, filename: str) -> Self:
        print(f'Loading {filename}')
        data = []
        symbols = []
        with open(filename, 'r') as fin:
            for y, line in enumerate(fin):
                line = line.replace('\n', '')
                data.append(line)
                for match in cls.symbols_re.finditer(line):
                    symbols.append(Position(x=match.start(), y=y))
        return cls(data, symbols)

    def is_digit(self, p: Position) -> bool:
        try:
            int(self.data[p.y][p.x])
        except (ValueError, IndexError):
            return False
        else:
            return True

    def extract_number_at(self, p: Position) -> int:
        source_str = self.data[p.y]
        not_digit_re = re.compile(r'[^\d]')

        start = p.x
        end = p.x
        while start >= 0:
            if not_digit_re.match(source_str[start]):
                break
            start -= 1
        while end < len(source_str):
            if not_digit_re.match(source_str[end]):
                break
            end += 1

        slice = source_str[start + 1 : end]
        return int(slice)

    def find_numbers_adjacent_to_symbols(self) -> List[int]:
        # I'll assume the same number cannot be counted twice

        # To no extract numbers multiple times if symbols touch the same position
        # I first gather positions
        all_numbers: List[int] = []

        for symbol_loc in self.symbols:
            # I'll assume the same piece cannot be next to the same symbol twice
            adjacent_numbers = set()
            for neighbour in symbol_loc.neighbours:
                if self.is_digit(neighbour):
                    adjacent_numbers.add(self.extract_number_at(neighbour))
            all_numbers.extend(adjacent_numbers)

        # returns the unique list of numbers as a number covering multiple
        # position could appear twice
        return all_numbers

    def find_gears(self) -> List[Gear]:
        all_gears: List[Gear] = []

        for symbol_loc in self.symbols:
            the_symbol = self.data[symbol_loc.y][symbol_loc.x]
            if the_symbol != Gear.symbol:
                continue

            adjacent_numbers = set()
            for neighbour in symbol_loc.neighbours:
                if self.is_digit(neighbour):
                    adjacent_numbers.add(self.extract_number_at(neighbour))
            if len(adjacent_numbers) != 2:
                continue  # a gear has exactly 2 neighbours

            # sorting to help unit tests - simple iteration is enough, but it's only 2 elements
            parts = sorted(adjacent_numbers)
            all_gears.append(Gear(symbol_loc, parts[0], parts[1]))

        return all_gears


def q1(schematic: Schematic) -> int:
    return sum(schematic.find_numbers_adjacent_to_symbols())


def q2(schematic: Schematic) -> int:
    return sum((gear.gear_ratio for gear in schematic.find_gears()))


def main(filename: str):
    data = Schematic.from_file(filename)

    print(f'Q1: sum of parts: {q1(data)}')
    print(f'Q2: sum of gear ratio: {q2(data)}')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    main(args.input)
