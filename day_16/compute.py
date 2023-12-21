import dataclasses
import time
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


BeamData = Tuple[Position, Position]  # position + beam


@dataclasses.dataclass
class Map:
    mirror_map: List[str]

    visited: Set[BeamData] = dataclasses.field(default_factory=set)
    mirror_cache: Dict[BeamData, Set[Position]] = dataclasses.field(default_factory=dict)

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

    def _visited_from(self, current: Position, beam: Position) -> Set[Position]:
        # with the cache - but does not work yet
        energy_map: Set[Position] = set()

        while is_within := self.within(current):
            if not is_within:
                break

            energy_map.add(current)
            print(f'\rchecking {current=} {beam=}...', end='')

            if (mirror := self.get(current)) != '.':
                visited_entry = (current, beam)
                if visited_entry in self.visited:
                    break

                self.visited.add(visited_entry)

                if visited_entry in self.mirror_cache:
                    print(f'!!! cache hit {visited_entry} !!!')
                    energy_map.update(self.mirror_cache[visited_entry])
                else:
                    beams = beam.hit_mirror(mirror)
                    other_energy_map = set()
                    for b in beams:
                        # not a full recursion - so the cache will be less efficient
                        other_energy_map.update(
                            self._visited_from(
                                current + b,
                                b,
                            ),
                        )
                    self.mirror_cache[visited_entry] = other_energy_map
                    print(f'!!! set cache {visited_entry} !!!')
                    energy_map.update(other_energy_map)

                break
            else:
                current += beam

        return energy_map

    def _next_beam(self, current: Position, beam: Position) -> Set[Position]:
        left_over: Set[Tuple[Position, Position]] = set()
        energy_map: Set[Position] = set()

        while (is_within := self.within(current)) or left_over:
            if not is_within:
                current, beam = left_over.pop()
                # self.energy_to_file('output.txt', current=current, show_mirrors=True)
                continue  # try again if we're within

            energy_map.add(current)

            if (mirror := self.get(current)) != '.':
                visited_entry = (current, beam)
                if visited_entry not in self.visited:
                    self.visited.add(visited_entry)
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

        return energy_map

    def trigger_beam(self, start: Position = Position(0, 0), beam: Position = Position(1, 0)) -> int:
        self.visited.clear()
        energy_map = self._next_beam(start, beam)
        # energy_map = self._visited_from(start, beam)
        return len(energy_map)

    def best_beam(self) -> int:
        beam_start = set()
        best_beam = 0
        for y in range(1, self.height - 1):
            beam_start.update(
                (
                    (Position(0, y), Position(1, 0)),
                    (Position(self.width - 1, y), Position(-1, 0)),
                ),
            )
        for x in range(1, self.width - 1):
            beam_start.update(((Position(x, 0), Position(0, 1)), (Position(x, self.height - 1), Position(0, -1))))
        beam_start.update(
            (
                (Position(0, 0), Position(1, 0)),
                (Position(0, 0), Position(0, 1)),
                (Position(self.width - 1, 0), Position(-1, 0)),
                (Position(self.width - 1, 0), Position(0, -1)),
                (Position(self.width - 1, self.height - 1), Position(-1, 0)),
                (Position(self.width - 1, self.height - 1), Position(0, -1)),
                (Position(0, self.height - 1), Position(1, 0)),
                (Position(0, self.height - 1), Position(0, -1)),
            ),
        )
        start_time = time.time()
        print(f'Looking for {len(beam_start)} combinations')
        for start_position, beam in beam_start:
            energised = self.trigger_beam(start_position, beam)
            if energised > best_beam:
                print(f'  -> Best beam {start_position=} {beam=} -> {energised}')
                best_beam = energised

        print(f'Found best beam in {time.time() - start_time:.2f}s')
        return best_beam

    def energy_to_file(
        self, filename: str, energy_map: Set[Position], *, current: Position = None, show_mirrors: bool = False,
    ):
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
                    if p in energy_map:
                        c = '#'
                    else:
                        c = '.'
                    if show_mirrors:
                        mirror = self.get(p)
                        if mirror != '.':
                            c = mirror
                        if p in energy_map:
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

        return cls(mirror_map=mirror_map)


def main(filename: str):
    data = Map.from_file(filename)

    print(f'Q1: energised tiles: {data.trigger_beam()}')
    print(f'Q2: best energised tiles: {data.best_beam()}')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    main(args.input)
