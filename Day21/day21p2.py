import timeit
from functools import reduce

import numpy as np

WINNING_SCORE = 21
# probability, value pairs
rolls = [(1, 3), (3, 4), (6, 5), (7, 6), (6, 7), (3, 8), (1, 9)]


state_to_outcome = dict()



def new_space(pos, roll):
    return (((pos + roll) - 1) % 10) + 1


def generate_successors(turn: bool, p1_pos: int, p1_score: int, p2_pos: int, p2_score: int):
    if turn:
        return [(p, (False,
                     new_space(p1_pos, roll),
                     p1_score + new_space(p1_pos,
                                          roll),
                     p2_pos, p2_score))
                for p, roll in rolls]
    else:
        return [(p, (True,
                     p1_pos, p1_score,
                     new_space(p2_pos, roll),
                     p2_score + new_space(p2_pos, roll)))
                for p, roll in rolls]


def check_winner(turn: bool, p1_pos: int, p1_score: int, p2_pos: int, p2_score: int):
    if p1_score >= WINNING_SCORE:
        return True
    elif p2_score >= WINNING_SCORE:
        return False
    else:
        return turn, p1_pos, p1_score, p2_pos, p2_score


def find_outcome(state):
    """given a state, returns an array representing how many ways players 1 and 2 could win"""
    global total
    global calculate
    global lookup
    total += 1

    check = check_winner(*state)
    if type(check) is not tuple:
        if check:
            return np.array([1, 0], dtype=np.int64)
        else:
            return np.array([0, 1], dtype=np.int64)
    elif state not in state_to_outcome.keys():
        calculate += 1
        successors = generate_successors(*state)
        successor_outcomes = [p * find_outcome(s) for p, s in successors]
        state_to_outcome[state] = reduce(np.add, successor_outcomes)
    else:
        lookup += 1
    return state_to_outcome[state]


if __name__ == '__main__':
    lookup = 0
    calculate = 0
    total = 0

    starting_state = (True, 6, 0, 2, 0)
    start = timeit.default_timer()
    outcome = find_outcome(starting_state)
    stop = timeit.default_timer()
    print('time: ', stop - start)

    print(outcome)
    print(max(outcome))
    print('Total searches: ', total)
    print('Lookups: ', lookup)
    print('calculations: ', calculate)

    print('calculated nodes: ', len(state_to_outcome))
