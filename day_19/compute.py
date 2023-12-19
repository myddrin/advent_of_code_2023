import abc
import dataclasses
import json
from argparse import ArgumentParser
from typing import (
    ClassVar,
    Dict,
    List,
    Optional,
    Self,
)


@dataclasses.dataclass(frozen=True)
class Part:
    x: int  # extremely cool looking
    m: int  # musical
    a: int  # aerodynamic
    s: int  # shiny

    @property
    def score(self) -> int:
        return self.x + self.m + self.a + self.s

    @classmethod
    def from_line(cls, line: str) -> Self:
        # transform lines line `{x=787,m=2655,a=1222,s=2876}` to json
        line = line.replace('{', '{"').replace(',', ',"').replace('=', '":')
        data = json.loads(line)
        return cls(**data)


@dataclasses.dataclass(frozen=True)
class Rule(metaclass=abc.ABCMeta):
    ACCEPTED: ClassVar = 'A'
    REJECTED: ClassVar = 'R'

    target: str

    @abc.abstractmethod
    def check(self, part: Part) -> Optional[str]:
        raise NotImplementedError()

    @classmethod
    def from_str(cls, value: str) -> Self:
        if ':' in value:
            return Check.from_str(value)
        return GoTo(value)


@dataclasses.dataclass(frozen=True)
class GoTo(Rule):
    def check(self, part: Part):
        return self.target


@dataclasses.dataclass(frozen=True)
class Check(Rule):
    LT: ClassVar = '<'
    GT: ClassVar = '>'

    attr: str
    cmp: str
    value: int

    def check(self, part: Part) -> Optional[str]:
        part_value: int = getattr(part, self.attr)
        if self.cmp == self.LT and part_value < self.value:
            return self.target
        elif self.cmp == self.GT and part_value > self.value:
            return self.target
        return None

    @classmethod
    def from_str(cls, value_str: str) -> Self:
        rule, target = value_str.split(':')
        if cls.LT in rule:
            cmp = cls.LT
        elif cls.GT in rule:
            cmp = cls.GT
        else:
            raise ValueError(f'Unsupported rule from: "{value_str}"')

        attr, value_str = rule.split(cmp)
        return cls(
            target=target,
            attr=attr,
            cmp=cmp,
            value=int(value_str),
        )


@dataclasses.dataclass
class Workflow:
    workflows: Dict[str, List[Rule]] = dataclasses.field(default_factory=dict)
    parts: List[Part] = dataclasses.field(default_factory=list)

    def check_accepted(self, part: Part) -> bool:
        current = 'in'

        while current not in (Rule.ACCEPTED, Rule.REJECTED):
            rules = self.workflows[current]

            for r in rules:
                current = r.check(part)
                if current is not None:
                    break

        return current == Rule.ACCEPTED

    def load_rule_line(self, line: str):
        name_idx = line.find('{')
        name = line[:name_idx]
        # hdj{m>838:A,pv}
        rules_str = line[name_idx + 1 : -1]
        rules = []
        for rule_part in rules_str.split(','):
            rules.append(Rule.from_str(rule_part))

        self.workflows[name] = rules

    @classmethod
    def from_file(cls, filename: str) -> Self:
        obj = cls()
        print(f'Loading {filename}')
        loading_rules = True
        with open(filename, 'r') as fin:
            for line in fin:
                line = line.replace('\n', '')
                if not line:
                    # skip the empty line and switch to loading parts
                    loading_rules = False
                    continue

                if loading_rules:
                    obj.load_rule_line(line)
                else:
                    obj.parts.append(Part.from_line(line))
        print(f'  -> Loaded {len(obj.parts)} parts and {len(obj.workflows)} workflow')
        return obj


def q1(workflow: Workflow) -> int:
    return sum((p.score for p in workflow.parts if workflow.check_accepted(p)))


def main(filename: str):
    workflow = Workflow.from_file(filename)

    print(f'Q1: accepted score is {q1(workflow)}')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    main(args.input)
