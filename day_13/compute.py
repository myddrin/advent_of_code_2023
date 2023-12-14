import dataclasses
import functools
from argparse import ArgumentParser
from typing import (
    List,
    Self,
)


@dataclasses.dataclass(frozen=True)
class Position:
    x: int
    y: int

    @property
    def score(self) -> int:
        """
        To summarize your pattern notes, add up the number of columns to the left of each
        vertical line of reflection;
        to that, also add 100 multiplied by the number of rows above each horizontal line
        of reflection.
        """
        if self.x is not None:
            return self.x + 1
        if self.y is not None:
            return (self.y + 1) * 100
        return 0

    def __add__(self, other: Self) -> Self:
        return Position(
            self.x + other.x,
            self.y + other.y,
        )

    @classmethod
    def mirror_size(cls, mirror: Self, size: Self) -> Self:
        if mirror.x > 0 and mirror.y > 0:
            raise ValueError('Single direction mirror only')

        return Position(
            x=min((mirror.x + 1, size.x - mirror.x - 1)),
            y=min((mirror.y + 1, size.y - mirror.y - 1)),
        )


@functools.cache
def string_to_binary(value: str) -> int:
    st = 0
    for power, character in enumerate(reversed(value)):
        st += int(character == '#') << power
    return st


@dataclasses.dataclass(frozen=True)
class Pattern:
    data: List[str]

    @property
    def width(self) -> int:
        return len(self.data[0])

    @property
    def height(self) -> int:
        return len(self.data)

    def get_row_numbers(self) -> List[int]:
        results = []
        for y in range(0, self.height):
            results.append(string_to_binary(self.data[y]))
        return results

    def get_col_numbers(self) -> List[int]:
        results = []
        for x in range(0, self.width):
            values = ''
            for y in range(self.height - 1, -1, -1):
                values += self.data[y][x]

            results.append(string_to_binary(values))
        return results

    @classmethod
    def from_file(cls, filename: str) -> List[Self]:
        result = []
        print(f'Loading {filename}')
        with open(filename, 'r') as fin:
            data = []
            for line in fin:
                line = line.replace('\n', '')
                if not line:
                    result.append(
                        cls(
                            data=data,
                        ),
                    )
                    data = []
                else:
                    data.append(line)

            # end of file reached
            if data:
                result.append(
                    cls(
                        data=data,
                    ),
                )
        print(f'  -> loaded {len(result)} patterns')
        return result

    @classmethod
    def _find_symetry(self, values: List[int], start: int) -> bool:
        i = start
        j = start + 1
        match = True
        while i >= 0 and j < len(values) and match:
            match = values[i] == values[j]
            i -= 1
            j += 1
        return match

    def find_mirror(self) -> Position:
        rows = self.get_row_numbers()
        for y in range(0, len(rows) - 1):
            if self._find_symetry(rows, y):
                return Position(None, y)

        cols = self.get_col_numbers()
        for x in range(0, len(cols) - 1):
            if self._find_symetry(cols, x):
                return Position(x, None)

        return None


def q1(data: List[Pattern]) -> int:
    scores = 0
    for i, pat in enumerate(data):
        m = pat.find_mirror()
        print(f'Found {i}: {m}')
        scores += m.score
    return scores


def main(filename: str):
    data = Pattern.from_file(filename)

    print(f'Q1: {q1(data)}')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    main(args.input)
