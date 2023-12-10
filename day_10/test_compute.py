import os

import pytest

from day_10.compute import (
    Direction,
    Pipe,
    PipeMap,
    Position,
    q1,
    q2,
)


@pytest.fixture(scope='session')
def small_ex1_txt():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'small_ex1.txt',
    )


@pytest.fixture(scope='session')
def small_ex2_txt():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'small_ex2.txt',
    )


@pytest.fixture(scope='session')
def small_ex3_txt():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'small_ex3.txt',
    )


@pytest.fixture(scope='session')
def small_ex4_txt():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'small_ex4.txt',
    )


@pytest.fixture(scope='session')
def small_ex5_txt():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'small_ex5.txt',
    )


@pytest.fixture(scope='session')
def input_txt():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'input.txt',
    )


class TestPipeMap:
    def test_load_small_ex1(self, small_ex1_txt):
        data = PipeMap.from_file(small_ex1_txt)
        assert data.start == Position(1, 1)
        assert data.loop_map == {
            pipe.position: pipe
            for pipe in (
                Pipe(Position(1, 1), 0, None, None),
                Pipe(Position(2, 1), 1, Direction.East, Direction.West),
                Pipe(Position(3, 1), 2, Direction.South, Direction.West),
                Pipe(Position(3, 2), 3, Direction.North, Direction.South),
                Pipe(Position(3, 3), 4, Direction.North, Direction.West),
                Pipe(Position(2, 3), 3, Direction.East, Direction.West),
                Pipe(Position(1, 3), 2, Direction.North, Direction.East),
                Pipe(Position(1, 2), 1, Direction.North, Direction.South),
            )
        }

    def test_load_small_ex2(self, small_ex2_txt):
        data = PipeMap.from_file(small_ex2_txt)
        assert data.start == Position(0, 2)
        assert data.loop_map == {
            pipe.position: pipe
            for pipe in (
                Pipe(Position(0, 2), 0, None, None),
                Pipe(Position(1, 2), 1, Direction.North, Direction.West),
                Pipe(Position(1, 1), 2, Direction.South, Direction.East),
                Pipe(Position(2, 1), 3, Direction.North, Direction.West),
                Pipe(Position(2, 0), 4, Direction.South, Direction.East),
                Pipe(Position(3, 0), 5, Direction.South, Direction.West),
                Pipe(Position(3, 1), 6, Direction.North, Direction.South),
                Pipe(Position(3, 2), 7, Direction.North, Direction.East),
                Pipe(Position(4, 2), 8, Direction.South, Direction.West),
                Pipe(Position(4, 3), 7, Direction.North, Direction.West),
                Pipe(Position(3, 3), 6, Direction.East, Direction.West),
                Pipe(Position(2, 3), 5, Direction.East, Direction.West),
                Pipe(Position(1, 3), 4, Direction.South, Direction.East),
                Pipe(Position(1, 4), 3, Direction.North, Direction.West),
                Pipe(Position(0, 4), 2, Direction.North, Direction.East),
                Pipe(Position(0, 3), 1, Direction.North, Direction.South),
            )
        }

    def test_find_area_ex3(self, small_ex3_txt):
        pipe_map = PipeMap.from_file(small_ex3_txt)
        assert pipe_map.find_area() == {
            Position(2, 6),
            Position(3, 6),
            Position(7, 6),
            Position(8, 6),
        }

    def test_find_area_ex4(self, small_ex4_txt):
        pipe_map = PipeMap.from_file(small_ex4_txt)
        assert pipe_map.find_area() == {
            Position(13, 3),
            Position(7, 4),
            Position(8, 4),
            Position(9, 4),
            Position(7, 5),
            Position(8, 5),
            Position(6, 6),
            Position(13, 6),
        }

    def test_find_area_ex5(self, small_ex5_txt):
        pipe_map = PipeMap.from_file(small_ex5_txt)
        assert pipe_map.find_area() == {
            Position(14, 3),
            Position(10, 4),
            Position(11, 4),
            Position(12, 4),
            Position(13, 4),
            Position(11, 5),
            Position(12, 5),
            Position(13, 5),
            Position(13, 6),
            Position(14, 6),
        }


class TestQ1:
    def test_small_ex1(self, small_ex1_txt):
        assert q1(PipeMap.from_file(small_ex1_txt)) == 4

    def test_small_ex2(self, small_ex2_txt):
        return q1(PipeMap.from_file(small_ex2_txt)) == 8

    def test_input(self, input_txt):
        return q1(PipeMap.from_file(input_txt)) == 6640


class TestQ2:
    def test_small_ex3(self, small_ex3_txt):
        assert q2(PipeMap(small_ex3_txt)) == 4

    def test_small_ex4(self, small_ex4_txt):
        assert q2(PipeMap.from_file(small_ex4_txt)) == 8

    def test_small_ex5(self, small_ex5_txt):
        assert q2(PipeMap.from_file(small_ex5_txt)) == 10

    def test_input(self, input_txt):
        assert q2(PipeMap.from_file(input_txt)) == 42  # not the real value
