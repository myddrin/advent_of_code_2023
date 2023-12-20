import dataclasses
from argparse import ArgumentParser
from typing import (
    Dict,
    List,
    Self,
)


@dataclasses.dataclass(frozen=True)
class Pulse:
    mod_from: str
    mod_to: str
    value: bool


@dataclasses.dataclass
class Module:
    name: str
    input_names: List[str]
    output_names: List[str]

    def initialise(self):
        pass

    def process(self, pulse: Pulse) -> List[Pulse]:
        return [Pulse(self.name, mod_name, pulse.value) for mod_name in self.output_names]

    @classmethod
    def from_line(cls, line: str) -> Self:
        name, outputs = line.split(' -> ')
        outputs = outputs.split(', ')
        if name.startswith('%'):
            return FlipFlop(name[1:], [], outputs)
        elif name.startswith('&'):
            return Conjunction(name[1:], [], outputs)
        else:
            return Module(name, [], outputs)


@dataclasses.dataclass
class FlipFlop(Module):
    state: bool = False

    def initialise(self):
        self.state = False

    def process(self, pulse: Pulse) -> List[Pulse]:
        if not pulse.value:
            self.state ^= True
            return [Pulse(self.name, mod_name, self.state) for mod_name in self.output_names]
        return []


@dataclasses.dataclass
class Conjunction(Module):
    memory: Dict[str, bool] = dataclasses.field(default_factory=dict)

    def initialise(self):
        self.memory = {mod_name: False for mod_name in self.input_names}

    def process(self, pulse: Pulse) -> List[Pulse]:
        self.memory[pulse.mod_from] = pulse.value
        emits = not all(self.memory.values())
        return [Pulse(self.name, mod_name, emits) for mod_name in self.output_names]


@dataclasses.dataclass
class System:
    modules: Dict[str, Module]

    @classmethod
    def from_file(cls, filename: str) -> Self:
        print(f'Loading {filename}')
        modules = []
        with open(filename, 'r') as fin:
            for line in fin:
                line = line.replace('\n', '')
                modules.append(Module.from_line(line))
        return cls(modules={mod.name: mod for mod in modules})

    def __post_init__(self):
        # initialise modules inputs
        for name, module in list(self.modules.items()):
            for output_mod in module.output_names:
                if output_mod not in self.modules:
                    self.modules[output_mod] = Module(output_mod, [], [])
                self.modules[output_mod].input_names.append(name)
        for module in self.modules.values():
            module.initialise()

    def press_button(self) -> Dict[bool, int]:
        pulse_count = {
            True: 0,
            False: 0,
        }
        to_process = [Pulse('button', 'broadcaster', False)]

        while to_process:
            current = to_process.pop()
            pulse_count[current.value] += 1
            to_process.extend(self.modules[current.mod_to].process(current))

        return pulse_count

    def cycle(self, n: int = 1000) -> int:
        high_count = 0
        low_count = 0

        for i in range(1, n + 1, 1):
            states = self.press_button()
            high_count += states[True]
            low_count += states[False]
            if i % 100 == 0:
                print(f'  after {i}/{n} state is {high_count=} {low_count=}')

        return high_count * low_count


def main(filename: str):
    system = System.from_file(filename)

    print(f'Q1: score: {system.cycle()}')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    main(args.input)
