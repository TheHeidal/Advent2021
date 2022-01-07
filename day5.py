class Line:

    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.xdim = abs(x1 - x2)
        self.ydim = abs(y1 - y2)

    @property
    def xdir(self):
        if self.x1 < self.x2:
            return 1
        elif self.x1 == self.x2:
            return 0
        else:
            return -1

    @property
    def ydir(self):
        if self.y1 < self.y2:
            return 1
        elif self.y1 == self.y2:
            return 0
        else:
            return -1

    @property
    def same_x(self):
        return self.x1 == self.x2

    @property
    def same_y(self):
        return self.y1 == self.y2

    def __repr__(self):
        return f"{self.x1!r},{self.y1!r} -> {self.x2!r},{self.y2!r}"


def read_input(file):
    f = open(file, 'r')
    data = [x.rstrip() for x in f.readlines()]
    f.close()

    ret = []
    for a in data:
        b = a.split(" -> ")
        c1 = b[0].split(",")
        c2 = b[1].split(",")
        ret.append(Line(int(c1[0]), int(c1[1]), int(c2[0]), int(c2[1])))
    return ret


def main1():
    line_segments = read_input('inputs\inputD5.txt')
    v_h_lines = [l for l in line_segments if l.same_x or l.same_y]
    width = max([max(l.x1, l.x2) for l in v_h_lines]) + 1
    height = max([max(l.y1, l.y2) for l in v_h_lines]) + 1
    diagram = [[0] * height for _ in range(width)]  # access with diagram[x][y]
    check_hv(diagram, v_h_lines)
    print(len([p for col in diagram for p in col if p > 1]))


def check_hv(diagram, v_h_lines):
    for l in v_h_lines:
        if l.same_x:
            for y in range(min(l.y1, l.y2), max(l.y1, l.y2) + 1):
                diagram[l.x1][y] += 1
        if l.same_y:
            for x in range(min(l.x1, l.x2), max(l.x1, l.x2) + 1):
                diagram[x][l.y1] += 1


def main2():
    lines = read_input('inputs\inputD5.txt')
    width = max([max(l.x1, l.x2) for l in lines]) + 1
    height = max([max(l.y1, l.y2) for l in lines]) + 1
    diagram = [[0] * width for _ in range(height)]

    for l in lines:
        c_x = l.x1
        c_y = l.y1
        while c_x != l.x2 or c_y != l.y2:
            diagram[c_y][c_x] += 1
            c_x += l.xdir
            c_y += l.ydir
        diagram[c_y][c_x] += 1
    points = [p for col in diagram for p in col if p > 1]
    print(len(points))


if __name__ == '__main__':
    main1()
    main2()
