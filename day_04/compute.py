import dataclasses
import re
from argparse import ArgumentParser
from typing import (
    ClassVar,
    List,
    Self,
    Set,
)


@dataclasses.dataclass(frozen=True)
class Card:
    line_re: ClassVar = re.compile(r'Card\s+(\d+): (.*) \| (.*)$')

    id: int
    winning_numbers: Set[int]
    numbers: List[int]

    @property
    def points(self) -> int:
        matches = len(self.winning_numbers & set(self.numbers))
        if matches == 0:
            return 0
        return 1 << (matches - 1)

    @classmethod
    def from_line(cls, line: str) -> Self:
        match = cls.line_re.match(line)
        if match is None:
            raise RuntimeError(f'Bad line: {line}')
        card_id = int(match.group(1))
        winning_numbers = {
            int(n)
            for n in match.group(2).split(' ')
            if n  # handle empty string because numbers are aligned
        }
        numbers = [
            int(n)
            for n in match.group(3).split(' ')
            if n  # handle empty string because numbers are aligned
        ]
        return cls(
            id=card_id,
            winning_numbers=winning_numbers,
            numbers=numbers,
        )

    @classmethod
    def from_file(cls, filename: str) -> List[Self]:
        print(f'Loading {filename}')
        deck = []
        with open(filename, 'r') as fin:
            for line in fin:
                deck.append(cls.from_line(line))
        return deck


def q1(deck: List[Card]) -> int:
    return sum((card.points for card in deck))


def main(filename: str):
    deck = Card.from_file(filename)

    print(f'Q1: {q1(deck)} points')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    main(args.input)
