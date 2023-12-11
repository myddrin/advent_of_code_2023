import dataclasses
from argparse import ArgumentParser
from enum import Enum
from typing import (
    Dict,
    List,
    Optional,
    Self,
    Set,
)


class Direction(Enum):
    North = 1
    South = 2
    East = 3
    West = 4

    @property
    def is_vertical(self) -> bool:
        return self in {self.North, self.South}

    @property
    def is_horizontal(self) -> bool:
        return self in {self.East, self.West}

    @property
    def opposite_direction(self) -> Self:
        if self == self.North:
            return self.South
        elif self == self.South:
            return self.North
        elif self == self.East:
            return self.West
        elif self == self.West:
            return self.East
        raise ValueError(f'Unexpected {self}')


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

    @property
    def is_vertical(self) -> bool:
        return self.first.is_vertical or self.second.is_vertical

    @property
    def is_horizontal(self) -> bool:
        return self.first.is_horizontal or self.second.is_horizontal

    def has(self, a: Direction, b: Direction) -> bool:
        return (self.first == a and self.second == b) or (self.first == b and self.second == a)

    def to_str(self, fancy: bool = True) -> str:
        if self.has(Direction.North, Direction.South):
            return '║' if fancy else '|'
        elif self.has(Direction.East, Direction.West):
            return '═' if fancy else '-'
        elif self.has(Direction.North, Direction.East):
            return '╚' if fancy else 'L'
        elif self.has(Direction.North, Direction.West):
            return '╝' if fancy else 'J'
        elif self.has(Direction.South, Direction.West):
            return '╗' if fancy else '7'
        elif self.has(Direction.South, Direction.East):
            return '╔' if fancy else 'F'
        elif self.first is None and self.second is None:
            return '╬' if fancy else 'S'
        raise ValueError(f'Unexpected {self.first} {self.second}')

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

    @property
    def width(self) -> int:
        return len(self.raw_data[0])

    @property
    def height(self) -> int:
        return len(self.raw_data)

    def _travel(self, target: Position, direction: Direction) -> int:
        if direction == Direction.North:
            cross = {Direction.East, Direction.West}
            vector = Position(0, -1)
            current = Position(target.x, self.height - 1)
        elif direction == Direction.South:
            cross = {Direction.East, Direction.West}
            vector = Position(0, 1)
            current = Position(target.x, 0)
        elif direction == Direction.East:
            cross = {Direction.North, Direction.South}
            vector = Position(1, 0)
            current = Position(0, target.y)
        elif direction == Direction.West:
            cross = {Direction.North, Direction.South}
            vector = Position(-1, 0)
            current = Position(self.width - 1, target.y)
        else:
            raise ValueError(f'Unexpected {direction}')

        crossed = 0
        while current != target:
            pipe = self.loop_map.get(current)
            if pipe and (pipe.first in cross or pipe.second in cross):
                crossed += 1
            current = Position(current.x + vector.x, current.y + vector.y)

        return crossed

    def find_area_fail(self) -> Set[Position]:
        checked: Dict[Position, bool] = {}
        for y in range(self.height):
            for x in range(self.width):
                current = Position(x, y)
                if current in self.loop_map:
                    continue

                # maybe to make it faster check neighbours?
                checked[current] = all((self._travel(current, d) % 2 == 1 for d in Direction))

        return {k for k, v in checked.items() if v}

    def has_vertical_neighbour(self, pipe: Pipe) -> bool:
        interesting_neighbours = [
            pipe.position.neighbour(Direction.West),
            pipe.position.neighbour(Direction.East),
        ]
        for neighbour in interesting_neighbours:
            other = self.loop_map.get(neighbour)
            if other is not None and other.is_vertical:
                return True
        return False

    def has_horizontal_neighbour(self, pipe: Pipe) -> bool:
        interesting_neighbours = [
            pipe.position.neighbour(Direction.North),
            pipe.position.neighbour(Direction.South),
        ]
        for neighbour in interesting_neighbours:
            other = self.loop_map.get(neighbour)
            if other is not None and other.first.is_horizontal:
                return True
        return False

    def _squeeze(self, current: Position, direction: Direction, neighbour: Pipe) -> Optional[Position]:
        vector = Position(neighbour.position.x - current.x, neighbour.position.y - current.y)
        if direction.is_vertical:
            if neighbour.first.is_horizontal:
                stop_at = neighbour.first.opposite_direction
            else:
                stop_at = neighbour.second.opposite_direction
        else:
            if neighbour.first.is_vertical:
                stop_at = neighbour.first.opposite_direction
            else:
                stop_at = neighbour.second.opposite_direction

        while stop_at not in (neighbour.first, neighbour.second):
            current = Position(neighbour.position.x + vector.x, neighbour.position.y + vector.y)
            if current.x < 0 or current.x >= self.width or current.y < 0 or current.y >= self.height:
                break  # end of map without finding a tile
            neighbour = self.loop_map.get(current)
            if neighbour is None:
                # we hit an empty space and were not stopped
                return current
        # we were stopped or reached the end of the map
        return None

    def find_area(self) -> Set[Position]:  # noqa
        left_to_search: Set[Position] = set()
        found_outside: Set[Position] = set()
        ignored: Set[Position] = {self.start}

        for y in range(self.height):
            position = Position(0, y)
            if position in self.loop_map:
                ignored.add(position)
            else:
                left_to_search.add(position)

            position = Position(self.width - 1, y)
            if position in self.loop_map:
                ignored.add(position)
            else:
                left_to_search.add(position)
        for x in range(self.width):
            position = Position(x, 0)
            if position in self.loop_map:
                ignored.add(position)
            else:
                left_to_search.add(position)

            position = Position(x, self.height - 1)
            if position in self.loop_map:
                ignored.add(position)
            else:
                left_to_search.add(position)

        it = 0
        while left_to_search:
            it += 1
            current = left_to_search.pop()
            # if it % 10000 == 1:
            print(f'Checking {current} {it}/{self.width * self.height}')

            found_outside.add(current)
            for d in Direction:
                neighbour = current.neighbour(d)
                next_pipe = self.loop_map.get(neighbour)
                if neighbour.x < 0 or neighbour.x >= self.width or neighbour.y < 0 or neighbour.y >= self.height:
                    continue
                elif neighbour in found_outside or neighbour in ignored:
                    continue  # we've handled it before
                elif next_pipe is not None:
                    if d.is_vertical and (next_pipe.first == Direction.East and next_pipe.second == Direction.West):
                        ignored.add(neighbour)
                        continue  # we're looking up or down and the neighbour is a straight line
                    elif d.is_horizontal and (next_pipe.first == Direction.East and next_pipe.second == Direction.West):
                        ignored.add(neighbour)
                        continue  # we're looking left or right and the neighbour is a straight line
                    else:
                        # we have to check the neighbour opposite the pipe to know if we could
                        # "squeeze past" it
                        next_position = self._squeeze(current, d, next_pipe)
                        if (
                            next_position is not None
                            and next_position not in found_outside
                            and next_position not in ignored
                        ):
                            left_to_search.add(next_position)
                else:
                    # not a know location: check it next
                    left_to_search.add(neighbour)

        inside = set()
        for y in range(self.height):
            for x in range(self.width):
                current = Position(x, y)
                if current in self.loop_map or current in found_outside:
                    continue
                inside.add(current)
        return inside

    def to_file(self, filename: str, found_inside: Set[Position]):
        print(f'Saving to {filename}')
        with open(filename, 'w') as fout:
            for y in range(self.height):
                line = []
                for x in range(self.width):
                    position = Position(x, y)
                    if position in self.loop_map:
                        c = self.loop_map[position].to_str(fancy=True)
                    elif position in found_inside:
                        c = 'I'
                    else:
                        c = '.'
                    line.append(c)
                fout.write(''.join(line) + '\n')


def q1(pipe_map: PipeMap) -> int:
    return max((p.distance for p in pipe_map.loop_map.values()))


def q2(pipe_map: PipeMap) -> int:
    found = pipe_map.find_area()
    pipe_map.to_file('output.txt', found)
    return len(found)


def main(filename: str):
    pipe_map = PipeMap.from_file(filename)

    print(f'Q1: furthest: {q1(pipe_map)}')
    print(f'Q2: enclosed: {q2(pipe_map)}')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    main(args.input)
