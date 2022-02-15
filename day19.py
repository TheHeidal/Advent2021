import logging
import re

import numpy as np

scanner_name = re.compile(r'--- scanner (\d+) ---')
beacon_coord = re.compile(r'(-?\d*),(-?\d*),(-?\d*)')

logging.basicConfig(filename='day19.log',
                    encoding='utf-8',
                    level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                    )


def read_input(filename):
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
            curr_ls.append(match_array(beacon_coord.match(line)))
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
        self.base_cloud = clouds[index]
        if index == 0:
            self.location = np.array([0, 0, 0])
            self.solved_cloud = clouds[index]
            self.rotation_i = IDENTITY_ROT_I
            self.isSolved = True
        else:
            self.location = None
            self.isSolved = False
            self.rotation_i = None
            self.solved_cloud = None

    def solve(self, solved_scanner_i, solved_beacon_i, self_beacon_i, rotation_i):
        self.isSolved = True
        self.rotation_i = rotation_i

        rotated_cloud = np.einsum('yx,zx->zy', ROTATIONS[rotation_i], self.base_cloud)
        s_beacon_coord = scn_dict[solved_scanner_i].solved_cloud[solved_beacon_i]
        offset = s_beacon_coord - rotated_cloud[self_beacon_i]
        self.solved_cloud = rotated_cloud + offset
        self.location = scn_dict[solved_scanner_i].location + offset
        logging.info(f"solved scanner {self.index}!")

    def __repr__(self):
        return f"scanner {self.index}"


R90 = {'x': np.array([[1, 0, 0],
                      [0, 0, 1],
                      [0, -1, 0]], int),
       'y': np.array([[0, 0, 1],
                      [0, 1, 0],
                      [-1, 0, 0]], int),
       'z': np.array([[0, 1, 0],
                      [-1, 0, 0],
                      [0, 0, 1]], int)}

xr = [np.identity(3, int), (R90['x']), R90['x'] @ R90['x'], R90['x'] @ R90['x'] @ R90['x']]
yr = [np.identity(3, int), (R90['y']), R90['y'] @ R90['y'], R90['y'] @ R90['y'] @ R90['y']]
zr = [np.identity(3, int), (R90['z']), R90['z'] @ R90['z'], R90['z'] @ R90['z'] @ R90['z']]

ROTATIONS = np.array([xr[x % 4] @ yr[y % 4] @ zr[z % 4]
                      for x, y in [(0, 0), (1, 0), (2, 0), (3, 0), (0, 1), (0, 3)] for z in range(4)])


# x is right, y is forwards, z is up. x and z follow left hand rule, y follows right (should probably fix that)

def find_matches():
    # pick a solved scanner
    # for each beacon b (until we are sure we must have tried one in the overlap cloud):
    #   get the coordinates of every beacon in the cloud relative to b (rebase onto b)
    #   for each scanner we haven't compared the solved scanner to (the comparison scanner)
    #       for each beacon c_b in the comparison scanner's cloud
    #           for each possible rotation r:
    #               rebase all beacons onto c_b
    #               rotate all beacons by r
    #               if the rebased clouds have at least 12 beacons in common, we know
    #                   - the comparison scanner can be corrected with rotation r
    #                   - b and cb are the same beacon
    #                   - true location of every beacon seen by comp_scanner is r@(beacon - cb) + origin beacon
    solved_scanners = [0]
    for solved_scanner_i in solved_scanners:
        while len(scn_dict[solved_scanner_i].uncompared):
            unsolved_scanner_i = scn_dict[solved_scanner_i].uncompared.pop()
            if not scn_dict[unsolved_scanner_i].isSolved:
                logging.debug(f'comparing scanner {solved_scanner_i:2} to scanner {unsolved_scanner_i:2}')
                res = match_scanners(solved_scanner_i, unsolved_scanner_i)
                scn_dict[solved_scanner_i].uncompared.discard(unsolved_scanner_i)
                scn_dict[unsolved_scanner_i].uncompared.discard(solved_scanner_i)
                if res is not None:
                    logging.debug(f'overlap found!')
                    s_beacon_i, u_beacon_i, rot_i = res
                    scn_dict[unsolved_scanner_i].solve(solved_scanner_i, s_beacon_i, u_beacon_i, rot_i)
                    solved_scanners.append(unsolved_scanner_i)
    return None


def match_scanners(s_scan_i, u_scan_i):
    """Given a solved and an unsolved scanner, find if they have overlapping detection cubes"""
    # for each beacon b (until we are sure we must have tried one in the overlap cloud):
    #   get the coordinates of every beacon in the cloud relative to b (rebase onto b)
    #   for each scanner we haven't compared the solved scanner to (the comparison scanner)
    #       for each beacon c_b in the comparison scanner's cloud
    #           for each possible rotation r:
    #               rebase all beacons onto c_b
    #               rotate all beacons by r
    #               if the rebased clouds have at least 12 beacons in common, we know
    #                   - the comparison scanner can be corrected with rotation r
    #                   - b and cb are the same beacon
    #                   - true location of every beacon seen by comp_scanner is r@(beacon - cb) + origin beacon
    rotated_uns_beacons = np.einsum('wyx,zx->wzy', ROTATIONS, scn_dict[u_scan_i].base_cloud)

    for s_beacon_i in range(len(scn_dict[s_scan_i].solved_cloud) - (OVERLAP_COUNT - 1)):
        # includes at least one scanner in the overlap cloud, if any exist
        rebased_s_beacons = scn_dict[s_scan_i].solved_cloud - scn_dict[s_scan_i].solved_cloud[s_beacon_i]
        s_view = rebased_s_beacons.view(view_dtype)

        for uns_beacon_i in range(len(scn_dict[u_scan_i].base_cloud)):
            rebased_uns_beacons = rotated_uns_beacons - rotated_uns_beacons[:, np.newaxis, uns_beacon_i]
            for rotation_i in range(len(ROTATIONS)):
                u_view = rebased_uns_beacons[rotation_i].view(view_dtype)
                matches, s_indices, c_indices = np.intersect1d(s_view, u_view, return_indices=True)
                if matches.size >= 12:
                    return s_beacon_i, uns_beacon_i, rotation_i


def count_beacons():
    beacons = np.vstack([scn_dict[i].solved_cloud for i in range(len(scanner_clouds))])
    b_set = np.unique(beacons, axis=0)
    return b_set.shape[0]


IDENTITY_ROT_I = 0
OVERLAP_COUNT = 12
view_dtype = {'names': ['f0', 'f1', 'f2'], 'formats': [int, int, int]}

test_case = 'inputs/D19test.txt'
real_case = 'inputs/D19.txt'

if __name__ == '__main__':
    scanner_clouds = read_input('inputs/D19test.txt')
    # scanner_clouds = read_input('inputs/D19.txt')
    scn_dict = {i: Scanner(i, scanner_clouds) for i in range(len(scanner_clouds))}  # comparison tracker

    find_matches()
    num_beacons = count_beacons()
    print(num_beacons)
    pass
