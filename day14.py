import logging
from collections import Counter
from collections import defaultdict as ddict

logging.basicConfig(filename='day14.log', encoding='utf-8', level=logging.DEBUG)


def mtstr(): return ''


def zero(): return 0


def cached_fn(poly, steps, rule_dict):
    # lookup_map steps is offset by one, so result of applying AB for 3 steps is lookup_map['AB'][2]
    lookup_map = ddict(Counter, {rule: [None for _ in range(steps)] for rule in rule_dict.keys()})
    for k in rule_dict.keys():
        lookup_map[k][0] = Counter(rule_dict[k])
    insertions = [(poly[i:i + 2], steps - 1) for i in range(len(poly) - 1)]
    cnt = Counter(poly)
    for c_i in [lookup(pair, steps, rule_dict, lookup_map) for pair, steps in insertions]:
        cnt.update(c_i)
    return cnt


def lookup(pair: str, steps: int, rules: dict, lookup_map: dict):
    logging.debug(f'looking up {pair}, {steps}')
    if pair not in rules:
        return Counter()
    if lookup_map[pair][steps] is None:
        logging.debug(f'having to calculate. inserting {rules[pair]}')
        lpair = lookup(pair[0] + rules[pair], steps - 1, rules, lookup_map)
        rpair = lookup(rules[pair] + pair[1], steps - 1, rules, lookup_map)
        lookup_map[pair][steps] = lpair + rpair + Counter(rules[pair])
    logging.debug(f'found {pair}, {steps} = {lookup_map[pair][steps]}')
    return lookup_map[pair][steps]


if __name__ == '__main__':
    f = open('inputs/D14.txt', 'r')
    polymer = f.readline().strip()
    rules = ddict(mtstr, [x.strip().split(sep=' -> ') for x in f.readlines()[1:]])
    f.close()
    STEPS = 40
    count_dict = Counter()
    logging.debug(f'\nstarting with polymer {polymer} for {STEPS} steps')
    counts = cached_fn(polymer, STEPS, rules)
    _, most_common = counts.most_common(1)[0]
    _, least_common = counts.most_common()[-1]
    solution = most_common - least_common
    print(solution)
