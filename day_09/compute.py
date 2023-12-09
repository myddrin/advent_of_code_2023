import dataclasses
from argparse import ArgumentParser
from typing import (
    List,
    Self,
)


@dataclasses.dataclass
class DataSeq:
    data: List[int]

    @classmethod
    def _extrapolate(cls, data: List[int]) -> int:
        if all((d == 0 for d in data)):
            return 0

        diff = []
        for i in range(1, len(data)):
            diff.append(data[i] - data[i - 1])
        diff_etra = cls._extrapolate(diff)
        return data[-1] + diff_etra

    @classmethod
    def from_line(cls, line: str) -> Self:
        data = list(map(int, line.split(' ')))
        return cls(data)

    @classmethod
    def from_file(cls, filename: str) -> List[Self]:
        print(f'Loading {filename}')
        data = []
        with open(filename, 'r') as fin:
            for line in fin:
                data.append(cls.from_line(line))
        return data

    def extrapolate(self) -> Self:
        self.data.append(self._extrapolate(self.data))
        return self


def q1(datalog: List[DataSeq]) -> int:
    return sum((d.extrapolate().data[-1] for d in datalog))


def main(filename: str):
    datalog = DataSeq.from_file(filename)

    print(f'Q1: first extrapolation: {q1(datalog)}')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    main(args.input)
