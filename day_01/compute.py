import dataclasses
from argparse import ArgumentParser
from operator import itemgetter
from typing import (
    Iterable,
    List,
    Self,
)


@dataclasses.dataclass(frozen=True)
class Line:
    data: str
    digits: List[int]
    extended_digits: List[int]

    @property
    def calibration_q1(self) -> int:
        return self.digits[0] * 10 + self.digits[-1]

    @property
    def calibration_q2(self) -> int:
        return self.extended_digits[0] * 10 + self.extended_digits[-1]

    @classmethod
    def extract_digits(cls, line: str) -> Iterable[int]:
        ord_0 = ord('0')
        ord_9 = ord('9')
        for c in line:
            if ord_0 <= ord(c) <= ord_9:
                yield int(c)

    @classmethod
    def from_line(cls, line: str) -> Self:
        found_at = []
        for digit_value, alt_digit in enumerate(
            ('one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine'),
            start=1,
        ):
            # handling linking of values, like eightwo should give 8 and 2
            pos = 0
            while pos >= 0:
                pos = line.find(alt_digit, pos)
                if pos >= 0:
                    found_at.append((pos, str(digit_value)))
                    pos += 1  # start at next character - avoid finding the same one in a loop!
        new_data = line
        for pos, to_insert in sorted(found_at, key=itemgetter(0), reverse=True):
            new_data = new_data[:pos] + to_insert + new_data[pos:]

        digits = list(cls.extract_digits(line))
        extended_digits = list(cls.extract_digits(new_data))

        return cls(line, digits, extended_digits)


def load_data(filename: str) -> List[Line]:
    print(f'Loading {filename}')
    data = []
    with open(filename, 'r') as fin:
        for line in fin:
            data.append(Line.from_line(line))
    print(f'Loaded {len(data)} lines')
    return data


def q1(lines: List[Line]) -> int:
    return sum((line.calibration_q1 for line in lines))


def q2(lines: List[Line]) -> int:
    return sum((line.calibration_q2 for line in lines))


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    dat = load_data(args.input)

    print(f'Q1 calibration: {q1(dat)}')
    print(f'Q2 calibration: {q2(dat)}')
