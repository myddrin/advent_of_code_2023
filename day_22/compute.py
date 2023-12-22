import dataclasses
import re
import time
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
    z: int

    @property
    def on_ground(self) -> bool:
        return self.z == 1

    def __add__(self, other: Self) -> Self:
        return Position(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z,
        )

    def __lt__(self, other: Self) -> bool:
        if self.z == other.z:
            if self.y == other.y:
                return self.x < other.x
            return self.y < other.y
        return self.z < other.z

    def __str__(self):
        return f'{self.x},{self.y},{self.z}'

    def volume(self, other: Self) -> int:
        x = abs(self.x - other.x) + 1
        y = abs(self.y - other.y) + 1
        z = abs(self.z - other.z) + 1
        return x * y * z


@dataclasses.dataclass
class Brick:
    re_format: ClassVar = re.compile(r'(\d+),(\d+),(\d+)~(\d+),(\d+),(\d+)')
    all_bricks: ClassVar[int] = 0

    name: str
    start: Position
    end: Position

    # volume: int = None
    supports: List[str] = dataclasses.field(default_factory=list, compare=False)
    lies_on: List[str] = dataclasses.field(default_factory=list, compare=False)

    @property
    def lowest_z(self):
        return min(self.start.z, self.end.z)

    @property
    def highest_z(self):
        return max(self.start.z, self.end.z)

    @classmethod
    def from_line(cls, line: str, *, name: str = ''):
        if not name:
            name = f'b{cls.all_bricks:04d}'
        cls.all_bricks += 1
        coords = cls.re_format.match(line).groups()
        start = Position(*map(int, coords[:3]))
        end = Position(*map(int, coords[3:]))
        sel_start = min(start, end)
        return cls(
            name=name,
            start=sel_start,
            end=end if sel_start == start else start,
        )

    # def __post_init__(self):
    #     if self.volume is None:
    #         self.volume = self.start.volume(self.end)

    def __lt__(self, other: Self) -> bool:
        return self.lowest_z < other.lowest_z

    def translate(self, position: Position) -> Self:
        self.start += position
        self.end += position
        return self

    def _z_slice(self, z: int) -> Set[Position]:
        return {
            Position(x, y, z)
            for y in range(min(self.start.y, self.end.y), max(self.start.y, self.end.y) + 1)
            for x in range(min(self.start.x, self.end.x), max(self.start.x, self.end.x) + 1)
        }

    def supports_z_slice(self) -> Set[Position]:
        """find the top-most z slice to know what other bricks can lay on"""
        return self._z_slice(self.highest_z + 1)

    def low_z_slice(self) -> Set[Position]:
        return self._z_slice(self.lowest_z)

    def __str__(self):
        return f'{str(self.start)}~{str(self.end)}'


@dataclasses.dataclass
class BrickMap:
    bricks_in_air: List[Brick]
    bricks_on_ground: Dict[str, Brick] = dataclasses.field(default_factory=dict)

    @classmethod
    def from_file(cls, filename: str) -> Self:
        print(f'Loading {filename}')
        bricks = []
        with open(filename, 'r') as fin:
            for line in fin:
                line = line.replace('\n', '')
                bricks.append(Brick.from_line(line))
        print(f'  -> Loaded {len(bricks)} bricks')
        return cls(
            bricks_in_air=bricks,
        )

    def __post_init__(self):
        self.bricks_in_air = sorted(self.bricks_in_air)  # by lowest z

    def fall(self):
        it = 0
        g = Position(0, 0, -1)
        ground_support: Dict[str, Set[Position]] = {}
        for brick in self.bricks_on_ground.values():
            ground_support[brick.name] = brick.supports_z_slice()

        fall_start = time.time()
        while self.bricks_in_air:
            it += 1
            print(f'  {it=} {len(self.bricks_in_air):4d} in air, {len(self.bricks_on_ground):4d} on ground', end='\r')
            next_brick = self.bricks_in_air.pop(0)
            if next_brick.lowest_z == 1:
                # already on the ground
                self.bricks_on_ground[next_brick.name] = next_brick
                ground_support[next_brick.name] = next_brick.supports_z_slice()
            else:
                lowest = next_brick.low_z_slice()
                on_ground = Position(
                    next_brick.start.x,
                    next_brick.start.y,
                    1,
                )

                n = 0
                while on_ground not in lowest:
                    supported_by = []
                    for brick_name, top_z in ground_support.items():
                        if lowest & top_z != set():
                            supported_by.append(brick_name)
                    if supported_by:
                        for k in supported_by:
                            self.bricks_on_ground[k].supports.append(next_brick.name)
                        next_brick.lies_on = supported_by
                        break  # it is supported by bricks
                    # not supported: we move down
                    n += 1
                    lowest = {low_brick + g for low_brick in lowest}

                next_brick.translate(Position(0, 0, n * -1))
                self.bricks_on_ground[next_brick.name] = next_brick
                ground_support[next_brick.name] = next_brick.supports_z_slice()

        fall_end = time.time()
        print(f'All bricks on ground after {it=} in {fall_end - fall_start:.2f}s')

    def destruction_candidates(self) -> List[str]:
        if len(self.bricks_in_air) > 0:
            raise RuntimeError('Should settle first by calling `fall()`')
        candidates = []
        for brick in self.bricks_on_ground.values():
            if len(brick.supports) == 0:
                candidates.append(brick.name)
            else:
                # we support some other brick - are we sharing the load?
                key_brick = False
                for supported_name in brick.supports:
                    if len(self.bricks_on_ground[supported_name].lies_on) == 1:
                        key_brick = True
                        break
                if not key_brick:
                    candidates.append(brick.name)
        return candidates

    def to_file(self, filename: str):
        print(f'Saving to {filename}')
        with open(filename, 'w') as fout:
            for brick in self.bricks_in_air:
                fout.write(f'{str(brick)}\n')
            for brick in self.bricks_on_ground.values():
                fout.write(f'{str(brick)}\n')


def q1(brick_map: BrickMap) -> int:
    return len(brick_map.destruction_candidates())


def main(filename: str):
    brick_map = BrickMap.from_file(filename)
    # settle all bricks
    brick_map.fall()
    brick_map.to_file('output_fall.txt')

    print(f'Q1: first round removable: {q1(brick_map)}')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    main(args.input)
