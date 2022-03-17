import re


def read_input(filename):
    f = open(filename)
    step_match = re.compile(r'(on|off) x=(-?\d+)..(-?\d+),y=(-?\d+)..(-?\d+),z=(-?\d+)..(-?\d+)\n?')
    step_lst = [step_match.match(line).groups() for line in f.readlines()]
    f.close()
    return step_lst
