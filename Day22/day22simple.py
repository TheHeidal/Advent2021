import re

import numpy as np


def read_input(filename):
    f = open(filename)
    step_match = re.compile(r'(on|off) x=(-?\d+)..(-?\d+),y=(-?\d+)..(-?\d+),z=(-?\d+)..(-?\d+)\n?')
    step_lst = [step.groups() for step in (step_match.match(line) for line in f.readlines()) if step is not None]
    f.close()
    return step_lst


class InitializeStep:
    """
    A step in the reboot sequence
    """

    def __init__(self, state, x_min, x_max, y_min, y_max, z_min, z_max):
        self.state = state == 'on'
        xmin, xmax = int(x_min), int(x_max)
        ymin, ymax = int(y_min), int(y_max)
        zmin, zmax = int(z_min), int(z_max)
        if any((mx < -50 for mx in [xmax, ymax, zmax])) or any((mn > 50 for mn in [xmin, ymin, zmin])):
            self.malformed = True
        else:
            self.malformed = False
            xmin = max(xmin, -50)
            ymin = max(ymin, -50)
            zmin = max(zmin, -50)
            xmax = min(xmax, 50)
            ymax = min(ymax, 50)
            zmax = min(zmax, 50)
            self.x_range = range(xmin, xmax + 1)
            self.y_range = range(ymin, ymax + 1)
            self.z_range = range(zmin, zmax + 1)

    def correct(self):
        if any([r.stop <= -50 for r in [self.x_range, self.y_range, self.z_range]]):
            self = None

    def __repr__(self):
        return (f"{'on' if self.state else 'off'} "
                f"x={self.x_range.start}..{self.x_range.stop - 1},"
                f"y={self.y_range.start}..{self.y_range.stop - 1},"
                f"z={self.z_range.start}..{self.z_range.stop - 1}")


def apply_step(array, step: InitializeStep):
    if step is None:
        return
    array[
    step.x_range.start + 50:step.x_range.stop + 50,
    step.y_range.start + 50:step.y_range.stop + 50,
    step.z_range.start + 50:step.z_range.stop + 50] = step.state


if __name__ == '__main__':
    data = read_input('input.txt')
    steps = [stp for stp in (InitializeStep(*s) for s in data) if not stp.malformed]
    reactor = np.zeros((101, 101, 101), dtype=np.bool_)
    for s in steps:
        apply_step(reactor, s)
    print(np.count_nonzero(reactor))
    pass
