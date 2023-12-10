import dataclasses
from argparse import ArgumentParser
from enum import Enum
from typing import (
    Dict,
    List,
    Optional,
    Self,
)


class Direction(Enum):
    North = 1
    South = 2
    East = 3
    West = 4


@dataclasses.dataclass(frozen=True, repr=False)
class Position:
    x: int
    y: int

    def neighbour(self, direction: Direction) -> Self:
        if direction == Direction.North:
            return Position(self.x, self.y - 1)
        elif direction == Direction.South:
            return Position(self.x, self.y + 1)
        elif direction == Direction.East:
            return Position(self.x + 1, self.y)
        elif direction == Direction.West:
            return Position(self.x - 1, self.y)
        raise ValueError(f'Unexpected {direction}')

    def __repr__(self):
        return f'({self.x}, {self.y})'


@dataclasses.dataclass(frozen=True)
class Pipe:
    position: Position
    distance: int
    first: Optional[Direction]
    second: Optional[Direction]

    @property
    def is_start(self) -> bool:
        return self.first is None and self.second is None

    def get_neighbours(self) -> List[Position]:
        if self.is_start:
            return [self.position.neighbour(direction) for direction in Direction]

        return [self.position.neighbour(direction) for direction in (self.first, self.second)]

    @classmethod
    def from_str(cls, position: Position, distance: int, value: str) -> Optional[Self]:
        if value == '|':
            return cls(position, distance, Direction.North, Direction.South)
        elif value == '-':
            return cls(position, distance, Direction.East, Direction.West)
        elif value == 'L':
            return cls(position, distance, Direction.North, Direction.East)
        elif value == 'J':
            return cls(position, distance, Direction.North, Direction.West)
        elif value == '7':
            return cls(position, distance, Direction.South, Direction.West)
        elif value == 'F':
            return cls(position, distance, Direction.South, Direction.East)
        elif value == '.':
            return None
        elif value == 'S':
            return cls(position, 0, None, None)
        raise ValueError(f'Unknown {value}')


@dataclasses.dataclass
class PipeMap:
    raw_data: List[str]
    start: Position

    loop_map: Dict[Position, Pipe] = dataclasses.field(default_factory=dict)

    @classmethod
    def from_file(cls, filename: str) -> Self:
        print(f'Loading {filename}')
        raw_data = []
        start = None
        with open(filename, 'r') as fin:
            for line in fin:
                has_start = line.find('S')
                if has_start >= 0:
                    start = Position(has_start, len(raw_data))

                raw_data.append(line.replace('\n', ''))

        return cls(raw_data, start)

    def __post_init__(self):
        if not self.loop_map:
            self._build_map()

    def _build_from_raw(self, p: Position, distance: int) -> Optional[Pipe]:
        if p.x < 0 or p.x >= len(self.raw_data[0]) or p.y < 0 or p.y >= len(self.raw_data):
            return None

        return Pipe.from_str(p, distance, self.raw_data[p.y][p.x])

    def _build_map(self):
        left_to_check = [self.start]
        self.loop_map[self.start] = Pipe.from_str(self.start, 0, 'S')
        print(f'Building map from start={self.start}')

        it = 0
        while left_to_check:
            it += 1
            current_position = left_to_check.pop(0)
            current = self.loop_map[current_position]
            if it % 1000 == 0:
                print(f'Considering {current_position} ({len(left_to_check)} other positions)')

            for neighbour_position in current.get_neighbours():
                # print(f'  checking neighbour {neighbour_position}')
                if neighbour_position not in self.loop_map:
                    new_pipe = self._build_from_raw(neighbour_position, current.distance + 1)
                    if new_pipe is None:
                        continue  # outside the edge
                    if current_position in new_pipe.get_neighbours():
                        left_to_check.append(neighbour_position)
                        self.loop_map[neighbour_position] = new_pipe
                    #    print(f'    new {neighbour_position} -> {new_pipe}')
                    # else:
                    #     print(f'    {neighbour_position} is not attached')
                # else:
                #     print(f'    known {neighbour_position} skipped')
                # else we know about it already
        print(f'Built map in {it} iterations')


def q1(pipe_map: PipeMap) -> int:
    return max((p.distance for p in pipe_map.loop_map.values()))


def main(filename: str):
    pipe_map = PipeMap.from_file(filename)

    print(f'Q1: furthest: {q1(pipe_map)}')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    main(args.input)
