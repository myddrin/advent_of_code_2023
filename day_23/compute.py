import dataclasses
from argparse import ArgumentParser
from typing import (
    ClassVar,
    Dict,
    List,
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
class Path:
    """A path with its neighbours - if iced forced to go the neighbour"""

    position: Position
    neighbours: List[Position] = dataclasses.field(default_factory=list)
    iced: bool = False


@dataclasses.dataclass
class HikingMap:
    neighbour_map: ClassVar = {
        '>': Position(1, 0),
        '<': Position(-1, 0),
        '^': Position(0, -1),
        'v': Position(0, 1),
    }

    path_map: Dict[Position, Path]
    start: Position
    end: Position

    def __post_init__(self):
        # once loaded we have to compute neighbours on non iced slopes
        for pos, path in self.path_map.items():
            if path.iced:
                continue  # done while loading
            for move in self.neighbour_map.values():
                if other := self.path_map.get(pos + move):
                    if other.iced and pos in other.neighbours:
                        continue
                    if other.position not in path.neighbours:
                        path.neighbours.append(other.position)
                    if pos not in other.neighbours and not other.iced:
                        other.neighbours.append(pos)

    @classmethod
    def from_file(cls, filename: str) -> Self:
        print(f'Loading {filename}')
        path_map = {}
        start = None
        end = None
        with open(filename, 'r') as fin:
            for y, line in enumerate(fin):
                line = line.replace('\n', '')
                for x, c in enumerate(line):
                    if c == '#':  # tree
                        continue
                    p = Position(x, y)
                    if start is None:
                        start = p
                    end = p  # always point to the last one
                    neighbours = []
                    # if iced we compute the neighbour
                    if move := cls.neighbour_map.get(c):
                        neighbours.append(p + move)

                    path_map[p] = Path(
                        position=p,
                        neighbours=neighbours,
                        iced=bool(neighbours),
                    )
        print(f'  -> Loaded {len(path_map)} paths')
        return cls(path_map=path_map, start=start, end=end)


@dataclasses.dataclass
class Ant:
    ants: ClassVar[int] = 0

    current: Position
    name: int = 0
    visited: Set[Position] = dataclasses.field(default_factory=set)

    @property
    def steps(self):
        return len(self.visited) - 1

    def __post_init__(self):
        self.__class__.ants += 1
        if not self.name:
            self.name = self.__class__.ants

    def visit(self, hiking_map: HikingMap) -> int:
        """Queen used as an overall cache of all visited places"""
        other_ants = []

        while True:
            path = hiking_map.path_map[self.current]
            next_path = None
            if path.iced and path.neighbours[0] not in self.visited:
                next_path = path.neighbours[0]
            else:
                next_paths = [p for p in path.neighbours if p not in self.visited]
                for p in next_paths[1:]:
                    other_ants.append(
                        Ant(
                            current=p,
                            visited=self.visited | {p},
                        ),
                    )
                    # print(
                    #     f'DBG: created {other_ants[-1].name} from '
                    #     f'{self.name} at {self.current} -> {p}',
                    # )
                if next_paths:
                    next_path = next_paths[0]
                    # if len(next_paths) > 1:
                    #     print(
                    #         f'DBG: {self.name} continuing on {next_path} '
                    #         f'(steps: {len(self.visited)})',
                    #     )

            if next_path is None:
                break

            self.current = next_path
            self.visited.add(self.current)

        # print(f'DBG: finished {self.name} at {len(self.visited)} steps')
        longest_hike = self.steps
        for ant in other_ants:
            longest_hike = max(ant.visit(hiking_map), longest_hike)
        return longest_hike


def q1(hiking_map: HikingMap) -> int:
    walker = Ant(current=hiking_map.start, visited={hiking_map.start})
    return walker.visit(hiking_map)


def main(filename: str):
    data = HikingMap.from_file(filename)

    print(f'Q1: longest hike is {q1(data)}')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    main(args.input)
