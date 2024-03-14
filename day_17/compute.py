import dataclasses
import time
from argparse import ArgumentParser
from typing import (
    ClassVar,
    Dict,
    Iterable,
    List,
    Optional,
    Self,
    Tuple,
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

    def __sub__(self, other: Self) -> Self:
        return Position(
            self.x - other.x,
            self.y - other.y,
        )

    def __repr__(self) -> str:
        return f'({self.x}, {self.y})'


@dataclasses.dataclass
class HeatMap:
    heat_loss: List[List[int]]
    # pos -> total heat at visit
    visited: Dict[Position, 'Ant'] = dataclasses.field(default_factory=dict)

    @property
    def width(self) -> int:
        return len(self.heat_loss[0])

    @property
    def height(self) -> int:
        return len(self.heat_loss)

    def heat_loss_at_end(self) -> Optional[int]:
        end_pos = Position(self.width - 1, self.height - 1)
        if (ant := self.visited.get(end_pos)) is not None:
            return ant.total_heat_loss
        return None

    @classmethod
    def from_file(cls, filename: str) -> Self:
        print(f'Loading {filename}')
        with open(filename, 'r') as fin:
            data = []
            for line in fin:
                line = line.replace('\n', '')
                data.append([int(c) for c in line])
        return cls(heat_loss=data)

    def get_heat_loss(self, position: Position) -> int:
        return self.heat_loss[position.y][position.x]

    def is_visited(self, position: Position) -> bool:
        return position in self.visited

    def visit_map(self):
        self.visited.clear()
        ants = [Ant(Position(0, 0), travelled=[Position(0, 0)])]

        self.visited[Position(0, 0)] = ants[0]
        total_to_visit = self.width * self.height
        starting = time.time()
        it = 1
        while ants:
            next_ants = []
            for i, ant in enumerate(ants, start=1):
                for new_ant in ant.next_moves(self):
                    if new_ant.current not in self.visited or new_ant < self.visited[new_ant.current]:
                        self.visited[new_ant.current] = new_ant
                        # next_ants.append(new_ant)
                    # indent in IF to make it faster, but it finds the wrong answer for small_ex
                    # this finds ALL solutions but is super slow
                    next_ants.append(new_ant)
                if i % 1000 == 0:
                    print(
                        f'\r  {it=} {i}/{len(ants)} we have {len(next_ants)} new ants '
                        f'(visited {len(self.visited)}/{total_to_visit})  ',
                        end='',
                    )
            print(
                f'\r  {it=} ({len(ants)}) we have {len(next_ants)} new ants '
                f'(visited {len(self.visited)}/{total_to_visit})  ',
                end='',
            )
            ants = next_ants
            it += 1
        ending = time.time() - starting
        print(f'\nVisited {len(self.visited)}/{total_to_visit} in {ending:0.2f}s')

        assert len(self.visited) == total_to_visit

    def to_file(self, filename: str):
        print(f'Saving {filename}')
        best_ant = self.visited[Position(self.width - 1, self.height - 1)]

        with open(filename, 'w') as fout:
            for y in range(self.height):
                line = []
                for x in range(self.width):
                    p = Position(x, y)
                    if p == Position(0, 0):
                        c = 'S'
                    elif p in best_ant.travelled:
                        i = best_ant.travelled.index(p)
                        d = p - best_ant.travelled[i - 1]
                        if d == Position(1, 0):
                            c = '>'
                        elif d == Position(-1, 0):
                            c = '<'
                        elif d == Position(0, 1):
                            c = 'v'
                        else:
                            c = '^'
                    else:
                        c = str(self.get_heat_loss(p))
                    line.append(c)
                fout.write(''.join(line) + '\n')


@dataclasses.dataclass
class Ant:
    moves: ClassVar = [
        Position(1, 0),
        Position(0, 1),
        Position(-1, 0),
        Position(0, -1),
    ]

    current: Position
    total_heat_loss: int = 0
    travelled: List[Position] = dataclasses.field(default_factory=list)

    def __hash__(self):
        return hash(self.current)

    def __lt__(self, other: Self) -> bool:
        _, last_con = self.last_consecutive()
        _, other_last_con = other.last_consecutive()
        if self.total_heat_loss == other.total_heat_loss:
            return last_con < other_last_con
        return self.total_heat_loss < other.total_heat_loss

    def last_consecutive(self) -> Tuple[Position, int]:
        consecutive_move = 0
        last = None
        for pair in reversed(list(zip(self.travelled[-4:-1], self.travelled[-3:]))):
            vector = pair[1] - pair[0]
            if last is not None and last == vector:
                consecutive_move += 1
            else:
                consecutive_move = 1
            last = vector
        return last, consecutive_move

    def next_moves(self, heat_map: HeatMap) -> Iterable[Self]:
        last, consecutive_move = self.last_consecutive()

        for m in self.moves:
            if consecutive_move >= 3 and last == m:
                continue  # cannot continue this way
            next_move = self.current + m
            within_map = 0 <= next_move.x < heat_map.width and 0 <= next_move.y < heat_map.height
            if within_map and next_move not in self.travelled:
                yield Ant(
                    total_heat_loss=self.total_heat_loss + heat_map.get_heat_loss(next_move),
                    current=next_move,
                    travelled=self.travelled + [next_move],
                )


def main(filename: str):
    heatmap = HeatMap.from_file(filename)
    heatmap.visit_map()
    heatmap.to_file('output.txt')

    print(f'Q1: smallest heat loss: {heatmap.heat_loss_at_end()}')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    main(args.input)
