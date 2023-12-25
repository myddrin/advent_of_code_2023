import os

import pytest

from day_25.compute import (
    Edge,
    Graph,
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


class TestEdge:
    @pytest.mark.parametrize(
        'path, exp',
        (
            (['aaa', 'aab', 'aac'], {Edge('aaa', 'aab'), Edge('aab', 'aac')}),
            (['aab', 'aaa'], {Edge('aaa', 'aab')}),
        ),
    )
    def test_build_from_path(self, path, exp):
        assert Edge.build_from_path(path) == exp


class TestGraph:
    def test_full_dijkstra(self, small_ex_txt):
        graph = Graph.from_file(small_ex_txt)
        graph.full_dijkstra()

        jqt = graph.nodes['jqt']
        for conn in jqt.connections:
            e = Edge.build('jqt', conn)
            assert graph.shortest_path[e] == {e}
        # further neighbours checks


class TestQ1:
    def test_small_ex(self, small_ex_txt):
        graph = Graph.from_file(small_ex_txt)
        assert q1(graph) == 54

    @pytest.mark.slow
    def test_input(self, input_txt):
        # takes ~15min
        graph = Graph.from_file(input_txt)
        assert q1(graph) == 583338
