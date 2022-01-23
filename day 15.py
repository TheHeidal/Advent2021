from heapq import heapify, heappop, heappush
from queue import PriorityQueue

from neighbors import neumann_neighbors


def heuristic(x, y):
    return max_x - x + max_y - y


def a_star(paths, risks):
    while True:
        _, curr_risk, curr_path = heappop(paths)
        if len(paths) % 100 == 0:
            print(curr_path)
        curr_x, curr_y = curr_path[-1]
        for new_x, new_y in neumann_neighbors(curr_x, curr_y, max_x, max_y):
            if new_x == max_x and new_y == max_y:
                return curr_risk + risks[new_y][new_x]
            elif (new_x, new_y) not in curr_path:
                new_risk = curr_risk + risks[new_y][new_x]
                heappush(paths, (heuristic(new_x, new_y) + new_risk,
                                 new_risk,
                                 curr_path + [(new_x, new_y)]))


if __name__ == '__main__':
    f = open('inputs/D15.txt', 'r')
    risks = [[int(c) for c in line.strip()] for line in f.readlines()]
    f.close()
    max_x = len(risks[0]) - 1
    max_y = len(risks) - 1
    queue = PriorityQueue()
    queue.put((heuristic(0, 0), 0, [(0, 0)]))

    paths = [(heuristic(0, 0), 0, [(0, 0)])]  # estimated risk, actual risk, path so far
    heapify(paths)
    lowest_risk = a_star(paths, risks)
    print(lowest_risk)
