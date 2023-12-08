import dataclasses
import math
import re
from argparse import ArgumentParser
from typing import (
    ClassVar,
    Dict,
    List,
    Optional,
    Self,
    Tuple,
)


@dataclasses.dataclass
class Node:
    name: str
    left: Optional[str] = None
    right: Optional[str] = None

    node_re: ClassVar = re.compile(r'(.*)\s=\s\((.*),\s(.*)\)')

    @classmethod
    def from_line(cls, line: str) -> Self:
        name, left, right = cls.node_re.match(line).groups()
        return cls(name=name, left=left, right=right)


@dataclasses.dataclass
class NodeMap:
    instructions: str
    node_map: Dict[str, Node]

    @classmethod
    def from_file(cls, filename: str) -> Self:
        print(f'Loading {filename}')
        instructions = None
        nodes = {}
        with open(filename, 'r') as fin:
            for line in fin:
                line = line.replace('\n', '')
                if not line:
                    continue

                if instructions is None:
                    instructions = line
                else:
                    new_node = Node.from_line(line)

                    nodes[new_node.name] = new_node
                    if new_node.left not in nodes:
                        nodes[new_node.left] = Node(new_node.left)
                    if new_node.right not in nodes:
                        nodes[new_node.right] = Node(new_node.right)

        print(f'  -> {len(instructions)} directions to navigate {len(nodes)} nodes')
        return cls(instructions, nodes)

    def get_left(self, node: Node) -> Node:
        if node.left is None:
            raise ValueError(f'Failed to load {node.name}')
        return self.node_map[node.left]

    def get_right(self, node: Node) -> Node:
        if node.right is None:
            raise ValueError(f'Failed to load {node.name}')
        return self.node_map[node.right]

    def follow_one(self, start: str = 'AAA', end_with: str = 'ZZZ') -> int:
        n_iterations = 0
        current_idx = 0

        current_node = self.node_map[start]

        while not current_node.name.endswith(end_with):
            current_instruction = self.instructions[current_idx]
            if current_instruction == 'L':
                current_node = self.get_left(current_node)
            elif current_instruction == 'R':
                current_node = self.get_right(current_node)
            else:
                raise ValueError(f'Unexpected instruction {current_idx}:{current_instruction}')

            current_idx = (current_idx + 1) % len(self.instructions)
            n_iterations += 1

        return n_iterations

    def find_loops(self, start: str, end_width: str = 'Z') -> List[int]:
        # Dict[(name, instruction idx) -> n_iteration]
        visited: Dict[Tuple[str, int], int] = {}

        n_iterations = 0
        current_idx = 0

        current_node = self.node_map[start]

        print(f'Find all loops from {start}')
        found_end = False
        rolled_over_since_end = False

        while not rolled_over_since_end:
            current_visited = (current_node.name, current_idx)
            if current_visited in visited:
                print(f' stopping because we are looping at {current_visited}')
                break

            visited[current_visited] = n_iterations

            current_instruction = self.instructions[current_idx]
            if current_instruction == 'L':
                current_node = self.get_left(current_node)
            elif current_instruction == 'R':
                current_node = self.get_right(current_node)
            else:
                raise ValueError(f'Unexpected instruction {current_idx}:{current_instruction}')

            rolled_over_since_end = found_end and current_idx == len(self.instructions) - 1

            current_idx = (current_idx + 1) % len(self.instructions)
            n_iterations += 1

        if rolled_over_since_end:
            print(f' aborted at {n_iterations}')
        all_loops = [(key[0], key[1], n_ite) for key, n_ite in visited.items() if key[0].endswith(end_width)]
        print(f'All loops for {start}: {all_loops!r}')
        return all_loops

    def follow_all_fast(self, start_ends_with: str = 'A', end_ends_with: str = 'Z') -> int:
        start_nodes = [node for node_name, node in self.node_map.items() if node_name.endswith(start_ends_with)]
        print(f'  using {len(start_nodes)} starting nodes')

        # assuming there is a single loop per node
        loop_durations = [self.follow_one(current_node.name, end_with=end_ends_with) for current_node in start_nodes]

        # just to print it
        [self.find_loops(current_node.name, end_width=end_ends_with) for current_node in start_nodes]

        for st, first_loop in zip(start_nodes, loop_durations):
            print(f' {st.name} loop is {first_loop}')

        # I'm not convince this is a universal solution because if the loops aren't at
        # the same instruction index we could be off...
        # But this worked for my colleague's input and mine...
        return math.lcm(*loop_durations)

    def follow_all(self, start_ends_with: str = 'A', end_ends_with: str = 'Z') -> int:
        n_iterations = 0
        current_idx = 0

        current_nodes = [node for node_name, node in self.node_map.items() if node_name.endswith(start_ends_with)]
        print(f'  using {len(current_nodes)} starting nodes')

        while not all((node.name.endswith(end_ends_with) for node in current_nodes)):
            current_instruction = self.instructions[current_idx]
            new_current_nodes = []
            for current_node in current_nodes:
                if current_instruction == 'L':
                    current_node = self.get_left(current_node)
                elif current_instruction == 'R':
                    current_node = self.get_right(current_node)
                else:
                    raise ValueError(f'Unexpected instruction {current_idx}:{current_instruction}')
                new_current_nodes.append(current_node)

            current_nodes = new_current_nodes
            current_idx = (current_idx + 1) % len(self.instructions)
            n_iterations += 1

            if n_iterations % 1000000 == 0:
                print(f'  ... {n_iterations} iterations later we are still inside')

        return n_iterations


def q1(node_map: NodeMap) -> int:
    return node_map.follow_one()


def q2(node_map: NodeMap) -> int:
    return node_map.follow_all_fast()


def main(filename: str):
    node_map = NodeMap.from_file(filename)

    # print(f'Q1: it took {q1(node_map)} iteration to find ZZZ')
    print(f'Q2: it took {q2(node_map)} iteration to find *Z from *A')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    main(args.input)
