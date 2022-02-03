import heapq
import logging
from functools import reduce

logging.basicConfig(filename='day18.log', encoding='utf-8', level=logging.DEBUG)


class SnailNumber:
    def __init__(self, num, depth: int = 0, parent=None, side=None):
        """

        :param num:
        :param depth:
        :param parent:
        :param side: str
            'l' if this is the parent's left child, 'r' if this is the parent's right child
        """
        self.depth = depth
        self.parent = parent
        self.side = side
        if type(num) is int:
            self.val = num
            self.left = None
            self.right = None
        else:
            self.val = None
            self.left = SnailNumber(num[0], depth + 1, parent=self, side='l')
            self.right = SnailNumber(num[1], depth + 1, parent=self, side='r')

    def reduce(self):
        """
        To reduce a snailfish number, you must repeatedly do the first action in this list that applies to the snailfish number:
            If any pair is nested inside four pairs, the leftmost such pair explodes.
            If any regular number is 10 or greater, the leftmost such regular number splits.
        """
        exploded = self.search_explode()
        if exploded:
            logging.info(f"after explode:  {self}")
        split = False
        if not exploded:
            split = self.split()
            if split:
                logging.info(f"after split:    {self}")
        if exploded or split:
            self.reduce()

    def search_explode(self):
        """
        If any pair is nested inside four pairs, the leftmost such pair explodes.
            To explode a pair
                the pair's left value is added to the first regular number to the left of the exploding pair (if any),
                the pair's right value is added to the first regular number to the right of the exploding pair (if any).
                Then, the entire exploding pair is replaced with the regular number 0.
            Exploding pairs will always consist of two regular numbers.
        :return: Bool
            True if found something to explode
        """
        if self.val is not None:
            return False  # Can't explode ints

        elif self.left.val is not None and self.right.val is not None:
            # if this is a leaf pair (both children are ints)
            if self.depth >= 4:
                # explode pair
                logging.debug(f"exploding {self}")
                l_neighbor = self.find_left_neighbor()
                if l_neighbor is not None:
                    l_neighbor.val = l_neighbor.val + self.left.val
                r_neighbor = self.find_right_neighbor()
                if r_neighbor is not None:
                    r_neighbor.val = r_neighbor.val + self.right.val
                self.left = None
                self.right = None
                self.val = 0
                return True
            else:
                return False
        else:
            explode_l = self.left.search_explode()
            if not explode_l:
                return self.right.search_explode()
            else:
                return True

    def split(self):
        """
        To split a regular number, replace it with a pair;
            the left element of the pair should be the regular number divided by two and rounded down
            the right element of the pair should be the regular number divided by two and rounded up.
        :return: Bool
            True if something split
        """
        if self.val is not None:
            if self.val >= 10:
                self.left = SnailNumber(self.val // 2, depth=self.depth + 1, parent=self, side='l')
                self.right = SnailNumber((self.val + 1) // 2, depth=self.depth + 1, parent=self, side='r')
                self.val = None
                return True
            else:
                return False
        else:
            split_l = self.left.split()
            if not split_l:
                return self.right.split()
            else:
                return True

    def find_left_neighbor(self):
        """Find the first int to the left of self"""

        def dive_right(snail_num):
            """find rightmost SnailNumber"""
            curr = snail_num
            while curr.right is not None:
                curr = curr.right
            return curr

        if self.side == 'r':
            return dive_right(self.parent.left)
        if self.side == 'l':
            # climb left until we're on the right of something
            cl_curr = self.parent
            while cl_curr.side is not None and cl_curr.side == 'l':
                cl_curr = cl_curr.parent
            if cl_curr.side is None:
                return None
            elif cl_curr.side == 'r':
                return dive_right(cl_curr.parent.left)

    def find_right_neighbor(self):
        """find the first int to the right of self"""

        def dive_left(snail_num):
            """find leftmost snailNumber"""
            curr = snail_num
            while curr.left is not None:
                curr = curr.left
            return curr

        if self.side == 'l':
            return dive_left(self.parent.right)
        if self.side == 'r':
            # climb right until we're on the left of something
            cr_curr = self.parent
            while cr_curr.side is not None and cr_curr.side == 'r':
                cr_curr = cr_curr.parent
            if cr_curr.side is None:
                return None
            elif cr_curr.side == 'l':
                return dive_left(cr_curr.parent.right)

    def increment_depth(self):
        self.depth += 1
        if self.val is not None:
            self.left.increment_depth()
            self.right.increment_depth()

    def to_list(self):
        if self.val is not None:
            return self.val
        else:
            return [x.to_list() for x in [self.left, self.right]]

    def magnitude(self):
        if self.val is not None:
            return self.val
        else:
            return (3 * self.left.magnitude()) + (2 * self.right.magnitude())

    def __add__(self, other):
        assert type(other) is SnailNumber
        number = SnailNumber([x.to_list() for x in [self, other]])
        logging.info(f"after addition: {number}")
        number.reduce()
        return number

    def __copy__(self):
        return SnailNumber(self.to_list())

    def __eq__(self, other):
        if type(other) is SnailNumber:
            if self.val is not None:
                return self.val == other.val
            else:
                return self.left == other.left and self.right == other.right
        else:
            return False

    def __repr__(self):
        if self.val is not None:
            return f"{self.val}"
        else:
            return f'[{self.left.__repr__()},{self.right.__repr__()}]'


example_numbers = [[1, 2],
                   [[1, 2], 3],
                   [9, [8, 7]],
                   [[1, 9], [8, 5]],
                   [[[[1, 2], [3, 4]], [[5, 6], [7, 8]]], 9],
                   [[[9, [3, 8]], [[0, 9], 6]], [[[3, 7], [4, 9]], 3]],
                   [[[[1, 3], [5, 3]], [[1, 3], [8, 7]]], [[[4, 9], [6, 9]], [[8, 2], [7, 3]]]]]

example_explosions = [([[[[[9, 8], 1], 2], 3], 4], [[[[0, 9], 2], 3], 4]),
                      ([7, [6, [5, [4, [3, 2]]]]], [7, [6, [5, [7, 0]]]]),
                      ([[6, [5, [4, [3, 2]]]], 1], [[6, [5, [7, 0]]], 3]),
                      ([[3, [2, [1, [7, 3]]]], [6, [5, [4, [3, 2]]]]], [[3, [2, [8, 0]]], [9, [5, [4, [3, 2]]]]]),
                      ([[3, [2, [8, 0]]], [9, [5, [4, [3, 2]]]]], [[3, [2, [8, 0]]], [9, [5, [7, 0]]]])]

example_add = [([[[[[4, 3], 4], 4], [7, [[8, 4], 9]]],
                 [1, 1]],
                [[[[0, 7], 4], [[7, 8], [6, 0]]], [8, 1]]),
               ([[1, 1],
                 [2, 2],
                 [3, 3],
                 [4, 4]],
                [[[[1, 1], [2, 2]], [3, 3]], [4, 4]]),
               ([[1, 1],
                 [2, 2],
                 [3, 3],
                 [4, 4],
                 [5, 5]],
                [[[[3, 0], [5, 3]], [4, 4]], [5, 5]]),
               ([[[[0, [4, 5]], [0, 0]], [[[4, 5], [2, 6]], [9, 5]]],
                 [7, [[[3, 7], [4, 3]], [[6, 3], [8, 8]]]],
                 [[2, [[0, 8], [3, 4]]], [[[6, 7], 1], [7, [1, 6]]]],
                 [[[[2, 4], 7], [6, [0, 5]]], [[[6, 8], [2, 8]], [[2, 1], [4, 5]]]],
                 [7, [5, [[3, 8], [1, 4]]]],
                 [[2, [2, 2]], [8, [8, 1]]],
                 [2, 9],
                 [1, [[[9, 3], 9], [[9, 0], [0, 7]]]],
                 [[[5, [7, 4]], 7], 1],
                 [[[[4, 2], 2], 6], [8, 7]]],
                [[[[8, 7], [7, 7]], [[8, 6], [7, 7]]], [[[0, 7], [6, 6]], [8, 7]]])]

example_magnitude = [([9, 1], 29),
                     ([[1, 2], [[3, 4], 5]], 143),
                     ([[[[0, 7], 4], [[7, 8], [6, 0]]], [8, 1]], 1384),
                     ([[[[1, 1], [2, 2]], [3, 3]], [4, 4]], 445)]

input_data = [[[[4, 5], [[0, 6], [4, 5]]], [3, [[5, 0], [0, 8]]]],
              [[8, 3], 2],
              [[4, [7, [5, 6]]], [[[7, 8], 5], [[7, 0], 1]]],
              [[[1, 8], [7, 6]], [[8, 6], [3, 2]]],
              [[[4, [2, 0]], [1, [7, 0]]], 9],
              [2, [[[2, 3], 5], [6, 5]]],
              [9, [1, [0, 3]]],
              [5, [5, [8, [8, 4]]]],
              [5, [1, [4, [0, 8]]]],
              [1, [[[6, 1], 9], 2]],
              [7, [[6, 1], [[7, 8], [4, 2]]]],
              [[[[6, 6], [3, 3]], [6, [7, 6]]], 4],
              [[[3, [9, 8]], [[6, 6], [9, 3]]], [[[9, 2], 3], [[7, 6], 0]]],
              [[[[5, 2], 6], [9, [1, 7]]], [[9, 9], [9, [4, 3]]]],
              [[[7, 6], [9, 5]], [[[6, 3], [8, 4]], [[4, 0], 8]]],
              [[[0, [1, 9]], [8, [4, 4]]], 1],
              [[1, [1, [9, 4]]], [5, [[9, 3], 9]]],
              [[[1, 3], [[2, 3], 9]], [7, 9]],
              [[8, [[6, 9], [5, 9]]], [5, [5, [9, 4]]]],
              [[[[3, 7], [8, 0]], [4, [8, 9]]], [[[3, 8], [3, 5]], [9, 0]]],
              [[[0, 5], [5, 1]], [3, [0, [0, 5]]]],
              [7, [[4, [1, 6]], 0]],
              [[3, [4, 4]], [[[0, 5], 9], [8, [9, 5]]]],
              [[8, [5, 2]], [[[7, 4], [3, 2]], 4]],
              [[[[6, 4], [7, 9]], 5], [3, [[4, 3], [4, 3]]]],
              [[[[7, 0], 6], [6, 7]], [[[9, 7], [3, 7]], [[4, 1], [0, 6]]]],
              [[6, [[1, 0], [1, 7]]], [3, [3, 0]]],
              [[[2, [6, 0]], 4], [[3, 9], [4, 1]]],
              [[[0, [8, 4]], [[8, 7], 5]], [1, 6]],
              [[[[4, 0], 7], 9], [6, [8, [9, 3]]]],
              [[[[0, 8], 7], [5, [4, 0]]], [5, [6, [8, 7]]]],
              [[[1, 4], [[9, 7], 4]], [[4, [6, 4]], 1]],
              [[5, [[8, 6], 9]], 1],
              [[[[5, 7], [8, 3]], [[3, 2], [1, 9]]], [2, [1, 2]]],
              [[[9, 6], [1, 5]], [8, 6]],
              [3, 1],
              [[2, [[2, 0], 4]], [[[3, 4], 1], 3]],
              [[[[8, 6], [5, 9]], 7], 2],
              [[[[1, 0], [8, 5]], [[6, 5], [0, 0]]], [[[3, 4], [4, 6]], [[5, 0], 8]]],
              [[[[6, 4], [9, 4]], [[2, 1], [2, 2]]], [[[7, 9], 1], [[6, 1], 5]]],
              [2, [[4, 4], 5]],
              [[[[0, 8], 9], [8, 6]], [[[9, 7], [0, 8]], [[9, 3], 7]]],
              [[[[2, 0], [7, 8]], [[8, 5], [6, 8]]], [7, [[1, 1], [2, 3]]]],
              [[9, [5, [4, 7]]], [0, [9, 2]]],
              [5, [[[7, 5], 3], [6, [5, 3]]]],
              [[1, [5, 1]], [[[0, 3], [3, 9]], 3]],
              [7, [[0, [0, 1]], [1, 2]]],
              [[4, [8, 0]], [3, [[2, 4], 7]]],
              [8, [[1, [8, 9]], [0, 0]]],
              [0, [[2, 9], [[9, 7], [5, 3]]]],
              [[[6, [3, 4]], [[0, 6], [4, 3]]], 9],
              [[[[0, 6], 6], 6], [[7, 8], [[7, 3], [5, 0]]]],
              [[[7, [4, 5]], [9, 2]], [6, [[5, 5], [0, 2]]]],
              [[[6, 8], [5, [0, 8]]], [[1, [6, 6]], [0, 6]]],
              [[[[4, 7], 7], [2, 7]], [[8, 0], [[6, 5], [2, 0]]]],
              [8, [[4, 9], [[8, 8], 2]]],
              [2, [[4, [5, 8]], [[8, 7], [0, 9]]]],
              [[[[2, 8], 0], 6], [[[4, 4], 0], [1, 3]]],
              [1, [[[8, 5], 1], 8]],
              [[3, 3], [[[5, 6], [6, 2]], 5]],
              [[9, 2], [3, [[3, 2], 4]]],
              [[[[2, 4], [6, 3]], [[4, 6], 4]], [[[1, 9], [0, 4]], [[2, 6], [9, 0]]]],
              [[[4, [6, 7]], [[8, 4], [6, 2]]], [[5, 2], [[4, 8], 0]]],
              [[[6, 0], [[3, 2], 5]], [[[9, 0], [7, 0]], 5]],
              [[2, [9, 3]], [[4, [4, 6]], [9, 6]]],
              [[3, [3, 6]], [[[2, 4], 1], [9, [7, 7]]]],
              [4, [1, [[3, 6], [4, 1]]]],
              [[3, 7], [[5, 6], 6]],
              [[[0, 8], 4], [[3, 5], [[6, 2], 6]]],
              [[[6, [8, 9]], [5, [2, 4]]], [4, [3, 4]]],
              [5, [[[6, 8], [5, 7]], [5, [9, 9]]]],
              [[[[9, 5], 6], 3], [[[8, 2], 4], [1, 8]]],
              [[9, [9, 3]], [[[5, 7], 0], [[5, 4], [7, 4]]]],
              [[[[7, 7], 7], 6], 9],
              [[9, 8], [2, [7, 7]]],
              [[[[5, 9], 6], [8, [9, 2]]], [[[8, 5], [9, 5]], [3, [8, 3]]]],
              [[[4, [3, 8]], [8, [4, 3]]], [[0, 5], [5, [4, 5]]]],
              [[[0, 5], [[7, 7], 5]], [[[2, 7], [6, 0]], [[7, 9], [2, 2]]]],
              [6, [2, 8]],
              [[[2, 7], 7], [[[8, 4], [3, 9]], 1]],
              [[[2, 0], [[0, 5], [9, 4]]], [[7, [6, 2]], 9]],
              [[1, [[8, 3], [3, 4]]], 1],
              [[[[2, 0], 9], 3], [1, [7, [2, 1]]]],
              [4, [[6, [5, 7]], [[1, 1], [0, 5]]]],
              [[[6, [0, 7]], [4, [8, 6]]], 3],
              [[[8, 5], 6], [1, [[6, 0], 4]]],
              [[[[6, 5], [5, 6]], [[0, 1], [2, 7]]], [[7, [7, 6]], [[3, 2], [4, 0]]]],
              [[[5, [0, 0]], 0], 5],
              [[[[7, 2], [5, 9]], 2], [3, 7]],
              [7, [[[1, 1], 4], [[4, 4], 2]]],
              [9, [[[9, 1], 1], 3]],
              [[[[6, 9], [3, 9]], [7, [1, 5]]], [[[5, 0], 6], [[5, 9], 8]]],
              [[7, [1, [2, 1]]], [7, [[6, 3], [7, 1]]]],
              [3, [0, [1, 3]]],
              [9, [[[6, 6], 6], [6, 4]]],
              [[[2, [0, 4]], 1], [[9, [5, 1]], [[9, 6], [5, 2]]]],
              [[[9, 8], 6], [0, [6, [0, 5]]]],
              [[[7, 3], [[9, 9], 0]], 7],
              [[[7, 5], [6, 8]], [6, [[0, 8], 9]]],
              [[[2, [0, 5]], [[2, 9], [5, 7]]], 7]]

testing_explode = False
testing_add = False
testing_magnitude = False
testing_homework = False
solve_Q1 = False
solve_Q2_brute = True

if __name__ == '__main__':
    if testing_explode:
        sn_explosions = [(SnailNumber(a), SnailNumber(b)) for a, b in example_explosions]
        for a, b in sn_explosions:
            assert a == a
            a.search_explode()
            assert a == b
    if testing_add:
        sn_add = [([SnailNumber(sn) for sn in sns], SnailNumber(res)) for sns, res in example_add]
        for sns, res in sn_add:
            sm = reduce(lambda x, y: x + y, sns)
            assert sm == res
    if testing_magnitude:
        sn_mag = [(SnailNumber(a), b) for a, b in example_magnitude]
        for a, b in sn_mag:
            assert a.magnitude() == b
    if solve_Q1:
        q1_sum = reduce(lambda x, y: x + y, [SnailNumber(z) for z in input_data])
        print(q1_sum.magnitude())
    if solve_Q2_brute:
        snail_nums = [SnailNumber(x) for x in input_data]
        sorted_sns = []
        for left_i in range(len(snail_nums)):
            for right_i in range(len(snail_nums)):
                heapq.heappush(sorted_sns, (snail_nums[left_i] + snail_nums[right_i]).magnitude())
                heapq.heappush(sorted_sns, (snail_nums[right_i] + snail_nums[left_i]).magnitude())
            if left_i % 10 == 0:
                print(left_i)
        print(heapq.nlargest(1, sorted_sns))

