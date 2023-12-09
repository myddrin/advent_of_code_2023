import dataclasses
from argparse import ArgumentParser
from typing import (
    Iterable,
    List,
    Self,
    Tuple,
)


@dataclasses.dataclass
class DataSeq:
    data: List[int]

    @classmethod
    def _extrapolate(cls, data: List[int]) -> Tuple[int, int]:
        """Return a new value for the beginning and the end"""
        if all((d == 0 for d in data)):
            return 0, 0

        diff = []
        for i in range(1, len(data)):
            diff.append(data[i] - data[i - 1])
        diff_etra_st, diff_extra_ed = cls._extrapolate(diff)
        return data[0] - diff_etra_st, data[-1] + diff_extra_ed

    @classmethod
    def from_line(cls, line: str) -> Self:
        data = list(map(int, line.split(' ')))
        return cls(data)

    @classmethod
    def from_file(cls, filename: str) -> Iterable[Self]:
        print(f'Loading {filename}')
        with open(filename, 'r') as fin:
            for line in fin:
                yield cls.from_line(line)

    def extrapolate(self) -> Self:
        new_st, new_ed = self._extrapolate(self.data)
        self.data.insert(0, new_st)
        self.data.append(new_ed)
        return self


def q1(extrapolated: List[DataSeq]) -> int:
    return sum((d.data[-1] for d in extrapolated))


def q2(extrapolated: List[DataSeq]) -> int:
    # assumes q1 ran extrapolate already
    return sum((d.data[0] for d in extrapolated))


def main(filename: str):
    extrapolated_data = [d.extrapolate() for d in DataSeq.from_file(filename)]

    print(f'Q1: last entry extrapolation sum: {q1(extrapolated_data)}')
    print(f'Q2: first entry extrapolation sum: {q2(extrapolated_data)}')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    main(args.input)
