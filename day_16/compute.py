import dataclasses
from argparse import ArgumentParser
from typing import (
    Dict,
    List,
    Self,
    Set,
    Tuple,
)


@dataclasses.dataclass(frozen=True)
class Position:
    x: int = 1
    y: int = 0

    def __add__(self, other: Self) -> Self:
        return Position(
            self.x + other.x,
            self.y + other.y,
        )

    def __str__(self):
        return f'({self.x}, {self.y})'

    def hit_mirror(self, mirror: str) -> List[Self]:
        if mirror == '|':
            if self.x != 0:
                return [
                    Position(0, -self.x),
                    Position(0, self.x),
                ]
            # if self.y == 0: nothing changes
            return [self]
        elif mirror == '-':
            if self.y != 0:
                return [
                    Position(-self.y, 0),
                    Position(self.y, 0),
                ]
            # if self.x == 0: nothing changes
            return [self]
        elif mirror == '/':
            if self.y == 0:
                return [Position(0, -self.x)]
            else:  # self.x == 0
                return [Position(-self.y, 0)]
        elif mirror == '\\':
            if self.y == 0:
                return [Position(0, self.x)]
            else:  # self.x == 0
                return [Position(self.y, 0)]
        raise ValueError(f'Unexpected mirror {mirror}')


@dataclasses.dataclass
class Map:
    mirror_map: List[str]
    energy_map: Dict[Position, int]

    @property
    def width(self) -> int:
        return len(self.mirror_map[0])

    @property
    def height(self) -> int:
        return len(self.mirror_map)

    def get(self, position: Position) -> str:
        return self.mirror_map[position.y][position.x]

    def within(self, position: Position) -> bool:
        return 0 <= position.x < self.width and 0 <= position.y < self.height

    def _next_beam(self, current: Position, beam: Position):
        left_over: Set[Tuple[Position, Position]] = set()
        visited: Set[Tuple[Position, Position]] = set()

        while (is_within := self.within(current)) or left_over:
            if not is_within:
                # print(f'DBG: going back to {current}, ->{beam}')
                current, beam = left_over.pop()
                # self.energy_to_file('output.txt', current=current, show_mirrors=True)
                continue  # try again if we're within

            if current not in self.energy_map:
                self.energy_map[current] = 0
            self.energy_map[current] += 1

            if (mirror := self.get(current)) != '.':
                visited_entry = (current, beam)
                if visited_entry not in visited:
                    visited.add(visited_entry)
                    beams = beam.hit_mirror(mirror)
                    for b in beams[1:]:
                        left_over.add((current + b, b))
                    # change direction
                    beam = beams[0]
                else:
                    # go outside to use the next beam
                    current = Position(self.width, self.height)
            # move in the same direction
            current += beam

    def trigger_beam(self) -> int:
        self._next_beam(Position(0, 0), Position(1, 0))
        return len(self.energy_map)

    def energy_to_file(self, filename: str, *, current: Position = None, show_mirrors: bool = False):
        print(f'Saving {filename}')
        energised_mirror = {
            '/': '(',
            '\\': ')',
            '-': '=',
            '|': '!',
        }
        with open(filename, 'w') as fout:
            for y in range(self.height):
                line = []
                for x in range(self.width):
                    p = Position(x, y)
                    if p in self.energy_map:
                        c = '#'
                    else:
                        c = '.'
                    if show_mirrors:
                        mirror = self.get(p)
                        if mirror != '.':
                            c = mirror
                        if p in self.energy_map:
                            c = energised_mirror[c]
                    if current is not None and current == p:
                        c = 'O'
                    line.append(c)
                fout.write(''.join(line) + '\n')

    @classmethod
    def from_file(cls, filename: str) -> Self:
        print(f'Loading {filename}')
        mirror_map = []
        with open(filename, 'r') as fin:
            for line in fin:
                line = line.replace('\n', '')
                mirror_map.append(line)

        return cls(mirror_map=mirror_map, energy_map={})


def main(filename: str):
    data = Map.from_file(filename)

    print(f'Q1: energised tiles: {data.trigger_beam()}')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    main(args.input)
