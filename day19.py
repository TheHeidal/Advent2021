import logging
import re
from collections import deque, defaultdict

import numpy as np

logging.basicConfig(filename='day19.log',
                    encoding='utf-8',
                    level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                    )


def read_input(filename):
    """Parses input files and returns a list of np arrays of beacon locations"""
    scanner_name = re.compile(r"--- scanner (\d+) ---")
    beacon_coord = re.compile(r'(-?\d*),(-?\d*),(-?\d*)')

    logging.info(f'reading {filename}')
    file = open(filename, 'r')
    scanner_lists = []
    for line in file:
        match_scanner = scanner_name.match(line)
        if match_scanner:
            curr_ls = []
        elif line == '\n':
            scanner_lists.append(np.array(curr_ls))
        else:
            b_match = beacon_coord.match(line)
            curr_ls.append([int(b_match.group(1)), int(b_match.group(2)), int(b_match.group(3))])
    file.close()
    return scanner_lists


OVERLAP_COUNT = 12
MIN_OVERLAP = (OVERLAP_COUNT * (OVERLAP_COUNT - 1)) // 2
view_dtype = {'names': ['x', 'y', 'z'], 'formats': [int, int, int]}


class Scanner:
    """A scanner that stores pairs of beacons by their distance

    Attributes:
        index (int): the scanner's index in the list of scanners
        cloud (np.array): the beacons the scanner can see from its own perspective, stored as rows
        dist_to_pair (dict[int, (int, int, int)]): given a distance, returns the indices of the two beacons seen by the scanner with that distance between them
        beacon_to_dists (dict[int, set[int]]): given the index of a beacon, returns the set of distances between that beacon and all others in the cloud
        s_cloud (np.array): the beacons the scanner can see from the perspective of scanner 0. Matches indices with cloud
        rotation (int): the index of the rotation that rotates this beacon's perspective to match scanner 0
        offset (np.array): the 3-component vector from this scanner to scanner 0
    """

    def __init__(self, index, cloud):
        self.index = index
        self.cloud = cloud
        self.dist_to_pair = dict()
        self.beacon_to_dists = defaultdict(set)
        for beacon_i in range(len(cloud)):
            for beacon_j in range(beacon_i + 1, len(cloud)):
                vector = cloud[beacon_i] - cloud[beacon_j]
                dist = sum(vector ** 2)
                if dist not in self.dist_to_pair:
                    self.dist_to_pair[dist] = (beacon_i, beacon_j, vector)
                    self.beacon_to_dists[beacon_i].add(dist)
                    self.beacon_to_dists[beacon_j].add(dist)
                else:
                    raise KeyError("distance collision on scanner {} btw pairs ({}, {}) and {}".format(
                        self.index, beacon_i,
                        beacon_j,
                        self.dist_to_pair[dist][0:2]))
        if 0 == self.index:
            self.offset = np.zeros(3, dtype=np.int32)
        else:
            self.parent = None
            self.rotation = None
            self.offset = None

    def solve(self, new_parent, new_rotation, new_offset):
        assert self.parent is None
        self.parent = new_parent
        self.rotation = new_rotation
        self.offset = new_offset
        parent_cloud_view = self.parent.cloud.view(view_dtype)
        offset_view = (rotate_vectors(self.cloud, self.rotation) + self.offset).view(view_dtype)
        intersect_d = np.intersect1d(parent_cloud_view, offset_view)
        # assert OVERLAP_COUNT <= len(intersect_d)
        assert len(intersect_d)

    def s_cloud(self):
        curr_scanner = self
        curr_cloud = self.cloud
        while curr_scanner.index != 0:
            curr_cloud = rotate_vectors(curr_cloud, curr_scanner.rotation) + curr_scanner.offset
            curr_scanner = curr_scanner.parent
        return curr_cloud

    def s_location(self):
        curr_scanner = self
        curr_offset = np.zeros(3)
        while curr_scanner.index != 0:
            curr_offset = rotate_vectors(curr_offset) + curr_scanner.offset
            curr_scanner = curr_scanner.parent
        return curr_offset

    def solved(self):
        if self.index == 0:
            return True
        else:
            return self.parent.solved()

    def __repr__(self):
        return f"Scanner {self.index}"


def match_beacons(scanner_x, scanner_y):
    shared_dists = scanner_x.dist_to_pair.keys() & scanner_y.dist_to_pair.keys()
    # if len(shared_dists) >= MIN_OVERLAP:
    if len(shared_dists) > 3:
        for dist in shared_dists:
            break
        key_x_beacon = scanner_x.dist_to_pair[dist][0]
        key_x_beacon_shared_dists = scanner_x.beacon_to_dists[key_x_beacon] & shared_dists
        dist_iter = iter(key_x_beacon_shared_dists)
        key_y_beacon = (set(scanner_y.dist_to_pair[next(dist_iter)][:2])
                        & set(scanner_y.dist_to_pair[next(dist_iter)][:2])).pop()
        # now we know scanner_x_beacon_a and scanner_y_beacon_a are the same beacon.
        x_beacon_to_y_beacon = {key_x_beacon: key_y_beacon}

        for dist in key_x_beacon_shared_dists:
            x_beacon = (set(scanner_x.dist_to_pair[dist][:2]) - {key_x_beacon}).pop()
            y_beacon = (set(scanner_y.dist_to_pair[dist][:2]) - {key_y_beacon}).pop()
            x_beacon_to_y_beacon[x_beacon] = y_beacon
        return x_beacon_to_y_beacon
    return dict()


def rotate_vectors(vectors, rotation_matrix):
    return np.einsum("vj,jh->vh", vectors, rotation_matrix)


def solve_scanners(scanner_lst, solved=0):
    scanner_queue = deque([solved])
    u_scanners_set = set(range(len(scanner_lst))) - {solved}

    while scanner_queue:
        s_scan_i = scanner_queue.pop()
        s_scanner = scanner_lst[s_scan_i]
        newly_solved = set()
        for u_scan_i in u_scanners_set:
            u_scanner = scanner_lst[u_scan_i]
            logging.debug(f"attempting to solve {u_scanner} with {s_scanner}")
            s_beacon_to_u_beacon = match_beacons(s_scanner, u_scanner)
            if s_beacon_to_u_beacon:
                logging.debug(f"overlap between {u_scanner} and {s_scanner}")
                beacons_and_vectors = find_vectors(s_beacon_to_u_beacon, s_scanner, u_scanner)
                if beacons_and_vectors is not None:
                    s_beacons, s_vector, u_beacons, u_vector = beacons_and_vectors
                    rotation = find_rotation(s_vector, u_vector)
                    assert np.array_equal(u_vector @ rotation, s_vector)

                    offset = s_scanner.cloud[s_beacons[0]] - (u_scanner.cloud[u_beacons[0]] @ rotation)
                    assert np.array_equal(s_scanner.cloud[s_beacons[1]],
                                          (u_scanner.cloud[u_beacons[1]] @ rotation) + offset)

                    u_scanner.solve(s_scanner, rotation, offset)

                    newly_solved.add(u_scan_i)
                    scanner_queue.extend(newly_solved)
        u_scanners_set.difference_update(newly_solved)
    assert not u_scanners_set
    beacon_list = np.vstack([s.s_cloud() for s in scanner_lst])
    unique_beacons = np.unique(beacon_list.view(view_dtype))
    print(len(unique_beacons))
    beacon_locations = [s.s_location for s in scanner_lst]


def find_vectors(s_beacon_to_u_beacon, s_scanner, u_scanner):
    for b0 in iter(s_beacon_to_u_beacon):
        for b1 in iter(s_beacon_to_u_beacon):
            if b0 != b1:
                s_beacons = [b0, b1]
                u_beacons = [s_beacon_to_u_beacon[s] for s in s_beacons]
                s_vector = s_scanner.cloud[s_beacons[0]] - s_scanner.cloud[s_beacons[1]]
                u_vector = u_scanner.cloud[u_beacons[0]] - u_scanner.cloud[u_beacons[1]]
                if 0 not in s_vector and 0 not in u_vector:
                    if len(np.unique(np.abs(s_vector))) == len(np.unique(np.abs(u_vector))) == 3:
                        return s_beacons, s_vector, u_beacons, u_vector
    return None


def find_rotation(s_vector, u_vector):
    return np.array(
        [[1 if s_vector[s] == u_vector[u] else (-1 if s_vector[s] == -u_vector[u] else 0) for s in range(3)]
         for u in range(3)], dtype=np.int32)


if __name__ == '__main__':
    # scanner_clouds = read_input('inputs/D19test.txt')
    scanner_clouds = read_input('inputs/D19.txt')

    scan_lst = [Scanner(i, scanner_clouds[i]) for i in range(len(scanner_clouds))]

    solve_scanners(scan_lst)
