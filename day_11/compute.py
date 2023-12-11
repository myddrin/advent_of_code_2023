import dataclasses
from argparse import ArgumentParser
from collections import defaultdict
from typing import (
    Dict,
    Iterable,
    Self,
)


@dataclasses.dataclass(frozen=True)
class Position:
    x: int
    y: int

    def manhattan_distance(self, other: Self) -> int:
        return abs(self.x - other.x) + abs(self.y - other.y)

    def __lt__(self, other: Self):
        # raster order
        if self.y == other.y:
            return self.x < other.x
        return self.y < other.y


@dataclasses.dataclass
class GalaxyMap:
    # Position -> planet id
    universe: Dict[Position, int]
    width: int
    height: int

    @classmethod
    def from_file(cls, filename: str) -> Self:
        print(f'Loading {filename}')
        universe = {}
        height = 0
        width = 0
        with open(filename, 'r') as fin:
            for y, line in enumerate(fin):  # type: int, str
                x = 0
                while x < len(line):
                    x = line.find('#', x)
                    if x < 0:
                        break  # no more galaxies to find
                    universe[Position(x, y)] = len(universe)
                    width = max(width, x + 1)
                    height = max(height, y + 1)
                    x += 1
        return cls(universe, width=width, height=height)

    def _expand_vertically(self):
        vertical_map = defaultdict(list)
        for position in self.universe.keys():
            vertical_map[position.y].append(position)

        for y in range(self.height, -1, -1):
            if y in vertical_map:
                continue  # we have a galaxy on that column
            shifted = False
            for shift_y in range(self.height - 1, y, -1):
                positions = vertical_map.pop(shift_y, [])
                new_positions = []
                for p in positions:
                    galaxy = self.universe.pop(p)
                    new_p = Position(p.x, shift_y + 1)
                    self.universe[new_p] = galaxy
                    new_positions.append(new_p)
                if new_positions:
                    vertical_map[shift_y + 1] = new_positions
                    shifted = True
            if shifted:
                # keep height up to date
                self.height += 1

    def _expand_horizontally(self):
        horizontal_map = defaultdict(list)
        for position in self.universe.keys():
            horizontal_map[position.x].append(position)

        for x in range(self.width, -1, -1):
            if x in horizontal_map:
                continue  # we have a galaxy on that row
            shifted = False
            for shift_x in range(self.width - 1, x, -1):
                positions = horizontal_map.pop(shift_x, [])
                new_positions = []
                for p in positions:
                    galaxy = self.universe.pop(p)
                    new_p = Position(shift_x + 1, p.y)
                    self.universe[new_p] = galaxy
                    new_positions.append(new_p)
                if new_positions:
                    horizontal_map[shift_x + 1] = new_positions
                    shifted = True
            if shifted:
                # keep width up to date
                self.width += 1

    def expand(self) -> Self:
        """find all empty rows and columns and make them count as double"""
        self._expand_vertically()
        self._expand_horizontally()
        return self

    def distances(self) -> Iterable[int]:
        all_positions = sorted(self.universe.keys())
        for current_idx, current in enumerate(all_positions):  # type: int, Position
            for next_idx in range(current_idx + 1, len(all_positions)):
                next_position = all_positions[next_idx]
                yield current.manhattan_distance(next_position)


def q1(galaxy: GalaxyMap) -> int:
    return sum(galaxy.distances())


def main(filename: str):
    galaxy = GalaxyMap.from_file(filename).expand()

    print(f'Q1: sum of distances is {q1(galaxy)}')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    main(args.input)
