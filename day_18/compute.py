import dataclasses
import re
from argparse import ArgumentParser
from enum import Enum
from typing import (
    ClassVar,
    List,
    Optional,
    Self,
)


class Direction(Enum):
    Up = 'U'
    Down = 'D'
    Left = 'L'
    Right = 'R'


@dataclasses.dataclass(frozen=True)
class Position:
    x: int
    y: int

    def __add__(self, other: Self) -> Self:
        return Position(
            self.x + other.x,
            self.y + other.y,
        )

    def direction(self) -> Optional[Direction]:
        if self.x == 0 and self.y > 0:
            return Direction.Up
        elif self.x == 0 and self.y < 0:
            return Direction.Down
        elif self.x < 0 and self.y == 0:
            return Direction.Left
        elif self.x > 0 and self.y == 0:
            return Direction.Right
        return None

    def dot_product(self, other: Self) -> int:
        return self.x * other.y - other.x * self.y

    @classmethod
    def vector_from(cls, direction_str: str, distance: int) -> Self:
        from_direction = {
            Direction.Up: Position(0, distance),
            Direction.Down: Position(0, -distance),
            Direction.Left: Position(-distance, 0),
            Direction.Right: Position(distance, 0),
        }
        return from_direction[Direction(direction_str)]


@dataclasses.dataclass(frozen=True)
class Operation:
    line_re = re.compile(r'([U|D|L|R])\s(\d+)\s\(#([0-9a-f]{6})\)')
    Up: ClassVar[str] = 'U'
    Down: ClassVar[str] = 'D'
    Left: ClassVar[str] = 'L'
    Right: ClassVar[str] = 'R'

    vector: Position
    colour: int

    @classmethod
    def from_line(cls, line: str) -> Self:
        # R 6 (#70c710)
        direction, distance, colour = cls.line_re.match(line).groups()
        return cls(Position.vector_from(direction, int(distance)), int(colour, 16))


@dataclasses.dataclass
class DigPlan:
    dig_plan: List[Operation]
    points: List[Position] = dataclasses.field(default_factory=list)

    def __post_init__(self):
        if self.dig_plan and not self.points:
            self._refresh_points(Position(0, 0))

    def _refresh_points(self, start: Position) -> List[Position]:
        self.points.clear()
        self.points.append(start)
        current = self.points[0]
        for plan in self.dig_plan:
            next_point = current + plan.vector
            self.points.append(next_point)
            current = next_point
        print(f'  -> Built {len(self.points)} points from dig plan')
        return self.points

    def edge_area(self) -> int:
        return sum(
            (
                abs(op.vector.x + op.vector.y)  # only 1 of them is not 0
                for op in self.dig_plan
            ),
        )

    def area(self) -> int:
        area = self.points[-1].dot_product(self.points[0])
        previous = self.points[0]
        for point in self.points[1:]:
            area += previous.dot_product(point)
            previous = point
        return area / 2.0

    @classmethod
    def from_file(cls, filename: str) -> Self:
        print(f'Loading {filename}')
        dig_plan = []
        with open(filename, 'r') as fin:
            for line in fin:
                line = line.replace('\n', '')
                dig_plan.append(Operation.from_line(line))
        print(f'  -> Loading {len(dig_plan)} dig plan operations')
        return cls(dig_plan=dig_plan)


def q1(dig_plan: DigPlan) -> int:
    return dig_plan.area()


def main(filename: str):
    dig_plan = DigPlan.from_file(filename)

    print(f'edge area {dig_plan.edge_area()}')
    print(f'Q1: initial area is {q1(dig_plan)}')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    main(args.input)
