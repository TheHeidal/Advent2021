from heapq import heappop, heappush

import numpy as np

from neighbors import neumann_neighbors


# for q2, 2886 is too high
# mike's answer 1 is 745

def heuristic(x, y):
    return max_x - x + max_y - y


def a_star(paths, risks):
    while True:
        _, curr_risk, curr_path = heappop(paths)
        curr_x, curr_y = curr_path[-1]
        for new_x, new_y in neumann_neighbors(curr_x, curr_y, max_x, max_y):
            if new_x == max_x and new_y == max_y:
                return curr_risk + risks[new_y][new_x]
            elif (new_x, new_y) not in curr_path:
                new_risk = curr_risk + risks[new_y][new_x]
                heappush(paths, (heuristic(new_x, new_y) + new_risk,
                                 new_risk,
                                 curr_path + [(new_x, new_y)]))


class Tile:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self._H = heuristic(x, y)
        self._parent = None

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

    @property
    def heuristic(self):
        return self._H

    @heuristic.setter
    def heuristic(self, value):
        self._H = value


def a_star_frontier(risks, end):
    open_heap = [(0, (0, 0))]
    closed_set = set()
    closed_set.add((0, 0))
    grid = [[Tile(x, y) for x in range(max_x + 1)] for y in range(max_y + 1)]
    last_len = 0

    while open_heap:
        if len(closed_set) % 1000 == 0 and len(closed_set) != last_len:
            last_len = len(closed_set)
            print(f"processed {len(closed_set)} tiles\n frontier has {len(open_heap)} options")

        curr_cost, current = heappop(open_heap)
        if current == end:
            return curr_cost
        for n_x, n_y in neumann_neighbors(current[0], current[1], max_x, max_y):
            if (n_x, n_y) not in closed_set:
                closed_set.add((n_x, n_y))
                grid[n_y][n_x].parent = current
                heappush(open_heap, ((risks[n_y][n_x] + curr_cost),
                                     (n_x, n_y)))


q2 = True

if __name__ == '__main__':
    filename = 'inputs/Day15/D15.txt'
    f = open(filename, 'r')
    risks = np.array([[int(c) for c in line.strip()] for line in f.readlines()], dtype=np.int8)
    f.close()
    if q2:
        risks_top = np.concatenate([risks + i for i in range(9)], axis=1)
        risks_full = np.concatenate([np.roll(risks_top, -len(risks) * i) for i in range(9)], axis=0) \
            [:len(risks) * 5, :len(risks[0]) * 5]
        mask = risks_full > 9
        risks = np.where(risks_full > 9, risks_full - 9, risks_full)
        if filename == 'inputs/D15test.txt':
            g = open('inputs/Day15/D15testbig.txt', 'r')
            test_array = np.array([[int(c) for c in line.strip()] for line in g.readlines()], dtype=np.int8)
            g.close()
            assert np.array_equal(risks, test_array)
    max_x = len(risks[0]) - 1
    max_y = len(risks) - 1
    res = a_star_frontier(risks, (max_x, max_y))
    print(res)
