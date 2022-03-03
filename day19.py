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
            self.s_cloud = self.cloud
            self.offset = np.zeros(3, dtype=np.int32)
        else:
            self.parent = None
            self.rotation = None
            self.offset = None
            self.s_cloud = None

    def solve(self, new_parent, new_rotation, new_offset):
        assert self.parent is None
        self.parent = new_parent
        self.rotation = new_rotation
        self.offset = new_offset
        parent_cloud_view = self.parent.cloud.view(view_dtype)
        offset_view = (rotate_vectors(self.cloud, u_scanner.rotation) + new_offset).view(view_dtype)
        intersect_d = np.intersect1d(parent_cloud_view, offset_view)
        assert OVERLAP_COUNT <= len(intersect_d)

    def __repr__(self):
        return f"Scanner {self.index}"


def match_beacons(scanner_x, scanner_y):
    shared_dists = scanner_x.dist_to_pair.keys() & scanner_y.dist_to_pair.keys()
    if len(shared_dists) >= MIN_OVERLAP:
        logging.debug(f"overlap found btw s {scanner_x.index} and s {scanner_y.index}")
        for dist in shared_dists:
            sx_b0, sx_b1, _ = scanner_x.dist_to_pair[dist]
            sy_b0, sy_b1, _ = scanner_y.dist_to_pair[dist]

            def are_same_beacon(b1, b2):
                return len(scanner_x.beacon_to_dists[b1] & scanner_y.beacon_to_dists[b2]) >= OVERLAP_COUNT - 1

            if are_same_beacon(sx_b0, sy_b0):
                return (sx_b0, sx_b1), (sy_b0, sy_b1)
            elif are_same_beacon(sx_b0, sy_b1):
                return (sx_b0, sx_b1,), (sy_b1, sy_b0)
        return None
    else:
        return None


def rotate_vectors(vectors, rotation_matrix):
    return np.einsum("bc,rc->br", vectors, rotation_matrix)


if __name__ == '__main__':
    scanner_clouds = read_input('inputs/D19test.txt')
    # scanner_clouds = read_input('inputs/D19.txt')

    scan_lst = [Scanner(i, scanner_clouds[i]) for i in range(len(scanner_clouds))]

    scanner_queue = deque([0])
    u_scanners_set = set(range(len(scan_lst))) - {0}

    while scanner_queue:
        s_scan_i = scanner_queue.pop()
        parent = scan_lst[s_scan_i]
        newly_solved = set()
        for u_scan_i in u_scanners_set:
            u_scanner = scan_lst[u_scan_i]
            logging.debug(f"attempting to solve {u_scanner} with {parent}")
            matched_beacons = match_beacons(parent, u_scanner)
            if matched_beacons is not None:
                s_beacons, u_beacons = matched_beacons
                s_vector = parent.cloud[s_beacons[0]] - parent.cloud[s_beacons[1]]
                u_vector = u_scanner.cloud[u_beacons[0]] - u_scanner.cloud[u_beacons[1]]
                assert 0 not in s_vector
                assert 0 not in u_vector

                rotation = np.array(
                    [[1 if s_vector[s] == u_vector[u] else (-1 if s_vector[s] == -u_vector[u] else 0) for s in range(3)]
                     for u in range(3)], dtype=np.int32)
                assert np.array_equal(u_vector @ rotation, s_vector)

                offset = parent.cloud[s_beacons[0]] - (u_scanner.cloud[u_beacons[0]] @ rotation)
                assert np.array_equal(parent.cloud[s_beacons[1]], u_scanner.cloud[u_beacons[1]] @ rotation + offset)

                u_scanner.solve(parent, rotation, offset)


                newly_solved.add(u_scan_i)
                scanner_queue.extend(newly_solved)
        u_scanners_set.difference_update(newly_solved)
    assert not u_scanners_set
    for s in scan_lst:
        print(s.offset)
        num_beacons = np.unique(np.vstack([s.s_cloud for s in scan_lst]).view(view_dtype))
        print(len(num_beacons))
