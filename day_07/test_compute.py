import os

import pytest

from day_07.compute import (
    Card,
    Hand,
    Kind,
    compute_score,
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
    original_kinds = (
        ('AAAAA', Kind.FiveOfKind),
        ('AA8AA', Kind.FourOfKind),
        ('23332', Kind.FullHouse),
        ('TTT98', Kind.ThreeOfKind),
        ('23432', Kind.TwoPair),
        ('A23A4', Kind.OnePair),
        ('23456', Kind.HighCard),
    )

    @pytest.mark.parametrize('cards_str, kind', original_kinds)
    def test_private_get_kind(self, cards_str: str, kind: Kind):
        cards = Card.from_line(cards_str)
        assert Hand._get_kind(cards) == kind

    @pytest.mark.parametrize(
        'cards_str, kind',
        original_kinds
        + (
            ('Q**Q2', Kind.FourOfKind),
            ('T55*5', Kind.FourOfKind),
            ('QQQ*A', Kind.FourOfKind),
            ('T55*5', Kind.FourOfKind),
        ),
    )
    def test_get_kind(self, cards_str: str, kind: Kind):
        cards = Card.from_line(cards_str)
        assert Hand.get_kind(cards)

    @pytest.mark.parametrize(
        'hand_a_str, hand_b_str, exp',
        (
            ('JKKK2 123', 'QQQQ2 123', True),  # kind a < kind b
            ('JJJJ2 123', 'QQQQ2 123', True),  # J < Q
            ('JJJJ3 123', 'JJJJ2 123', False),  # last card 3 > 2
            ('*JJJ2 123', 'QQQQ2 123', True),  # * < Q
            ('QQQ*2 123', 'QQQQ2 123', True),  # * < Q
        ),
    )
    def test_compare(self, hand_a_str, hand_b_str, exp):
        hand_a = Hand.from_line(hand_a_str)
        hand_b = Hand.from_line(hand_b_str)
        assert (hand_a < hand_b) is exp


class TestQ1:
    def test_small_ex(self, small_ex_txt):
        assert compute_score(Hand.from_file(small_ex_txt)) == 6440

    def test_input_txt(self, input_txt):
        assert compute_score(Hand.from_file(input_txt)) == 251927063


class TestQ2:
    def test_small_ex(self, small_ex_txt):
        assert compute_score(Hand.from_file(small_ex_txt, j_is_joker=True)) == 5905

    def test_input_txt(self, input_txt):
        assert compute_score(Hand.from_file(input_txt, j_is_joker=True)) == 255632664
