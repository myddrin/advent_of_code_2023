import dataclasses
import re
from argparse import ArgumentParser
from typing import (
    List,
    Self,
)


@dataclasses.dataclass(frozen=True)
class RacePlan:
    hold_duration: int  # in ms
    travel_distance: int  # in mm

    @property
    def speed(self) -> int:
        """In mm/ms"""
        return self.hold_duration

    @property
    def travel_duration(self) -> int:
        """In ms"""
        return self.travel_distance // self.speed


@dataclasses.dataclass(frozen=True)
class Record:
    race_duration: int  # in ms
    race_record: int  # in mm

    @classmethod
    def from_file(cls, filename: str) -> List[Self]:
        race_duration = None
        race_record = None

        print(f'Loading {filename}')
        with open(filename, 'r') as fin:
            line_split_re = re.compile(r'(Time|Distance):\s+([\s\d+]+)$')
            for line in fin:
                match = line_split_re.match(line)
                if match is not None:
                    title, content = match.groups()
                    if title == 'Time':
                        race_duration = [
                            int(d)
                            for d in content.split(' ')
                            if d  # remove empty slots as it's aligned
                        ]
                    elif title == 'Distance':
                        race_record = [int(d) for d in content.split(' ') if d]
                    else:
                        raise RuntimeError(f'Unexpected {title=}')

        if race_duration is None or race_record is None:
            raise RuntimeError(f'Incomplete {filename}')
        elif len(race_duration) != len(race_record):
            raise RuntimeError('Different number of duration than records')

        return [cls(race_duration=duration, race_record=record) for duration, record in zip(race_duration, race_record)]

    def race_plans(self) -> List[RacePlan]:
        """Get all race plans that beat the record"""
        winning_plans = []

        # speed is in mm/ms and is 1 mm/ms for every ms held
        for hold_duration in range(1, self.race_duration):
            speed = hold_duration
            race_left = self.race_duration - hold_duration
            plan = RacePlan(hold_duration, race_left * speed)

            if plan.travel_distance > self.race_record:
                winning_plans.append(plan)

        return winning_plans


def q1(records: List[Record]) -> int:
    mult = 1
    for record in records:
        mult *= len(record.race_plans())
    return mult


def main(filename: str):
    records = Record.from_file(filename)
    print(f'Q1: record race winning plans: {q1(records)}')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    main(args.input)
