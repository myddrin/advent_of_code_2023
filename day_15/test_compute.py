import os

import pytest

from day_15.compute import (
    InitSeq,
    hash_step,
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


class TestHashStep:
    @pytest.mark.parametrize(
        'step, hash_v',
        (
            ('', 0),
            ('HASH', 52),
        ),
    )
    def test_hash_step(self, step, hash_v):
        assert hash_step(step) == hash_v

    def test_load_input(self, input_txt):
        data = InitSeq.from_file(input_txt)
        assert len(data.steps) == 4000


class TestQ1:
    def test_small_ex(self, small_ex_txt):
        assert InitSeq.from_file(small_ex_txt).checksum() == 1320

    def test_input(self, input_txt):
        assert InitSeq.from_file(input_txt).checksum() == 510801


class TestQ2:
    def test_small_ex(self, small_ex_txt):
        assert q2(InitSeq.from_file(small_ex_txt)) == 145

    def test_input(self, input_txt):
        assert q2(InitSeq.from_file(input_txt)) == 212763
