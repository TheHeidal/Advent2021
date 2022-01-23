import logging
import multiprocessing as mp
import os
from collections import Counter
from collections import defaultdict as ddict
from queue import Empty
from datetime import datetime

logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)


def mtstr(): return ''


def zero(): return 0


def update(poly, ruledict):
    insertions = [ruledict[poly[i:i + 2]] for i in range(len(poly) - 1)]
    return "".join([insertions[i // 2] if i % 2 else poly[i // 2]
                    for i in range(len(poly) + len(insertions))])


def q1():
    for _ in range(STEPS):
        polymer = update(polymer, rules)
    for elem in polymer:
        count_dict[elem] += 1
    solution = count_dict[most_common(iter(count_dict), key=count_dict.get)] \
               - count_dict[least_common(iter(count_dict), key=count_dict.get)]
    print(solution)


def q2(poly, steps, rule_dict):
    start = datetime.now()
    cnt = Counter([i for i in poly])
    cnt_q = mp.Queue()
    q = mp.Queue()
    for pair in [(poly[i:i + 2], steps) for i in range(len(poly) - 1)]:
        q.put(pair)
    processes = [mp.Process(target=consume, args=(q, cnt_q, rule_dict)) for _ in range(4)]
    for p in processes:
        p.start()
    for p in processes:
        p.join()
    while not cnt_q.empty():
        cnt = cnt + cnt_q.get()
    elapsed = datetime.now() - start
    print(elapsed)
    return cnt


def consume(pair_queue, counter_queue, rule_dict):
    counter = Counter()
    logging.debug(f"{os.getpid()} started!")
    while not pair_queue.empty():
        try:
            pair, iter_c = pair_queue.get()
            logging.debug(f"{os.getpid()} working on {pair}, {iter_c}")
            if iter_c > 0:
                if pair in rule_dict:
                    counter[rule_dict[pair]] += 1
                    pair_queue.put((pair[0] + rule_dict[pair], iter_c - 1))
                    logging.debug(f"{os.getpid()} inserted {pair[0] + rule_dict[pair], iter_c - 1}")
                    pair_queue.put((rule_dict[pair] + pair[1], iter_c - 1))
                    logging.debug(f"{os.getpid()} inserted {rule_dict[pair] + pair[1], iter_c - 1}")
        except Empty:
            counter_queue.put(counter)
            logging.debug(f"{os.getpid()} finished")
            return
    counter_queue.put(counter)
    logging.debug(f"{os.getpid()} finished")
    return


if __name__ == '__main__':
    f = open('inputs/D14.txt', 'r')
    polymer = f.readline().strip()
    rules = ddict(mtstr, [x.strip().split(sep=' -> ') for x in f.readlines()[1:]])
    f.close()
    STEPS = 20
    count_dict = Counter()
    counts = q2(polymer, STEPS, rules)
    _, most_common = counts.most_common(1)[0]
    _, least_common = counts.most_common()[-1]
    solution = most_common - least_common
    print(solution)
