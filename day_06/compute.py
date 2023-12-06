import dataclasses
import re
import time
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
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
    def from_file(cls, filename: str, *, fix_spaces: bool = False) -> List[Self]:
        race_duration = None
        race_record = None

        print(f'Loading {filename}')
        with open(filename, 'r') as fin:
            line_split_re = re.compile(r'(Time|Distance):\s+([\s\d+]+)$')
            for line in fin:
                match = line_split_re.match(line)
                if match is not None:
                    title, content = match.groups()
                    if fix_spaces:
                        # for q2: 7  15   30 -> 71530
                        content = content.replace(' ', '')

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

    def race_plans(self, range_st: int = None, range_ed: int = None) -> int:
        """Get all race plans that beat the record"""
        winning_plans = 0
        if range_st is None:
            range_st = 1
        if range_ed is None:
            range_ed = self.race_duration

        # print(
        #     f'{range_st}: Computing winning plans for race of {self.race_duration}ms '
        #     f'for range ({range_st}, {range_ed})',
        # )
        # start = time.time()
        # speed is in mm/ms and is 1 mm/ms for every ms held
        for hold_duration in range(range_st, range_ed):
            speed = hold_duration
            race_left = self.race_duration - hold_duration
            plan = RacePlan(hold_duration, race_left * speed)

            if plan.travel_distance > self.race_record:
                winning_plans += 1
        # end = time.time()
        # print(f'{range_st}: found {winning_plans} winning plans in {end - start:0.2f}s')
        return winning_plans


def count_points(records: List[Record]) -> int:
    mult = 1
    for record in records:
        mult *= record.race_plans()
    return mult


def threaded_count_points(records: List[Record], step: int = 1000000) -> int:
    mult = 1
    start = time.time()
    with ThreadPoolExecutor() as executor:
        for record in records:
            wip = []
            st = 1
            for ed in range(min(step, record.race_duration), record.race_duration + 1, step):
                wip.append(executor.submit(
                    record.race_plans,
                    st,
                    ed,
                ))
                st = ed
            print(f'  started {len(wip)} tasks to find winning plans for race of {record.race_duration}ms')
            mult *= sum((fut.result() for fut in wip))
    end = time.time()
    print(f'Finished computing {len(records)} races winning plans in {end - start:0.2f}s')
    return mult


def main(filename: str):
    q1_records = Record.from_file(filename)
    print(f'Q1: record race winning plans: {threaded_count_points(q1_records)}')
    q2_records = Record.from_file(filename, fix_spaces=True)
    print(f'Q2: record race winning plans: {threaded_count_points(q2_records)}')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    main(args.input)
