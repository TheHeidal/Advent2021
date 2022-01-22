import multiprocessing as mp
from collections import Counter
from collections import defaultdict as ddict
from queue import Empty


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


def q2(poly, steps):
    cnt_0 = Counter([i for i in poly])
    cnts = [Counter() for _ in range(3)]
    q = mp.Queue()
    for pair in [(poly[i:i + 2], steps) for i in range(len(poly) - 1)]:
        q.put(pair)
    processes = [mp.Process(target=consume, args=(q, cnts[j])) for j in range(3)]
    for p in processes:
        p.start()
    for p in processes:
        p.join()
    return cnt_0 + cnts[0] + cnts[1] + cnts[2]


def consume(queue, counter):
    while queue.full():
        try:
            pair, iter_c = queue.get()
            if iter_c > 0:
                if pair in rules:
                    counter[rules[pair]] += 1
                    queue.append((pair[0] + rules[pair], iter_c - 1))
                    queue.append((rules[pair] + pair[1], iter_c - 1))
            queue.task_done()
        except Empty:
            return


if __name__ == '__main__':
    f = open('inputs/D14test.txt', 'r')
    polymer = f.readline().strip()
    rules = ddict(mtstr, [x.strip().split(sep=' -> ') for x in f.readlines()[1:]])
    f.close()
    STEPS = 10
    count_dict = Counter()
    counts = q2(polymer, STEPS)
    _, most_common = counts.most_common(1)[0]
    _, least_common = counts.most_common()[-1]
    solution = most_common - least_common
    print(solution)
