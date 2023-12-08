import dataclasses
import re
from argparse import ArgumentParser
from typing import (
    ClassVar,
    Dict,
    Optional,
    Self,
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

    def follow(self, start: str = 'AAA', end: str = 'ZZZ') -> int:
        n_iterations = 0
        current_idx = 0

        current_node = self.node_map[start]

        while current_node.name != end:
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


def q1(node_map: NodeMap) -> int:
    return node_map.follow()


def main(filename: str):
    node_map = NodeMap.from_file(filename)

    print(f'Q1: it took {q1(node_map)} iteration to find ZZZ')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    main(args.input)
