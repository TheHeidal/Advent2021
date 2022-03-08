MAX_ENERGY = 9
STEPS = 1000


def neighbors(x, y):
    return [(a, b) for a, b in [(x - 1, y - 1), (x, y - 1), (x + 1, y - 1),
                                (x + 1, y), (x - 1, y),
                                (x - 1, y + 1), (x, y + 1), (x + 1, y + 1)]
            if 0 <= a <= max_x and 0 <= b <= max_y]


def q1(array):
    """takes a data array, returns a pair of new array and number of flashes"""
    flashed = [[False for _ in range(len(data[0]))] for _ in array]
    to_update = []
    flash_counter = 0
    updated_data = [[None for _ in range(max_x + 1)] for _ in range(max_y + 1)]
    for y in range(max_y + 1):
        for x in range(max_x + 1):
            updated_data[y][x] = array[y][x] + 1
            if updated_data[y][x] > MAX_ENERGY and not flashed[y][x]:
                flash_counter += 1
                flashed[y][x] = True
                to_update.extend(neighbors(x, y))
    while len(to_update) > 0:
        x, y = to_update.pop()
        updated_data[y][x] += 1
        if updated_data[y][x] > MAX_ENERGY and not flashed[y][x]:
            flash_counter += 1
            flashed[y][x] = True
            to_update.extend(neighbors(x, y))
    updated_data = [[0 if x > MAX_ENERGY else x for x in l] for l in updated_data]
    all_flashed = all([all(row) for row in flashed])
    return updated_data, flash_counter, all_flashed


def iterate1(array):
    score = 0
    new_data, new_score, all_flashed = q1(array)
    score += new_score
    for _ in range(STEPS - 1):
        new_data, new_score, all_flashed = q1(new_data)
        score += new_score
    return score


def iterate2(array):
    step_counter = 1
    new_data, _, all_flashed = q1(array)
    if all_flashed:
        return step_counter
    for _ in range(STEPS - 1):
        new_data, _, all_flashed = q1(new_data)
        step_counter += 1
        if all_flashed:
            return step_counter
    return None


# data is accessed data[y][x] but coords are stored (x,y)
if __name__ == '__main__':
    f = open("D11.txt")
    data = [[int(c) for c in l.strip()] for l in f.readlines()]
    f.close()
    max_x = len(data[0]) - 1
    max_y = len(data) - 1
    # print(iterate1(data))
    print(iterate2(data))
