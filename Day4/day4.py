def readinput(file):
    f = open(file, 'r')
    data = [x.rstrip() for x in f.readlines()]
    f.close()

    numbers = data.pop(0)
    boards = [data[i + 1:i + 6] for i in range(0, len(data), 6)]

    return [int(n) for n in numbers.split(',')], \
           [[[int(num) for num in row.split()] for row in board] for board in boards]


def find_winner(nums, n_map):
    for n in nums:
        num_locs = n_map[n]
        for b, r, c in num_locs:
            marked_boards[b][r][c] = True
            if all(marked_boards[b][r]) or all([marked_boards[b][j][c] for j in range(5)]):
                return b, r, c, n


def find_last_winner(nums, n_map, marked_boards):
    won_boards = set()
    for n in nums:
        num_locs = n_map[n]
        for b, r, c in num_locs:
            if b not in won_boards:
                marked_boards[b][r][c] = True
                if all(marked_boards[b][r]) or all([marked_boards[b][j][c] for j in range(5)]):
                    won_boards.add(b)
                if len(won_boards) == len(marked_boards):
                    return b, r, c, n


class NumMap(dict):

    def inject(self, key, value):
        if key in self:
            self[key].append(value)
        else:
            self[key] = [value]


def main():
    numbers, boards = readinput("inputs\inputD4.txt")
    marked_boards = [[[False] * 5 for _ in range(5)] for _ in range(len(boards))]
    num_map = NumMap()
    for b in range(len(boards)):
        for r in range(5):
            for c in range(5):
                num_map.inject(boards[b][r][c], (b, r, c))
    wb, wr, wc, n = find_last_winner(numbers, num_map, marked_boards)
    score = n * sum([boards[wb][ri][ci] for ri in range(5) for ci in range(5) if not marked_boards[wb][ri][ci]])
    print(score)


if __name__ == "__main__":
    main()
