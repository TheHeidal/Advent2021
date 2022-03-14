import itertools
import re
from itertools import islice

WINNING_SCORE = 1000

MAX_SPACE = 10


def read_input(filename):
    f = open(filename)
    start_pos_match = re.compile(r'Player (\d+) starting position: (\d*)\s*')
    return [[int(start_pos_match.match(line).group(1)), int(start_pos_match.match(line).group(2))]
            for line in f.readlines()]


def deterministic_die(n):
    curr = 1
    max_val = 100
    while curr <= n:
        yield ((curr - 1) % max_val) + 1
        curr = ((curr - 1) % max_val) + 2


class DeterministicDie:

    def __init__(self, max_val):
        self.num_rolls = 0
        self._die = self.create_die(max_val)

    def roll(self, num_rolls):
        return islice(self._die, num_rolls)

    def create_die(self, max_val):
        curr_val = 1
        while True:
            self.num_rolls += 1
            yield ((curr_val - 1) % max_val) + 1
            curr_val = ((curr_val - 1) % max_val) + 2

itertools.permutations

class Player:
    def __init__(self, index, position):
        self.index = index
        self.position = position
        self.score = 0

    def move(self, die, rolls=3):
        dist = sum(die.roll(rolls))
        self.position = (self.position + dist - 1) % MAX_SPACE + 1
        self.score += self.position

    def __repr__(self):
        return f'P{self.index} @ {self.position} w/ {self.score}'


def play(players_, die):
    while True:
        for p in players_:
            p.move(die)
            if p.score >= WINNING_SCORE:
                return players_


if __name__ == '__main__':
    player_datas = read_input('D21.txt')
    players = [Player(data[0], data[1]) for data in player_datas]
    d_die = DeterministicDie(100)
    play(players, d_die)
    loser = [p for p in players if p.score < WINNING_SCORE][0]
    print(loser.score * d_die.num_rolls)
