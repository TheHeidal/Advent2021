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
    scanner_name = re.compile(r'--- scanner (\d+) ---')
    beacon_coord = re.compile(r'(-?\d*),(-?\d*),(-?\d*)')

    logging.info(f'reading {filename}')
    file = open(filename, 'r')
    scanner_lists = []
    for line in file:
        match_scanner = scanner_name.match(line)
        if match_scanner:
            curr_ls = []
            curr_scanner = int(match_scanner.group(1))
        elif line == '\n':
            scanner_lists.append(np.array(curr_ls))
        else:
            obj = beacon_coord.match(line)
            curr_ls.append([int(obj.group(1)), int(obj.group(2)), int(obj.group(3))])
    file.close()
    return scanner_lists


def match_array(match_obj):
    """Translate a match object into a list"""
    return [int(match_obj.group(1)),
            int(match_obj.group(2)),
            int(match_obj.group(3))]


class Scanner:
    def __init__(self, index, clouds):
        self.index = index  # index of the scanner's cloud in scanner_clouds
        self.uncompared = set(range(len(clouds))) - {index}
        self.u_cloud = clouds[index]
        if index == 0:
            self.location = np.array([0, 0, 0])
            self.s_cloud = clouds[index]
            self.rotation_i = IDENTITY_ROT_I
            self.isSolved = True
        else:
            self.isSolved = False
            self.location = None
            self.solved_from = None
            self.rotation_i = None
            self.s_cloud = None

    def solve(self, s_scanner_i, solved_beacon_i, self_beacon_i, rotation_i):
        self.isSolved = True
        self.solved_from = s_scanner_i
        self.rotation_i = rotation_i

        rotated_cloud = np.einsum('yx,zx->zy', ROTATIONS[rotation_i], self.u_cloud)
        s_beacon_coord = scn_dict[s_scanner_i].s_cloud[solved_beacon_i]
        offset = s_beacon_coord - rotated_cloud[self_beacon_i]
        self.s_cloud = rotated_cloud + offset
        self.location = scn_dict[s_scanner_i].location + offset
        logging.info(f"solved scanner {self.index}!")

    def __repr__(self):
        return f"scanner {self.index}"


x90 = np.array([[1, 0, 0],
                [0, 0, -1],
                [0, 1, 0]], dtype=np.int32)
y90 = np.array([[0, 0, 1],
                [0, 1, 0],
                [-1, 0, 0]], dtype=np.int32)
z90 = np.array([[0, -1, 0],
                [1, 0, 0],
                [0, 0, 1]], dtype=np.int32)

# assume scanner starts facing positive x
pos_x = [np.identity(3, dtype=np.int32), x90, x90 @ x90, x90 @ x90 @ x90]
neg_x = [z90 @ z90 @ xr for xr in pos_x]
pos_y = [z90 @ yr for yr in [np.identity(3, dtype=np.int32), y90, y90 @ y90, y90 @ y90 @ y90]]
neg_y = [z90 @ z90 @ z90 @ yr for yr in [np.identity(3, dtype=np.int32), y90, y90 @ y90, y90 @ y90 @ y90]]
pos_z = [y90 @ zr for zr in [np.identity(3, dtype=np.int32), z90, z90 @ z90, z90 @ z90 @ z90]]
neg_z = [y90 @ y90 @ y90 @ zr for zr in [np.identity(3, dtype=np.int32), z90, z90 @ z90, z90 @ z90 @ z90]]

# probably should convert to enumeration
ROTATIONS = np.concatenate([pos_x, neg_x, pos_y, neg_y, pos_z, neg_z])

IDENTITY_ROT_I = 0
OVERLAP_COUNT = 12
NECESSARY_OVERLAP = (OVERLAP_COUNT * (OVERLAP_COUNT - 1)) // 2
view_dtype = {'names': ['x', 'y', 'z'], 'formats': [int, int, int]}


class ScannerDist:
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
            self.s_cloud = None
            self.offset = None

    def solve(self, rotation_i, offset):
        self.rotation = rotation_i
        einsum = np.einsum('ab,vb->va', ROTATIONS[rotation_i], scan_lst[u_scan_i].cloud)
        self.s_cloud = einsum + offset
        x = np.intersect1d(scan_lst[self.index].s_cloud.view(view_dtype),
                           scan_lst[s_scan_i].s_cloud.view(view_dtype))

    def __repr__(self):
        return f"Distance Scanner {self.index}"


def find_rotation(dist, s_i, u_i):
    vec_solved = scan_lst[s_i].dist_to_pair[dist][2]
    vec_unsolved = scan_lst[u_i].dist_to_pair[dist][2]
    rotated_vectors = np.einsum('wvc,c->wv', ROTATIONS, vec_unsolved)
    _, isFlipped, rot_i = np.intersect1d((vec_solved * np.array([1, -1])[:, np.newaxis]).view(view_dtype),
                                         rotated_vectors.view(view_dtype),
                                         return_indices=True)
    return rot_i, isFlipped


def find_offset(dist, rot, flipped, s_i, u_i):
    s_beacon_i = scan_lst[s_i].dist_to_pair[dist][0]
    u_beacon_i = scan_lst[u_i].dist_to_pair[dist][flipped]

    offset = np.einsum('vc,c->v', ROTATIONS[rot], scan_lst[u_i].cloud[u_beacon_i]) - scan_lst[s_i].s_cloud[
        s_beacon_i]
    return offset


def match_beacons(dist, scanner_i0, scanner_i1, scanner_list):
    """Returns a pair of pairs of matched beacons (scanner_i0, scanner_i1)"""

    scanner_0 = scanner_list[scanner_i0]
    scanner_1 = scanner_list[scanner_i1]
    s0b0, s0b1, _ = scanner_0.dist_to_pair[dist]
    s1b0, s1b1, _ = scanner_1.dist_to_pair[dist]

    def are_same_beacon(b1, b2):
        return len(scanner_0.beacon_to_dists[b1] & scanner_1.beacon_to_dists[b2]) >= OVERLAP_COUNT - 1

    if are_same_beacon(s0b0, s1b0):
        return (s0b0, s0b1), (s1b0, s1b1)
    elif are_same_beacon(s0b0, s1b1):
        return (s0b0, s0b1,), (s1b1, s1b0)


if __name__ == '__main__':
    scanner_clouds = read_input('inputs/D19test.txt')
    # scanner_clouds = read_input('inputs/D19.txt')

    scan_lst = [ScannerDist(i, scanner_clouds[i]) for i in range(len(scanner_clouds))]

    scanner_queue = deque()
    scanner_queue.append(0)
    u_scanners_set = {i for i in range(1, len(scan_lst))}

    while scanner_queue:
        s_scan_i = scanner_queue.pop()
        s_scanner = scan_lst[s_scan_i]
        newly_solved = set()
        for u_scan_i in u_scanners_set:
            u_scanner = scan_lst[u_scan_i]
            logging.debug(f"attempting to solve {u_scanner} with {s_scanner}")
            dist_intersect = s_scanner.dist_to_pair.keys() & u_scanner.dist_to_pair.keys()
            if len(dist_intersect) >= NECESSARY_OVERLAP:
                logging.debug(f"overlap found")
                for shared_dist in dist_intersect:
                    break
                s_beacons, u_beacons = match_beacons(shared_dist, s_scan_i, u_scan_i, scan_lst)
                s_vector = s_scanner.s_cloud[s_beacons[0]] - s_scanner.s_cloud[s_beacons[1]]
                assert 0 not in s_vector
                u_vector = u_scanner.cloud[u_beacons[0]] - u_scanner.cloud[u_beacons[1]]
                assert 0 not in u_vector
                rotation = np.array(
                    [[1 if s_vector[s] == u_vector[u] else (-1 if s_vector[s] == -u_vector[u] else 0) for s in range(3)]
                     for u in range(3)])
                offset = s_scanner.s_cloud[s_beacons[0]] - (u_scanner.cloud[u_beacons[0]] @ rotation)
                u_scanner.s_cloud = np.einsum("bc,rc->br", u_scanner.cloud, rotation) + offset
                assert OVERLAP_COUNT <= len(np.intersect1d(s_scanner.s_cloud.view(view_dtype),
                                                           u_scanner.s_cloud.view(view_dtype)))
                u_scanner.offset = offset
                newly_solved.add(u_scan_i)
        scanner_queue.extend(newly_solved)
        u_scanners_set.difference_update(newly_solved)
    assert not u_scanners_set
    for s in scan_lst:
        print(s.offset)
    num_beacons = np.unique(np.vstack([s.s_cloud for s in scan_lst]).view(view_dtype))
    print(len(num_beacons))
