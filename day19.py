import re

import numpy as np

scanner_name = re.compile('--- scanner (\d+) ---')
beacon_coord = re.compile('(-?\d*),(-?\d*),(-?\d*)')


# class Beacon:
#
#     def __init__(self, match_obj, scanner_num):
#         self.scanner_num = scanner_num
#         self.a = int(match_obj.group(1))
#         self.b = int(match_obj.group(2))
#         self.c = int(match_obj.group(3))
#
#     def dist(self, other):
#         if self.scanner_num == other.scanner_num:
#             return (abs(self.a - other.a),
#                     abs(self.b - other.b),
#                     abs(self.c - other.c))
#         else:
#             raise NotImplementedError
#
#     def __repr__(self):
#         return f'({self.scanner_num}: {self.a}, {self.b}, {self.c})'


def read_input(filename):
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


def rx(theta):
    """Return a rotation matrix that rotates a vector about the x axis by theta degrees"""
    return np.array([[1, 0, 0],
                     [0, np.cos(theta), -np.sin(theta)],
                     [0, np.sin(theta), np.cos(theta)]])


def ry(theta):
    """Return a rotation matrix that rotates a vector about the y axis by theta degrees"""
    return np.array([[np.cos(theta), 0, np.sin(theta)],
                     [0, 1, 0],
                     [-np.sin(theta), 0, np.cos(theta)]])


def rz(theta):
    """Return a rotation matrix that rotates a vector about the z axis by theta degrees"""
    return np.array([[np.cos(theta), -np.sin(theta), 0],
                     [np.sin(theta), np.cos(theta), 0],
                     [0, 0, 1]])


class Scanner:
    def __init__(self, index, num_scanners):
        self.index = index  # index of the scanner's cloud in scanner_clouds
        self.uncompared = set(range(num_scanners)) - set([index])
        self.shared = set()
        self.rotation_i = None
        self.isSolved = False


x90 = np.array([[1, 0, 0],
                [0, 0, 1],
                [0, -1, 0]], int)
y90 = np.array([[0, 0, 1],
                [0, 1, 0],
                [-1, 0, 0]], int)
z90 = np.array([[0, 1, 0],
                [-1, 0, 0],
                [0, 0, 1]], int)

xr = [np.identity(3, int), x90, x90 @ x90, x90 @ x90 @ x90]
yr = [np.identity(3, int), y90, y90 @ y90, y90 @ y90 @ y90]
zr = [np.identity(3, int), z90, z90 @ z90, z90 @ z90 @ z90]


def rotate(vector, x=0, y=0, z=0):
    """rotate a vector in increments of 90 degrees. does x rotation, then y rotation, then z rotation"""
    return xr[x % 4] @ yr[y % 4] @ zr[z % 4] @ vector


rotations = np.array([xr[x % 4] @ yr[y % 4] @ zr[z % 4]
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
    view_dtype = {'names': ['f0', 'f1', 'f2'], 'formats': [int, int, int]}
    for s_scan_i in solved_scanners_indices:
        for s_beacon_i in range(len(scanner_clouds[s_scan_i]) - (OVERLAP_COUNT - 1)):
            # must include at least one scanner in the overlap cloud, if any exist
            rebased_s_beacons = scanner_clouds[s_scan_i] - scanner_clouds[s_scan_i][s_beacon_i]
            v1 = rebased_s_beacons.view(view_dtype)

            for c_scanner_i in comp_tracker[s_scan_i].uncompared:
                rotated_c_beacons = np.einsum('wyx,zx->wzy', rotations, scanner_clouds[c_scanner_i])
                for c_beacon_i in range(len(scanner_clouds[c_scanner_i])):
                    rebased_c_beacons = rotated_c_beacons - rotated_c_beacons[:, np.newaxis, c_beacon_i]
                    for rotation_i in range(len(rotations)):
                        v2 = rebased_c_beacons[rotation_i].view(view_dtype)
                        matches, s_indices, c_indices = np.intersect1d(v1,
                                                                       v2,
                                                                       return_indices=True)
                        if matches.size > 1:
                            pass
                        if matches.size >= 12:
                            return s_scan_i, s_beacon_i, c_scanner_i, c_beacon_i, rotation_i
    return None


def try_scanner():


IDENTITY_ROT_I = 0
OVERLAP_COUNT = 12

if __name__ == '__main__':
    scanner_clouds = read_input('inputs/D19test.txt')
    comp_tracker = {i: Scanner(i, len(scanner_clouds)) for i in range(len(scanner_clouds))}  # comparison tracker
    solved_scanners_indices = [0]
    comp_tracker[0].isSolved = True
    comp_tracker[0].rotation_i = IDENTITY_ROT_I

    solve_scanner, solve_beacon, new_scanner, new_beacon,  = find_matches()
    pass
