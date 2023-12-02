import dataclasses
import re
from argparse import ArgumentParser
from typing import (
    ClassVar,
    Iterable,
    List,
    Self,
)


@dataclasses.dataclass(frozen=True)
class Record:
    colour_re: ClassVar = re.compile(r'\s?(\d+)\s(.*)')

    blue: int = 0
    red: int = 0
    green: int = 0

    @property
    def power(self) -> int:
        return self.blue * self.red * self.green

    @classmethod
    def from_line(cls, line: str) -> List[Self]:
        records = []
        for record in line.split(';'):
            kwargs = {}
            for colour_part in record.split(','):
                count_str, colour = cls.colour_re.match(colour_part).groups()
                kwargs[colour] = int(count_str)
            records.append(cls(**kwargs))
        return records

    def is_possible(self, config: Self) -> bool:
        return self.blue <= config.blue and self.red <= config.red and self.green <= config.green


@dataclasses.dataclass(frozen=True)
class Game:
    game_re: ClassVar = re.compile(r'^Game\s(\d+):\s(.*)$')

    id: int
    records: List[Record]

    @classmethod
    def from_line(cls, line: str) -> Self:
        game_id_str, game_records_str = cls.game_re.match(line).groups()
        return cls(
            id=int(game_id_str),
            records=Record.from_line(game_records_str),
        )

    @classmethod
    def from_file(cls, filename: str) -> List[Self]:
        print(f'Loading {filename}')
        games = []
        with open(filename, 'r') as fin:
            for line in fin:
                games.append(cls.from_line(line))
        return games

    @classmethod
    def check_configuration(cls, games: List[Self], config: Record) -> Iterable[Self]:
        for current_game in games:
            is_valid = True
            for record in current_game.records:
                is_valid &= record.is_possible(config)
            if is_valid:
                yield current_game

    def minimum_setup(self) -> Record:
        return Record(
            blue=max((record.blue for record in self.records)),
            green=max((record.green for record in self.records)),
            red=max((record.red for record in self.records)),
        )


def q1(data: List[Game]) -> int:
    config = Record(red=12, green=13, blue=14)
    sum_valid_ids = 0
    for game in data:
        is_valid = True
        for record in game.records:
            is_valid &= record.is_possible(config)
        if is_valid:
            sum_valid_ids += game.id

    return sum_valid_ids


def q2(data: List[Game]) -> int:
    sum_of_powers = 0
    for game in data:
        minimum_set = game.minimum_setup()
        sum_of_powers += minimum_set.power
    return sum_of_powers


def main(filename: str):
    data = Game.from_file(filename)

    print(f'Q1: sum of possible id: {q1(data)}')
    print(f'Q2: sum of powers: {q2(data)}')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    main(args.input)
