def firstmatching(lst, condition):
    """returns the index of the first element matching some condition"""
    pass


def decode(signals):
    signal_sets = [set(x) for x in signals.split()]
    cf = [x for x in signal_sets if len(x) == 2][0]
    A = [x for x in signal_sets if len(x) == 3][0] - cf
    len6 = [x for x in signal_sets if len(x) == 6]  #
    abfg = len6[0] & len6[1] & len6[2]
    F = cf.intersection(abfg)
    C = cf - F
    bd = [x for x in signal_sets if len(x) == 4][0] - cf
    B = abfg.intersection(bd)
    D = bd - B
    abcdefg = [x for x in signal_sets if len(x) == 7][0]
    cde = abcdefg - abfg
    E = cde - (C | D)
    G = abfg - (A | B | F)
    return {frozenset(cf): "1",
            frozenset(A | C | F): "7",
            frozenset(B | C | D | F): "4",
            frozenset(A | C | D | E | G): "2",
            frozenset(A | C | D | F | G): "3",
            frozenset(A | B | D | F | G): "5",
            frozenset(A | B | C | E | F | G): "0",
            frozenset(A | B | D | E | F | G): "6",
            frozenset(A | B | C | D | F | G): "9",
            frozenset(abcdefg): "8"}


def count_uniques():
    return len([x for display in displays for x in display if len(x) in [2, 3, 4, 7]])


if __name__ == "__main__":
    F = open("inputs/D8.txt")
    data = F.readlines()
    F.close()
    data = [x.split("|") for x in data]
    outputs = []
    for datum in data:
        decoder = decode(datum[0])
        outputs.append(int("".join([decoder[frozenset(x)] for x in datum[1].split()])))
    print(sum(outputs))
    # print(count_uniques())
