import dataclasses
import re
from argparse import ArgumentParser
from typing import (
    ClassVar,
    Dict,
    List,
    Self,
    Set,
)


@dataclasses.dataclass(frozen=True)
class Card:
    line_re: ClassVar = re.compile(r'Card\s+(\d+): (.*) \| (.*)$')

    id: int
    winning_numbers: Set[int]
    numbers: List[int]  # TODO(tr) could be a set

    @property
    def number_matches(self) -> int:
        return len(self.winning_numbers & set(self.numbers))

    @property
    def points(self) -> int:
        matches = self.number_matches
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


@dataclasses.dataclass
class CardDeck:
    cards: List[Card]
    # Dict[card ref -> list of card ref] the winner card -> the card they make you win copies of
    winning_ref: Dict[int, List[int]]

    def play(self) -> int:
        """returns numbers of cards won"""
        # we start with all the cards
        left_to_play = {i: 1 for i, card in enumerate(self.cards)}
        cards_won = 0

        while left_to_play:
            smallest_to_play = sorted(left_to_play.keys())[0]
            number_to_play = left_to_play.pop(smallest_to_play)

            won_this_turn = self.winning_ref[smallest_to_play]

            # cards_won += len(won_this_turn) * number_to_play
            for other_card in won_this_turn:
                left_to_play[other_card] += number_to_play
                cards_won += number_to_play

        return cards_won

    @classmethod
    def from_file(cls, filename: str) -> Self:
        print(f'Loading {filename}')
        deck = []
        winning_ref = {}
        with open(filename, 'r') as fin:
            for line in fin:
                card = Card.from_line(line)
                deck.append(card)
                if matches := card.number_matches:
                    winning_ref[card.id - 1] = list(
                        range(
                            card.id,
                            card.id + matches,
                        ),
                    )
                else:
                    winning_ref[card.id - 1] = []
        return cls(cards=deck, winning_ref=winning_ref)


def q1(deck: CardDeck) -> int:
    return sum((card.points for card in deck.cards))


def q2(deck: CardDeck) -> int:
    return len(deck.cards) + deck.play()


def main(filename: str):
    deck = CardDeck.from_file(filename)

    print(f'Q1: {q1(deck)} points')
    print(f'Q2: {q2(deck)} cards at the end')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    main(args.input)
