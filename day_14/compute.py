import dataclasses
from argparse import ArgumentParser
from collections import defaultdict
from enum import Enum
from typing import (
    Dict,
    Iterable,
    Self,
)


class Obstacle(Enum):
    Boulder = 'O'  # round rocks on the website
    Rock = '#'  # square rocks on the website
    Ground = '.'


@dataclasses.dataclass(frozen=True)
class Position:
    x: int
    y: int

    def __lt__(self, other: Self) -> bool:
        # raster order
        if self.y == other.y:
            return self.x < other.x
        return self.y < other.y

    def __add__(self, other: Self) -> Self:
        return Position(
            self.x + other.x,
            self.y + other.y,
        )

    def within(self, width: int, height: int) -> bool:
        return 0 <= self.x < width and 0 <= self.y < height


@dataclasses.dataclass
class Platform:
    objects: Dict[Position, Obstacle]
    width: int
    height: int

    @classmethod
    def from_file(cls, filename: str) -> Self:
        print(f'Loading {filename}')
        with open(filename, 'r') as fin:
            objects = {}
            y = 0
            width = 0
            for y, line in enumerate(fin):
                line = line.replace('\n', '')
                x = 0
                for x, char in enumerate(line):
                    obstacle = Obstacle(char)
                    if obstacle != Obstacle.Ground:
                        objects[Position(x, y)] = obstacle
                width = x + 1
            height = y + 1

            return cls(objects, width, height)

    def last_free_space(self, current: Position, direction: Position) -> Position:
        next_position = current + direction
        while next_position.within(self.width, self.height) and next_position not in self.objects:
            current += direction
            next_position += direction
        return current

    def _boulders(self) -> Iterable[Position]:
        for position, obstacle in self.objects.items():
            if obstacle == Obstacle.Boulder:
                yield position

    def tilt_north(self) -> Self:
        vector = Position(0, -1)

        # in raster order, so let's just move them
        for boulder in sorted(self._boulders()):
            next_position = self.last_free_space(boulder, vector)
            if next_position != boulder:
                self.objects[next_position] = self.objects.pop(boulder)

        return self

    def north_load(self) -> int:
        by_row: Dict[int, int] = defaultdict(int)

        for boulder in self._boulders():
            by_row[boulder.y] += 1

        return sum(((self.width - y) * n for y, n in by_row.items()))


def q1(data: Platform) -> int:
    return data.tilt_north().north_load()


def main(filename: str):
    data = Platform.from_file(filename)

    print(f'Q1: load on north: {q1(data)}')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    main(args.input)
