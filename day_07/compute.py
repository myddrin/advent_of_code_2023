import dataclasses
from argparse import ArgumentParser
from collections import defaultdict
from enum import Enum
from typing import (
    Dict,
    List,
    Self,
)


class Card(Enum):
    Jocker = '*'  # loaded as 'J'
    Two = '2'
    Three = '3'
    Four = '4'
    Five = '5'
    Six = '6'
    Seven = '7'
    Eight = '8'
    Nine = '9'
    Ten = 'T'
    Jack = 'J'
    Queen = 'Q'
    King = 'K'
    Ace = 'A'

    @property
    def score(self) -> int:
        # Jocker is 1, other cards are their original value
        return _score_list.index(self) + 1

    @classmethod
    def from_line(cls, line: str) -> List[Self]:
        return [cls(c) for c in line]


_score_list: [List['Card']] = [c for c in Card]


class Kind(Enum):
    HighCard = 0
    OnePair = 1
    TwoPair = 2
    ThreeOfKind = 3
    FullHouse = 4
    FourOfKind = 5
    FiveOfKind = 6

    def __lt__(self, other: Self) -> bool:
        return self.value < other.value


@dataclasses.dataclass(frozen=True)
class Hand:
    cards: List[Card]
    kind: Kind
    bid: int

    @classmethod
    def _get_kind(cls, cards: List[Card]) -> Kind:
        assert len(cards) == 5
        hand: Dict[Card, int] = defaultdict(int)
        for card in cards:
            hand[card] += 1

        max_same = max(hand.values())
        min_same = min(hand.values())
        if max_same == 5:
            return Kind.FiveOfKind
        elif max_same == 1:
            return Kind.HighCard
        elif max_same == 4:
            return Kind.FourOfKind
        elif max_same == 3:
            # either full house or three of kind
            if min_same == 2:
                return Kind.FullHouse
            return Kind.ThreeOfKind
        elif max_same == 2:
            n_pairs = sum((1 for c in hand.values() if c == 2))
            if n_pairs == 2:
                return Kind.TwoPair
            return Kind.OnePair
        else:
            raise ValueError(f'Unexpected {cards}')

    @classmethod
    def get_kind(cls, original_cards: List[Card]) -> Kind:
        """Brute force to get best kind"""
        best_kind = cls._get_kind(original_cards)
        if Card.Jocker not in original_cards:
            return best_kind
        other_cards = {c for c in original_cards if c != Card.Jocker}
        for card in other_cards:
            alt_cards = [original if original != Card.Jocker else card for original in original_cards]
            if best_kind < (alt_kind := cls._get_kind(alt_cards)):
                best_kind = alt_kind
        return best_kind

    @classmethod
    def from_line(cls, line: str) -> Self:
        cards_str, bid_str = line.split(' ')
        cards = Card.from_line(cards_str)
        kind = cls.get_kind(cards)
        return cls(
            cards,
            kind,
            int(bid_str),
        )

    @classmethod
    def from_file(cls, filename: str, *, j_is_joker: bool = False) -> List[Self]:
        print(f'Loading {filename}')
        hands = []
        with open(filename, 'r') as fin:
            for line in fin:
                line = line.replace('\n', '')
                if not line:
                    continue
                if j_is_joker:
                    line = line.replace(Card.Jack.value, Card.Jocker.value)
                hands.append(cls.from_line(line))
        print(f'  -> {len(hands)} hands loaded')
        return hands

    def __lt__(self, other: Self) -> bool:
        if self.kind != other.kind:
            return self.kind < other.kind
        # same kind - we need to compare card by card
        for card_a, card_b in zip(self.cards, other.cards):
            if card_a != card_b:
                return card_a.score < card_b.score
        return False  # they are equal!


def compute_score(hands: List[Hand]) -> int:
    sorted_hands = sorted(hands)
    return sum((i * hand.bid for i, hand in enumerate(sorted_hands, start=1)))


def main(filename: str):
    print(f'Q1: total score: {compute_score(Hand.from_file(filename))}')
    print(f'Q2: total score: {compute_score(Hand.from_file(filename, j_is_joker=True))}')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    main(args.input)
