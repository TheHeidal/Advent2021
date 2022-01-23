def moore_neighbors(x, y, max_x, max_y):
    return [(a, b) for a, b in [(x - 1, y - 1), (x, y - 1), (x + 1, y - 1),
                                (x + 1, y), (x - 1, y),
                                (x - 1, y + 1), (x, y + 1), (x + 1, y + 1)]
            if 0 <= a <= max_x and 0 <= b <= max_y]


def neumann_neighbors(x, y, max_x, max_y):
    return [(a, b) for a, b in [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
            if 0 <= a <= max_x and 0 <= b <= max_y]
