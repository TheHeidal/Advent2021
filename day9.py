from numpy import prod


def neighbors(x, y):
    return [(a, b) for a, b in [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
            if 0 <= a <= max_x and 0 <= b <= max_y]


def q1():
    low_points = [(x, y) for x in range(len(data[0])) for y in range(len(data))
                  if data[y][x] < min([data[y1][x1] for x1, y1 in neighbors(x, y)])]
    risk = sum([data[y][x] for x, y in low_points]) + len(low_points)
    print(risk)


def q2():
    unchecked = set([(x, y) for x in range(len(data[0])) for y in range(len(data))])
    basin_counter = -1
    basins = [[] for _ in range(10000)]  # 100 should be enough?
    to_check = []
    while len(unchecked) > 0:  # start a basin
        to_check.append(unchecked.pop())  # I do not like how I did this
        unchecked.add(to_check[0])
        basin_counter += 1
        while len(to_check) > 0:  # iterate through members of that basin
            curr = to_check.pop()
            if curr in unchecked and data[curr[1]][curr[0]] != 9:
                basins[basin_counter].append(curr)
                to_check.extend([n for n in neighbors(curr[0], curr[1]) if n in unchecked])
            unchecked.discard(curr)
    basinsizes = sorted([len(i) for i in basins], reverse=True)[0:3]
    print(basinsizes)
    print(prod(basinsizes))


# data is accessed data[y][x] but coords are stored (x,y)
if __name__ == "__main__":
    f = open("inputs/D9.txt", 'r')
    data = [[int(a) for a in b.strip()] for b in f.readlines()]
    f.close()
    max_y = len(data) - 1
    max_x = len(data[0]) - 1
    q2()
