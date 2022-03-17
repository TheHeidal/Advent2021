from collections import deque

from rtree import index

import day22input


class Prism:
    """
    A class for representing a rectangular prism of cubes in the reactor

    x is right, y is up, z is away
    """

    def __init__(self, x_min, x_max, y_min, y_max, z_min, z_max):
        self.x_min = int(x_min)
        self.x_max = int(x_max)
        self.y_min = int(y_min)
        self.y_max = int(y_max)
        self.z_min = int(z_min)
        self.z_max = int(z_max)

    @staticmethod
    def have_intersection(prism1, prism2):
        return all([(prism1.x_min <= prism2.x_min <= prism1.x_max) or (prism2.x_min <= prism1.x_min <= prism2.x_max),
                    (prism1.y_min <= prism2.y_min <= prism1.y_max) or (prism2.y_min <= prism1.y_min <= prism2.y_max),
                    (prism1.z_min <= prism2.z_min <= prism1.z_max) or (prism2.z_min <= prism1.z_min <= prism2.z_max)])

    @staticmethod
    def intersection(prism1, prism2):
        """Returns the prism that is in prism1 and prism2"""
        if prism1.have_intersection(prism1, prism2):
            return Prism(max(prism1.x_min, prism2.x_min), min(prism1.x_max, prism2.x_max),
                         max(prism1.y_min, prism2.y_min), min(prism1.y_max, prism2.y_max),
                         max(prism1.z_min, prism2.z_min), min(prism1.y_max, prism2.z_max))

    def difference(self, other):
        """
        Returns the prisms that make up self prism without intersecting with other
            cuts off x_min, then x_max, then y_min, then y_max, then z_min, then z_max
        """
        if not Prism.have_intersection(self, other):
            return [self]
        else:
            self_prisms = []
            if self.x_min < other.x_min:  # left
                self_prisms.append(Prism(self.x_min, other.x_min - 1,
                                         self.y_min, self.y_max,
                                         self.z_min, self.z_max))
            if other.x_max < self.x_max:  # right
                self_prisms.append(Prism(other.x_max + 1, self.x_max,
                                         self.y_min, self.y_max,
                                         self.z_min, self.z_max))
            if self.y_min < other.y_min:  # below (but not left or right)
                self_prisms.append(Prism(max(self.x_min, other.x_min), min(self.x_max, other.x_max),
                                         self.y_min, other.y_min - 1,
                                         self.z_min, self.z_max))
            if other.y_max < self.y_max:  # above (but not left or right)
                self_prisms.append(Prism(max(self.x_min, other.x_min), min(self.x_max, other.x_max),
                                         other.y_max + 1, self.y_max,
                                         self.z_min, self.z_max))
            if self.z_min < other.z_min:  # behind
                self_prisms.append(Prism(max(self.x_min, other.x_min), min(self.x_max, other.x_max),
                                         max(self.y_min, other.y_min), min(self.y_max, other.y_max),
                                         self.z_min, other.z_min - 1))
            if other.z_max < self.z_max:  # in front of
                self_prisms.append(Prism(max(self.x_min, other.x_min), min(self.x_max, other.x_max),
                                         max(self.y_min, other.y_min), min(self.y_max, other.y_max),
                                         other.z_max + 1, self.z_max))
            return self_prisms

    @property
    def index_bounds(self):
        return self.x_min, self.x_max, self.y_min, self.y_max, self.z_min, self.z_max

    @property
    def area(self):
        return ((self.x_max - self.x_min) + 1) * ((self.y_max - self.y_min) + 1) * ((self.z_max - self.z_min) + 1)

    @property
    def cubes(self):
        return [(a, b, c)
                for a in range(self.x_min, self.x_max + 1)
                for b in range(self.y_min, self.y_max + 1)
                for c in range(self.z_min, self.z_max + 1)]

    def __repr__(self):
        return (f"x={self.x_min}..{self.x_max},"
                f"y={self.y_min}..{self.y_max},"
                f"z={self.z_min}..{self.z_max}")


class Step:
    def __init__(self, state, x_min, x_max, y_min, y_max, z_min, z_max):
        self.state = state == 'on'
        self.prism = Prism(x_min, x_max, y_min, y_max, z_min, z_max)

    def __repr__(self):
        return f"{'on' if self.state else 'off'} {self.prism}"


class Reactor:
    def __init__(self):
        self.data = index.Index(properties=index.Property(dimension=3), interleaved=False)


def get_prisms():
    return [id_to_prism[i] for i in idx.leaves()[0][1]]


def get_area():
    return sum((id_to_prism[i].area for i in idx.leaves()[0][1]))


if __name__ == '__main__':
    steps = [Step(*s) for s in day22input.read_input('D22test2.txt')[:-2]]
    reactor = Reactor()
    idx = reactor.data
    id_gen = (x for x in range(1000000))
    id_to_prism = {}
    for step in steps:
        if step.state:
            # Find the set of prisms that do not intersect with an already existing prism and add them to the index
            intersecting_prism_ids = idx.intersection(step.prism.index_bounds)
            untrimmed_prisms = deque([step.prism])
            for intersecting_prism_id in intersecting_prism_ids:
                trimmed_prisms = deque()
                for ut_prism in untrimmed_prisms:
                    trimmed_prisms.extend(ut_prism.difference(id_to_prism[intersecting_prism_id]))
                untrimmed_prisms = trimmed_prisms
            for prism in untrimmed_prisms:
                prism_id = next(id_gen)
                id_to_prism[prism_id] = prism
                idx.insert(prism_id, prism.index_bounds)
        else:
            # find the prisms that do intersect with step, remove them from the index,
            # and insert back the sub-prisms that don't intersect
            intersecting_prism_ids = list(idx.intersection(step.prism.index_bounds))
            prisms_to_add = deque()
            for intersecting_prism_id in intersecting_prism_ids:
                prisms_to_add.extend(id_to_prism[intersecting_prism_id].difference(step.prism))
                idx.delete(intersecting_prism_id, id_to_prism[intersecting_prism_id].index_bounds)
            for prism in prisms_to_add:
                prism_id = next(id_gen)
                id_to_prism[prism_id] = prism
                idx.insert(prism_id, prism.index_bounds)
    print(get_area())
