import dataclasses
from argparse import ArgumentParser
from copy import copy
from typing import (
    ClassVar,
    List,
    Optional,
    Self,
)


@dataclasses.dataclass
class SpringRow:
    Operational: ClassVar[str] = '.'
    Broken: ClassVar[str] = '#'
    Unknown: ClassVar[str] = '?'

    map_data: List[Optional[bool]]
    n_unknown: int = None
    checksum: List[int] = None

    def __post_init__(self):
        if self.n_unknown is None:
            self.n_unknown = sum((1 for spring in self.map_data if spring is None))
        if self.checksum is None:
            self.checksum = self.build_checksum(self.map_data)

    @property
    def width(self) -> int:
        return len(self.map_data)

    @property
    def n_exp_broken(self) -> int:
        return sum(self.checksum)

    @property
    def n_exp_working(self) -> int:
        return self.width - self.n_exp_broken

    @property
    def n_working(self) -> int:
        return sum((1 for spring in self.map_data if spring is True))

    @property
    def n_broken(self) -> int:
        return sum((1 for spring in self.map_data if spring is False))

    def _recursive_brute_choice(
        self, current: List[Optional[bool]], left_working: int, left_broken: int,
    ) -> List[List[bool]]:
        if left_working == 0 and left_broken == 0:
            return [current]

        next_unknown = current.index(None)
        results = []
        if left_working > 0:
            next_one = copy(current)
            next_one[next_unknown] = True
            results.extend(self._recursive_brute_choice(next_one, left_working - 1, left_broken))
        if left_broken > 0:
            next_one = copy(current)
            next_one[next_unknown] = False
            results.extend(self._recursive_brute_choice(next_one, left_working, left_broken - 1))

        return results

    def fill_gaps(self) -> int:
        """Return number of combinations that fill the gaps"""
        if self.n_unknown == 0:
            return 0

        missing_working = self.n_exp_working - self.n_working
        missing_broken = self.n_exp_broken - self.n_broken

        # if self.n_unknown == missing_working or self.n_unknown == missing_broken:
        #     return 1
        count = 0
        failed = 0
        for attempt in self._recursive_brute_choice(self.map_data, missing_working, missing_broken):
            if self.build_checksum(attempt) == self.checksum:
                count += 1
            else:
                failed += 1

        print(f'Generated {count}/{count + failed} combinations')
        return count

    @classmethod
    def build_checksum(cls, map_data: List[bool]) -> List[int]:
        checksum = []
        current_count = 0

        for current in range(len(map_data)):
            if map_data[current] is None:
                raise ValueError(f'Cannot have None when building checksum: map_data[{current}]')
            elif map_data[current] is False:
                current_count += 1
            else:
                if current_count > 0:
                    checksum.append(current_count)
                current_count = 0

        if current_count > 0:
            checksum.append(current_count)
        return checksum

    @classmethod
    def from_line(cls, line: str) -> Self:
        map_data_str, checksum_str = line.split(' ')

        map_data = []
        n_unknown = 0
        for status in map_data_str:
            if status == cls.Operational:
                map_data.append(True)
            elif status == cls.Broken:
                map_data.append(False)
            elif status == cls.Unknown:
                map_data.append(None)
                n_unknown += 1
            else:
                raise ValueError(f'Unexpected {status=}')

        checksum = list(map(int, checksum_str.split(',')))
        return cls(
            map_data=map_data,
            n_unknown=n_unknown,
            checksum=checksum,
        )

    @classmethod
    def from_file(cls, filename: str) -> List[Self]:
        print(f'Loading {filename}')
        data = []
        with open(filename, 'r') as fin:
            for line in fin:
                data.append(cls.from_line(line))
        print(f'  -> loaded {len(data)} entries')
        return data


def q1(data: List[SpringRow]) -> int:
    return sum((spring.fill_gaps() for spring in data))


def main(filename: str):
    data = SpringRow.from_file(filename)

    print(f'Q1: found {q1(data)}')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    main(args.input)
