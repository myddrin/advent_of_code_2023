import dataclasses
from argparse import ArgumentParser
from typing import (
    ClassVar,
    Dict,
    Iterable,
    Self,
    Set,
)


@dataclasses.dataclass(frozen=True)
class Position:
    x: int
    y: int

    def __add__(self, other: Self) -> Self:
        return Position(
            self.x + other.x,
            self.y + other.y,
        )


@dataclasses.dataclass
class Garden:
    rocks: Set[Position]
    start: Position
    width: int
    height: int

    reachable: Dict[Position, int] = dataclasses.field(default_factory=dict)

    @classmethod
    def from_file(cls, filename: str) -> Self:
        print(f'Loading {filename}')
        rocks = set()
        start = None
        width = 0
        with open(filename, 'r') as fin:
            y = 0
            for y, line in enumerate(fin):
                line = line.replace('\n', '')
                if width == 0:
                    width = len(line)
                for x, c in enumerate(line):
                    if c == '#':
                        rocks.add(Position(x, y))
                    elif c == 'S':
                        start = Position(x, y)
                    # if '.' then it's a garden
            height = y + 1
        return cls(rocks, start, width, height)

    def visit(self, n_steps: int = 64) -> int:
        self.reachable.clear()

        ants = [Ant(self.start, self)]
        last_next_ant = len(ants)

        for s in range(0, n_steps):
            next_ants = set()

            for ant in ants:
                if ant.position not in self.reachable:
                    self.reachable[ant.position] = s
                next_ants.update(ant.next_moves())

            last_next_ant = len(next_ants)
            ants.clear()
            for p in next_ants:
                ants.append(Ant(p, self))

            if s % 10 == 0:
                print(
                    f'  -> after {s} steps {len(self.reachable)} tiles are reachable (current ants: {len(ants)}, {last_next_ant=})',
                )

        return last_next_ant

    def to_file(self, filename: str):
        print(f'Saving to {filename}')
        with open(filename, 'w') as fout:
            for y in range(self.height):
                line = []
                for x in range(self.width):
                    position = Position(x, y)
                    if position in self.rocks:
                        c = '#'
                    elif position in self.reachable:
                        c = str(self.reachable[position])
                    else:
                        c = '.'
                    line.append(c)
                fout.write(''.join(line) + '\n')


@dataclasses.dataclass
class Ant:
    moves: ClassVar = (
        Position(1, 0),
        Position(0, 1),
        Position(-1, 0),
        Position(0, -1),
    )

    position: Position
    garden: Garden

    def next_moves(self) -> Iterable[Position]:
        for m in self.moves:
            next_p = self.position + m
            if not (0 <= next_p.x < self.garden.width and 0 <= next_p.y < self.garden.height):
                continue  # outside

            if next_p in self.garden.rocks:
                continue  # visited already

            yield next_p


def main(filename: str, n_steps: int):
    garden = Garden.from_file(filename)

    print(f'Q1: {garden.visit(n_steps)} tiles are reachable with {n_steps} steps')
    garden.to_file('output.txt')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    parser.add_argument('--n-steps', type=int, default=64)
    args = parser.parse_args()

    main(args.input, args.n_steps)
