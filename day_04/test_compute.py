import os

import pytest

from day_04.compute import (
    Card,
    CardDeck,
    q1,
    q2,
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
        'line, expected',
        (
            (
                'Card 3:  1 21 53 59 44 | 69 82 63 72 16 21 14  1',
                Card(3, {1, 21, 53, 59, 44}, [69, 82, 63, 72, 16, 21, 14, 1]),
            ),
            (
                'Card 126: 31 18 13 56 72 | 74 77 10 23 35 67 36 11',
                Card(
                    126,
                    {
                        31,
                        18,
                        13,
                        56,
                        72,
                    },
                    [74, 77, 10, 23, 35, 67, 36, 11],
                ),
            ),
        ),
    )
    def test_from_line(self, line, expected):
        assert Card.from_line(line) == expected


class TestCardDeck:
    def test_from_file(self, small_ex_txt):
        deck = CardDeck.from_file(small_ex_txt)
        assert len(deck.winning_ref) == len(deck.cards) == 6
        assert deck.winning_ref[0] == [1, 2, 3, 4]  # id: 2, 3, 4, 5
        assert deck.winning_ref[1] == [2, 3]  # id: 3, 4
        assert deck.winning_ref[2] == [3, 4]  # id 4, 5
        # ...


class TestQ1:
    def test_small_ex(self, small_ex_txt):
        deck = CardDeck.from_file(small_ex_txt)
        assert q1(deck) == 13

    def test_input(self, input_txt):
        deck = CardDeck.from_file(input_txt)
        assert q1(deck) == 18619


class TestQ2:
    def test_small_ex(self, small_ex_txt):
        deck = CardDeck.from_file(small_ex_txt)
        assert deck.play() == (30 - len(deck.cards))
        assert q2(deck) == 30

    def test_input(self, input_txt):
        deck = CardDeck.from_file(input_txt)
        assert q2(deck) == 8063216
