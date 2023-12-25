import dataclasses
import time
from argparse import ArgumentParser
from operator import itemgetter
from typing import (
    Dict,
    Iterable,
    List,
    Optional,
    Self,
    Set,
    Tuple,
)


@dataclasses.dataclass
class Node:
    name: str

    connections: List[str] = dataclasses.field(default_factory=list)

    def connect(self, node_name: str):
        if node_name not in self.connections:
            self.connections.append(node_name)


@dataclasses.dataclass(frozen=True)
class Edge:
    node_a: str
    node_b: str

    def select_other(self, node_name: str) -> Optional[str]:
        reverse = {
            self.node_a: self.node_b,
            self.node_b: self.node_a,
        }
        return reverse.get(node_name)

    @classmethod
    def build(cls, node_a: str, node_b: str) -> Self:
        if node_a == node_b:
            raise ValueError('Need two different nodes')
        elif node_a < node_b:
            return cls(node_a, node_b)
        return cls(node_b, node_a)

    @classmethod
    def build_from_path(cls, path: List[str]) -> Iterable[Self]:
        previous = path[0]
        for p in path[1:]:
            yield Edge.build(previous, p)
            previous = p


@dataclasses.dataclass
class Graph:
    nodes: Dict[str, Node] = dataclasses.field(default_factory=dict)
    shortest_path: Dict[Edge, List[str]] = dataclasses.field(default_factory=dict)
    betweenness: Dict[Edge, int] = dataclasses.field(default_factory=dict)

    @classmethod
    def from_file(cls, filename: str) -> Self:
        graph = cls()
        print(f'Loading {filename}')
        with open(filename, 'r') as fin:
            for line in fin:
                line = line.replace('\n', '')
                first, others = line.split(': ')
                others = others.split(' ')
                graph.connect(first, others)
        return graph

    def _dijkstra(self, start_node: Node) -> Dict[Edge, List[str]]:
        previous: Dict[str, List[str]] = {start_node.name: []}
        done: Set[str] = set()
        # TODO(tr) something like that to make it faster on futher runs?
        # for edge, prev in self.shortest_path.items():
        #     if other := edge.select_other(start_node.name):
        #         previous[other] = prev
        #         done.add(other)

        while len(done) < len(self.nodes):
            pending = sorted(
                [(p, len(previous[p])) for p in self.nodes if p in previous and p not in done],
                key=itemgetter(1),
            )
            selected, _ = pending[0]
            selected_node = self.nodes[selected]
            done.add(selected)

            pending_neighbours = {other_name for other_name in selected_node.connections if other_name not in done}

            for other in pending_neighbours:
                new_previous = previous[selected] + [selected]
                current_previous = previous.get(other)
                if current_previous is None or len(new_previous) < len(current_previous):
                    previous[other] = new_previous

        return {
            Edge.build(start_node.name, other): path + [other]
            for other, path in previous.items()
            if other != start_node.name
        }

    def full_dijkstra(self):
        n_nodes = len(self.nodes)
        start_time = time.time()
        for i, node in enumerate(self.nodes.values(), start=1):
            print(f'  dijkstra for {node.name}: {i}/{n_nodes}  ', end='\r')
            short_paths = self._dijkstra(node)
            self.shortest_path.update(short_paths)
            for path in short_paths.values():
                for edge in Edge.build_from_path(path):
                    if edge not in self.betweenness:
                        self.betweenness[edge] = 0
                    self.betweenness[edge] += 1
        print()
        end_time = time.time()
        print(f'Graph buildup done in {end_time - start_time:0.2f}s')

    def find_most_used_edge(self) -> Edge:
        most_used: List[Tuple[Edge, int]] = sorted(self.betweenness.items(), key=itemgetter(1), reverse=True)
        return most_used[0][0]

    def _new_graph(self, start: str, ignore: Edge, done: Dict[str, str], *, name: str) -> Self:
        graph = Graph()
        pending = [graph.get(start)]

        while pending:
            current = pending.pop(0)
            if current.name in done:
                if done[current.name] == name:
                    continue  # already done
                raise RuntimeError(f'Cannot add {current} to {name}: it is already in {done[current.name]}')
            done[current.name] = name
            for conn in self.nodes[current.name].connections:
                edge = Edge.build(current.name, conn)
                if edge == ignore:
                    continue  # cut the link
                if conn not in done:
                    other_node = graph.get(conn)
                    current.connect(conn)
                    other_node.connect(current.name)
                    pending.append(other_node)
                    # TODO(tr) copy the shortest path information to make next dijkstra faster?

        return graph

    def new_graphs(self, cut: Edge) -> List[Self]:
        done_cache: Dict[str, str] = {}
        graphs = [
            self._new_graph(cut.node_a, cut, done_cache, name='a'),
        ]
        missing = set(self.nodes) - set(done_cache)
        if missing:
            # build a second graph
            graphs.append(self._new_graph(cut.node_b, cut, done_cache, name='b'))

        missing = set(self.nodes) - set(done_cache)
        if missing:
            raise RuntimeError(f'Missing: {", ".join(sorted(missing))}')
        return graphs

    def get(self, node_name: str) -> Node:
        if node_name not in self.nodes:
            self.nodes[node_name] = Node(node_name)
        return self.nodes[node_name]

    def connect(self, a: str, other: List[str]):
        node_a = self.get(a)
        for b in other:
            node_b = self.get(b)
            node_a.connect(b)
            node_b.connect(a)

    def to_dot_file(self, filename: str, *, graph_name: str):
        print(f'Saving {filename}')
        with open(filename, 'w') as fout:
            fout.write(f'graph {graph_name} {{\n')
            for node_name in self.nodes.keys():
                fout.write(f'"{node_name}" []\n')
            already_done = set()
            for node in self.nodes.values():
                left_connections = [other for other in node.connections if other not in already_done]
                for conn in left_connections:
                    attributes = []
                    edge = Edge.build(node.name, conn)
                    if (label_content := self.betweenness.get(edge)) is not None:
                        attributes.append(f'label="{label_content}"')
                    fout.write(f'"{node.name}" -- "{conn}" [{", ".join(attributes)}]\n')
                already_done.add(node.name)
            fout.write('}')  # end graph


def q1(graph: Graph, n: int = 3) -> int:
    graph.to_dot_file('output_original.dot', graph_name='original')
    # To render use `dot -Tpng output_xx.dot -o output_xx.png`

    new_graphs = [graph]
    i = 0
    while i < n:
        if len(new_graphs) > 1:
            print(f'No more cuts needed after {i} cuts!')
            break
        graph = new_graphs[0]
        print(f'Edges left to cut {n - i}')
        graph.full_dijkstra()
        # use `dot -Tpng output_xx.dot -o output_xx.png`
        graph.to_dot_file(f'output_{i}.dot', graph_name=f'g_{i}')

        cut = graph.find_most_used_edge()
        new_graphs = graph.new_graphs(cut)
        i += 1

    comp = 1
    for i, g in enumerate(new_graphs, start=1):  # type: int, Graph
        g.to_dot_file(f'output_cut{i}.dot', graph_name=f'q1_{i}')
        comp *= len(g.nodes)
    return comp


def main(filename: str):
    graph = Graph.from_file(filename)

    print(f'Q1: components: {q1(graph, n=3)}')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    main(args.input)
