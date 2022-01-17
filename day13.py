def fold(direction, location, array):
    location = int(location)
    if direction == 'y':
        len_covered = min(location, len(array) - 1 - location)
        len_uncovered = location - len_covered
        new_array = [[] for _ in range(location)]
        for r_i in range(len_uncovered):
            new_array[r_i] = array[r_i][:]
        for r_i in range(1, len_covered + 1):
            new_array[location - r_i] = [array[location - r_i][c] or array[location + r_i][c] for c in
                                         range(len(array[0]))]
        return new_array
    if direction == 'x':
        len_covered = min(location, len(array[0]) - location)
        len_uncovered = location - len_covered
        new_array = [[False for _ in range(location)] for _ in range(len(array))]
        for r_i in range(len(array)):
            for c_i in range(len_uncovered):
                new_array[r_i][c_i] = array[r_i][c_i]
        for r_i in range(len(array)):
            for i in range(1, len_covered + 1):
                new_array[r_i][location - i] = array[r_i][location - i] or array[r_i][location + i]
        return new_array


if __name__ == '__main__':
    f = open('inputs/D13.txt')
    data = [line.strip() for line in f.readlines()]
    f.close()
    mtline = data.index("")
    folds = [inst.lstrip("fold along").split('=') for inst in data[mtline + 1:]]
    dots = [[int(n) for n in pair.split(",")] for pair in data[:mtline]]
    max_x = max((pair[0] for pair in dots))
    max_y = max((pair[1] for pair in dots))
    paper = [[False for _ in range(max_x + 1)] for _ in range(max_y + 1)]
    for x, y in dots:
        paper[y][x] = True
    new_paper = [line[:] for line in paper]
    for direction, loc in folds:
        new_paper = fold(direction, loc, new_paper)
    for row in new_paper:
        print("".join('#' if c else ' ' for c in row))
    # question 1
    count = [x for row in new_paper for x in row].count(True)
    print(count)
