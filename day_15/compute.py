import dataclasses
from argparse import ArgumentParser
from typing import (
    List,
    Self,
)


def hash_step(step: str) -> int:
    current = 0
    for c in step:
        current = ((current + ord(c)) * 17) % 256

    return current


@dataclasses.dataclass(frozen=True)
class InitSeq:
    steps: List[str]

    def checksum(self) -> int:
        return sum(hash_step(step) for step in self.steps)

    @classmethod
    def from_file(cls, filename: str) -> Self:
        print(f'Loading {filename}')
        with open(filename, 'r') as fin:
            steps = []
            for line in fin:
                line = line.replace('\n', '')
                steps.extend(line.split(','))

        print(f'  -> loaded {len(steps)} steps')
        return cls(steps)


def main(filename: str):
    seq = InitSeq.from_file(filename)

    print(f'Q1: checksum is {seq.checksum()}')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    main(args.input)
