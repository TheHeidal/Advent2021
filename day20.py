import numpy as np


def read(filename):
    f = open(filename)
    algorithm = [c == '#' for c in f.readline().rstrip()]
    f.readline()
    image = [[c == '#' for c in x.strip()] for x in f.readlines()]
    return algorithm, image


class Image:

    def __init__(self, algorithm, data):
        self.algorithm = algorithm
        self.data = [np.array(data, dtype=np.bool_)]
        self.outside_cells = np.False_

    def update(self, updates=1):
        for _ in range(updates):
            new_array = [[self.calc_cell(x, y) for x in range(-1, self.data[-1].shape[0] + 1)] for y in
                         range(-1, self.data[-1].shape[1] + 1)]
            new_img = np.array(new_array)
            self.data.append(new_img)
            if self.outside_cells:
                self.outside_cells = self.algorithm[0b111111111]
            else:
                self.outside_cells = self.algorithm[0b000000000]

    def calc_cell(self, x, y):
        bools = [self.lookup(a, b) for a, b in (moore_neighborhood(x, y))]
        index = Image.bools_to_num(bools)
        return self.algorithm[index]

    def lookup(self, x, y):
        if (0 <= x < self.data[-1].shape[1]) and (0 <= y < self.data[-1].shape[0]):
            return self.data[-1][y][x]
        else:
            return self.outside_cells

    @staticmethod
    def bools_to_num(bools):
        """converts a list of bools to an integer, using the first bool as the most significant bit"""
        l = len(bools)
        return sum((2 ** ((l - 1) - i) if bools[i] else 0 for i in range(l)))


def present(img):
    for line in img:
        print(" ".join('#' if c else '.' for c in line))


def moore_neighborhood(x, y):
    """Given a set of x y coordinates, returns a list of coordinates in that cell's neighborhood (including that cell)"""
    return [(x + a, y + b) for b in range(-1, 2) for a in range(-1, 2)]


if __name__ == '__main__':
    alg, img = read('inputs/Day20/D20.txt')
    image = Image(alg, img)
    image.update(updates=50)
    print(np.sum(image.data[-1]))
