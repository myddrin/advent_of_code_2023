import dataclasses
import re
from argparse import ArgumentParser
from typing import (
    ClassVar,
    List,
    Optional,
    Self,
    Tuple,
)


@dataclasses.dataclass(frozen=True)
class Position:
    x: float
    y: float
    z: float

    def __add__(self, other: Self) -> Self:
        return Position(
            self.x + other.x,
            self.y + other.y,
            self.x + other.z,
        )

    def __str__(self) -> str:
        return f'({self.x:.02f}, {self.y:.02f}, {self.z:.02f})'

    def within(self, zone: Tuple[Self, Self], *, ignore_z: bool = True) -> bool:
        within = [
            zone[0].x <= self.x <= zone[1].x,
            zone[0].y <= self.y <= zone[1].y,
        ]
        if not ignore_z:
            within.append(zone[0].z <= self.z <= zone[1].z)
        return all(within)


@dataclasses.dataclass
class Hailstone:
    re_format: ClassVar = re.compile(r'(-?\d+),\s+(-?\d+),\s+(-?\d+)\s+@\s+(-?\d+),\s+(-?\d+),\s+(-?\d+)')

    start: Position
    velocity: Position  # in nanoseconds

    # as a line: y = m*x + b
    # where m is slope and b the remainder
    slope: float = None
    remainder: float = None

    def __post_init__(self):
        if self.slope is None:
            # compute the trajectory line
            next_point = self.start + self.velocity
            self.slope = (next_point.y - self.start.y) / (next_point.x - self.start.x)
            self.remainder = -self.slope * self.start.x + self.start.y

    def make_point_at(self, x: float, *, z: float = None):
        if z is None:
            z = self.start.z
        return Position(
            x,
            x * self.slope + self.remainder,
            z,
        )

    def is_in_past(self, position: Position) -> bool:
        if self.velocity.x > 0:
            return position.x < self.start.x
        elif self.velocity.x < 0:
            return position.x > self.start.x
        else:
            return position.x != self.start.x

    def intersection(self, other: Self, *, z: float = None) -> Optional[Position]:
        if z is None:
            z = self.start.z

        # a1x+b1y+c1=0 (self) <=> a1x + c1 = -b1y  - in our case b1=-1
        # a2x+b2y+c2=0 (other) <=> a2x + c2 = -b1y  - in our case b1=-1
        # => intersection is thus
        # a1x0+b1y0+c1=0, a2x0+b2y0+c2=0
        # => (x0,y0)=( (b1c2−b2c1)/(a1b2−a2b1),(c1a2−c2a1)/(a1b2−a2b1) )

        divisor = other.slope - self.slope
        if divisor == 0:
            return None  # prevent divide by 0: parallel lines

        cross_x = (self.remainder - other.remainder) / divisor
        cross_y = (self.remainder * other.slope - other.remainder * self.slope) / divisor

        result = Position(cross_x, cross_y, z)
        if self.is_in_past(result) or other.is_in_past(result):
            result = None

        return result

    @classmethod
    def from_file(cls, filename: str) -> List[Self]:
        print(f'Loading {filename}')
        results = []
        with open(filename, 'r') as fin:
            for line in fin:
                results.append(Hailstone.from_line(line))
        print(f'  -> Loaded {len(results)} hailstones')
        return results

    @classmethod
    def from_line(cls, line: str) -> Self:
        groups = cls.re_format.match(line).groups()

        return cls(start=Position(*map(float, groups[:3])), velocity=Position(*map(float, groups[3:])))


def q1(hailstorm: List[Hailstone], zone: Tuple[float, float]):
    zone = (
        Position(zone[0], zone[0], 0),
        Position(zone[1], zone[1], 0),
    )
    intersection = 0
    for i, hailstone in enumerate(hailstorm):
        for other_hailstone in hailstorm[i + 1:]:
            collision = hailstone.intersection(other_hailstone)
            if collision is not None and collision.within(zone):
                intersection += 1
    return intersection


def main(filename: str, zone: Tuple[float, float]):
    hailstorm = Hailstone.from_file(filename)

    print(f'Q1: {q1(hailstorm, zone)} intersection within {zone}')


DEF_ZONE = 200000000000000.0, 400000000000000.0

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    parser.add_argument('--zone', nargs=2, type=float, default=DEF_ZONE, help='Inclusive zone range')
    args = parser.parse_args()

    main(args.input, tuple(map(float, args.zone)))
