import os

import pytest

from day_07.compute import (
    Card,
    Hand,
    Kind,
    q1,
)


@pytest.fixture(scope='session')
def small_ex_txt():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'small_ex.txt',
    )


@pytest.fixture(scope='session')
def input_txt():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'input.txt',
    )


class TestCard:
    @pytest.mark.parametrize(
        'card_str, score',
        [(str(i), i) for i in range(2, 10)]
        + [
            ('T', 10),
            ('J', 11),
            ('Q', 12),
            ('K', 13),
            ('A', 14),
        ],
    )
    def test_score(self, card_str, score):
        assert Card(card_str).score == score


class TestHand:
    @pytest.mark.parametrize(
        'cards_str, kind',
        (
            ('AAAAA', Kind.FiveOfKind),
            ('AA8AA', Kind.FourOfKind),
            ('23332', Kind.FullHouse),
            ('TTT98', Kind.ThreeOfKind),
            ('23432', Kind.TwoPair),
            ('A23A4', Kind.OnePair),
            ('23456', Kind.HighCard),
        ),
    )
    def test_get_kind(self, cards_str: str, kind: Kind):
        cards = Card.from_line(cards_str)
        assert Hand.get_kind(cards) == kind


class TestQ1:
    def test_small_ex(self, small_ex_txt):
        assert q1(Hand.from_file(small_ex_txt)) == 6440

    def test_input_txt(self, input_txt):
        assert q1(Hand.from_file(input_txt)) == 251927063
