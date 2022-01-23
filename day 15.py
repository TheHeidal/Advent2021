import multiprocessing as mp
from heapq import heappop, heappush
from multiprocessing.queues import

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


def a_star_consumer(paths: PriorityQueue, risks: list, answer_queue):
    while answer_queue.empty() and not paths.empty():
        try:
            _, curr_risk, curr_path = paths.get()
            curr_x, curr_y = curr_path[-1]
            for new_x, new_y in neumann_neighbors(curr_x, curr_y, max_x, max_y):
                if new_x == max_x and new_y == max_y:
                    answer_queue.put(curr_risk + risks[new_y][new_x])
                    return
                elif (new_x, new_y) not in curr_path:
                    new_risk = curr_risk + risks[new_y][new_x]
                    paths.put((heuristic(new_x, new_y) + new_risk,
                               new_risk,
                               curr_path + [(new_x, new_y)]))
        except Empty:
            return


if __name__ == '__main__':
    f = open('inputs/D15test.txt', 'r')
    risks = [[int(c) for c in line.strip()] for line in f.readlines()]
    f.close()
    max_x = len(risks[0]) - 1
    max_y = len(risks) - 1
    path_q = PriorityQueue()
    path_q.put((heuristic(0, 0), 0, [(0, 0)]))
    answer_q = PriorityQueue()

    processes = [mp.Process(target=a_star_consumer, args=(path_q, risks, answer_q))]
    for p in processes:
        p.start()
    for p in processes:
        p.join()
    lowest_risk = answer_q.get()
    print(lowest_risk)

    # with mp.Pool(processes=4, initializer=a_star_consumer, initargs=(path_q, risks, answer_q,)) as pool:
    #     pool.close()
    # pool.terminate()
    # pool.join()

    # processes = [mp.Process(target=a_star_consumer, args=(queue, risks)) for _ in range(4)]
    # paths = [(heuristic(0, 0), 0, [(0, 0)])]  # estimated risk, actual risk, path so far
    # heapify(paths)
    # lowest_risk = a_star(paths, risks)
    # print(lowest_risk)
