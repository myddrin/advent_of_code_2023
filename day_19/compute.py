import abc
import dataclasses
import json
from argparse import ArgumentParser
from collections import defaultdict
from copy import deepcopy
from typing import (
    ClassVar,
    Dict,
    List,
    Optional,
    Self,
    Set,
    Tuple,
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


@dataclasses.dataclass
class PartRange:
    @dataclasses.dataclass
    class _R:
        min: int = 1
        max: int = 4000

        @property
        def possibilities(self) -> int:
            return self.max - self.min + 1

        def as_tuple(self) -> Tuple[int, int]:
            return self.min, self.max

    # ranges are inclusive
    x: _R = dataclasses.field(default_factory=_R)
    m: _R = dataclasses.field(default_factory=_R)
    a: _R = dataclasses.field(default_factory=_R)
    s: _R = dataclasses.field(default_factory=_R)

    def __hash__(self):
        return hash(self.x.as_tuple() + self.m.as_tuple() + self.a.as_tuple() + self.s.as_tuple())

    @property
    def possibilities(self):
        return self.x.possibilities * self.m.possibilities * self.a.possibilities * self.s.possibilities

    def apply(self, rule: 'Check') -> Tuple[Self, Self]:
        self_copy = deepcopy(self)
        range_attr: PartRange._R = getattr(self_copy, rule.attr)
        reverse = deepcopy(self)
        reverse_range: PartRange._R = getattr(reverse, rule.attr)
        if rule.cmp == Check.GT:
            # update minimum
            range_attr.min = max(
                range_attr.min,
                rule.value + 1,
            )
            # reverse: update maximum
            reverse_range.max = min(
                reverse_range.max,
                rule.value,
            )
        elif rule.cmp == Check.LT:
            # update maximum
            range_attr.max = min(
                range_attr.max,
                rule.value - 1,
            )
            # reverse: update minimum
            reverse_range.min = max(
                reverse_range.min,
                rule.value,
            )

        return self_copy, reverse


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

    def _visitor(self, part_range: PartRange, next_workflow: str) -> Set[PartRange]:
        if next_workflow == Rule.ACCEPTED:
            return {part_range}
        elif next_workflow == Rule.REJECTED:
            return set()

        rules = self.workflows[next_workflow]
        next_rules: Dict[str, Set[PartRange]] = defaultdict(set)
        current_range = part_range
        for r in rules[:-1]:
            if isinstance(r, Check):
                new_ranges = current_range.apply(r)
                next_rules[r.target].add(new_ranges[0])
                current_range = new_ranges[1]
            else:
                raise ValueError(f'Unexpected {r}')
        # apply else rule
        next_rules[rules[-1].target].add(current_range)

        results = set()
        for workflow, part_ranges in next_rules.items():
            for part_range in part_ranges:
                results.update(self._visitor(part_range, workflow))
        return results

    def visit_for_accepted(self) -> int:
        results = self._visitor(PartRange(), 'in')
        return sum(res.possibilities for res in results)

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
    print(f'Q2: {workflow.visit_for_accepted()} possibilities')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    main(args.input)
