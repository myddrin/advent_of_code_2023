import dataclasses
import re
from argparse import ArgumentParser
from typing import (
    ClassVar,
    Dict,
    List,
    Optional,
    Self,
)


def hash_step(step: str) -> int:
    current = 0
    for c in step:
        current = ((current + ord(c)) * 17) % 256

    return current


@dataclasses.dataclass
class Lens:
    focal: int
    label: str
    prev: 'Lens' = None
    next: 'Lens' = None


@dataclasses.dataclass
class LensBox:
    index: Dict[str, Lens] = dataclasses.field(default_factory=dict)
    first: Optional[Lens] = None
    last: Optional[Lens] = None

    def add(self, lens: Lens):
        old_lens = self.index.get(lens.label)
        if old_lens:
            old_lens.label = lens.label
            old_lens.focal = lens.focal
        else:
            self.index[lens.label] = lens
            if self.first is None:
                self.first = lens

            lens.prev = self.last
            if self.last is not None:
                self.last.next = lens
            self.last = lens

    def remove(self, label: str):
        lens = self.index.pop(label, None)
        if lens is not None:
            if lens.prev is not None:
                lens.prev.next = lens.next
            if lens.next is not None:
                lens.next.prev = lens.prev

            if self.first is lens:
                self.first = lens.next
            if self.last is lens:
                self.last = lens.prev

    def get_focusing_power(self, box_index: int) -> int:
        current_value = 0
        current_idx = 1
        lens = self.first
        while lens is not None:
            current_value += box_index * current_idx * lens.focal
            lens = lens.next
            current_idx += 1
        return current_value


class BoxSystem:
    action_add_re: ClassVar = re.compile(r'(.*)=(\d+)$')
    action_rem_re: ClassVar = re.compile(r'(.*)-$')

    def __init__(self):
        self.boxes = [LensBox() for _ in range(256)]

    def load(self, init_seq: 'InitSeq') -> Self:
        for action in init_seq.steps:
            if m := self.action_rem_re.match(action):
                lens_label = m.group(1)
                box = hash_step(lens_label)
                self.boxes[box].remove(lens_label)
            elif m := self.action_add_re.match(action):
                lens_label, focal_str = m.groups()
                new_lens = Lens(int(focal_str), lens_label)
                box = hash_step(lens_label)
                self.boxes[box].add(new_lens)
            else:
                raise ValueError(f'Unexpected {action}')

        return self

    def get_focusing_power(self) -> int:
        return sum((box.get_focusing_power(i) for i, box in enumerate(self.boxes, start=1)))


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


def q2(init_seq: InitSeq) -> int:
    return BoxSystem().load(init_seq).get_focusing_power()


def main(filename: str):
    seq = InitSeq.from_file(filename)

    print(f'Q1: checksum is {seq.checksum()}')
    print(f'Q2: focus power {q2(seq)}')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    main(args.input)
