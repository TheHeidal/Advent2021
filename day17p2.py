import math

import numpy as np

ORIGIN_X = 0
ORIGIN_Y = 0

LB_X = 155
UB_X = 215
UB_Y = -72
LB_Y = -132


def sanity_check():
    assert UB_X > LB_X
    assert UB_Y > LB_Y


def tri(n):
    return (n * (n + 1)) // 2


def min_tri_geq(n):
    """returns smallest number x such that tri(x) >= n"""
    return math.ceil((math.sqrt((8 * n) + 1) - 1) / 2)


def x_pos(v0, time):
    """Return the x position of a projectile with initial velocity v0 at time"""
    if time < 0:
        return ORIGIN_X  # allows calculating x_pos(v0, 0)
    if time >= v0:
        return tri(v0)
    else:
        return time * v0 - tri(time - 1)


def vx(v0, t):
    """Return the velocity of a projectile with initial velocity v0 at time t"""
    if t < 0:
        return v0  # allows calculating vx(v0, 0)
    if t > v0:
        return 0
    else:
        return v0 - t


def x_will_hit(v0, t):
    """don't actually use this, just check if x_pos(v0,t) is in new_bounds"""
    return LB_X <= x_pos(v0, t - 1) + vx(v0, t - 1) <= UB_X


VX_MAX = UB_X  # greatest velocity that will ever have an x_pos <= UB_X
VX_MIN = min_tri_geq(LB_X - ORIGIN_X)  # smallest velocity that will ever end up past LB_X

# what is the fastest v0 (vx_max_inf) that will still be inside the target when it runs out of momentum?
# let v_max be the greatest v s.t. x_pos(v, v) <= UB_X
# x_pos(a,a) = tri(a)
# therefore v_max is the greatest v s.t. tri(v) <= UB_X
#                and the greatest v s.t. tri(v)  < UB_X + 1
# let w = v_max + 1
# w is the smallest integer s.t. tri(w) >= UB_X + 1
# w = min_tri_geq(UB_X + 1), by definition of min_tri_geq
# therefore v_max = min_tri_geq(UB_X + 1) - 1
VX_MAX_INF = min_tri_geq(UB_X + 1) - 1

# note: v_max is not necessarily the greatest v s.t. x_pos(v, min_tri_geq(UB_X + 1) - 1) <= UB_X
#       i.e. there can still be projectiles in new_bounds that started with more velocity that v_max.
#       They just must still have momentum.
#       But by next turn, x_pos(v_max+1, v_max+1) must be > UB_X, or else v_max+1 would = v_max
#       so at time v_max+1, the projectile with the greatest initial velocity still within new_bounds must be v_max
MAX_X_TIME = VX_MAX_INF + 1  # when t = MAX_X_TIME, every velocity that will overshoot has overshot


def max_vx(time):
    """
    Finds the greatest vx such that x_pos(vx, t) <= UB
        If we could have non-int velocities, we would be able to hit the UB every time.
        So we calculate what that would be, then round down.
    """
    if time == 0:
        return None
    if time >= MAX_X_TIME:
        return VX_MAX_INF
    else:
        return (UB_X + tri(time - 1)) // time


def min_vx(time):
    """Return the smallest vx0 such that x_pos(vx0, t) >= LB_X"""
    if time == 0:
        return None
    overall_min = min_tri_geq(LB_X)  # the smallest v0 that will ever put a projectile over the LB
    if time >= overall_min:
        return overall_min
    else:
        return math.ceil((LB_X + tri(time - 1)) / time)


def calc_x_bounds(t):
    """Return the smallest and greatest initial vx that will put a projectile within bounds at time t"""
    min_x, max_x = min_vx(t), max_vx(t)
    if min_x is not None and max_x is not None and min_x <= max_x:
        return min_x, max_x
    else:
        return None


VY_MAX = abs(LB_Y)  # the highest VY possible without immediately overshooting the target on the way back down
MAX_Y_TIME = (VY_MAX * 2)  # the time when a projectile shot at VY_MAX hits the mirror point
VY_MIN = LB_Y


def y_pos(v0, time):
    return time * v0 - tri(time - 1)


def ypos_neg(v0, time):
    """numpy can't do arrays with negative indexes, so this is my hack"""
    return y_pos(-v0, time)


def vy(v0, t):
    return v0 - t


def max_vy(t):
    """Finds the greatest vy such that y_pos(vy, t) <= UB"""
    if t == 0:
        return None
    return (UB_Y + tri(t - 1)) // t


def min_vy(t):
    """finds the smallest vy such that y_pos(vy,t) >= LB"""
    if t == 0:
        return None
    return math.ceil((LB_Y + tri(t - 1)) / t)


def calc_y_bounds(t):
    min_v = min_vy(t)
    max_v = max_vy(t)
    if min_v is not None and max_v is not None and min_v <= max_v:
        return min_v, max_v
    else:
        return None


class Bounds:
    def __init__(self, bounds=None, left=None, right=None, container=None):
        if bounds is None:
            self.initialized = False
            self._min = None
            self._max = None
        elif type(bounds) is tuple:
            self.initialized = True
            self._min, self._max = bounds

        if left is not None:
            self.left = left
        else:
            self.left = None

        if right is not None:
            self.right = right
        else:
            self.right = None

    def update(self, new_bounds=None, call_from=None):
        """Add new bounds. call_from should only be used by this class"""
        if new_bounds is None:
            return
        elif self.initialized:
            if new_bounds[1] < self.min:  # if new_bound is outside and left of current bounds
                if call_from == 'l':  # if already trying to update from left
                    self._insert_left(new_bounds)
                elif self.left is not None:
                    self.left.update(new_bounds, call_from='r')
                else:
                    self.left = Bounds(bounds=new_bounds, right=self)

            elif new_bounds[0] > self.max:
                if call_from == 'r':
                    self._insert_right(new_bounds)
                elif self.right is not None:
                    self.right.update(new_bounds, call_from='l')
                else:
                    self.right = Bounds(bounds=new_bounds, left=self)

            else:
                self.min = min(self.min, new_bounds[0])
                self.max = max(self.max, new_bounds[1])
        else:
            self.min = new_bounds[0]
            self.max = new_bounds[1]
            self.initialized = True

    def count(self):
        if self.left is not None:
            l_count = self.left.count_left()
        else:
            l_count = 0
        if self.right is not None:
            r_count = self.right.count_right()
        else:
            r_count = 0
        if self.initialized:
            return self.max - self.min + 1 + l_count + r_count
        else:
            return 0

    def count_left(self):
        if self.left is None:
            return self.max - self.min + 1
        else:
            return (self.max - self.min + 1) + self.left.count_left()

    def count_right(self):
        if self.right is None:
            return self.max - self.min + 1
        else:
            return (self.max - self.min + 1) + self.right.count_right()

    @property
    def min(self):
        return self._min

    @min.setter
    def min(self, value):
        if self._min is None:
            self._min = value
        else:
            if self._min > value:
                self._min = value
                if self.left is not None and self.left.max >= value:
                    self._merge_left()

    @property
    def max(self):
        return self._max

    @max.setter
    def max(self, value):
        if self._max is None:
            self._max = value
        else:
            if self._max > value:
                self._max = value
                if self.right is not None and self.right.min <= value:
                    self._merge_left()

    def _insert_left(self, bounds):
        """inserts a Bound between this and its left"""
        new_Bound = Bounds(bounds=bounds, left=self.left, right=self)
        self.left.right = new_Bound
        self.left = new_Bound

    def _insert_right(self, bounds):
        """Insert a Bound between this and its right neighbor"""
        new_Bound = Bounds(bounds=bounds, left=self, right=self.right)
        self.right.left = new_Bound
        self.right = new_Bound

    def _merge_left(self):
        self._min = self.left.min
        next_left = self.left.left
        del self.left
        self.left = next_left

    def _merge_right(self):
        self._max = self.right.max
        next_right = self.right.right
        del self.right
        self.right = next_right

    def print_left(self):
        """returns a string representation of this and all bounds left of it. Called by the bound right of it"""
        if self.left is None:
            return f"[({self.min},{self.max}), "
        else:
            return f"{self.left.print_left()}({self.min},{self.max}), "

    def print_right(self):
        if self.right is None:
            return f", ({self.min},{self.max})]"
        else:
            return f", ({self.min},{self.max}){self.right.print_right()}"

    def __repr__(self):
        if self.initialized is False:
            return '(,)'
        else:
            return f'''{'[' if self.left is None else self.left.print_left()}*({self.min},{self.max})*{']' if self.right is None else self.right.print_right()}'''


xpos_v = np.vectorize(x_pos)
ypos_v = np.vectorize(y_pos)
ypos_neg_v = np.vectorize(ypos_neg)


def test_x():
    max_vxs = [max_vx(t) for t in range(MAX_X_TIME + 1)]
    min_vxs = [min_vx(t) for t in range(MAX_X_TIME + 1)]
    x_table = np.fromfunction(xpos_v, (VX_MAX + 1, MAX_X_TIME + 1), dtype=int)  # +1 to correct for 0 indexing
    x_table_hit = np.logical_and(x_table <= UB_X, LB_X <= x_table)
    pass


def test_y():
    max_vys = [max_vy(t) for t in range(MAX_Y_TIME + 1)]
    min_vys = [min_vy(t) for t in range(MAX_Y_TIME + 1)]
    y_table = np.fromfunction(ypos_v, (31, 31), dtype=int)
    y_table_hit = np.logical_and(LB_Y <= y_table, y_table <= UB_Y)
    y_table_neg = np.fromfunction(ypos_neg_v, (12, 31), dtype=int)
    y_table_neg_hit = np.logical_and(LB_Y <= y_table_neg, y_table_neg <= UB_Y)
    pass


def calc_bounds():
    vx_bounds = [calc_x_bounds(t) for t in range(MAX_X_TIME + 1)]
    vy_bounds = [calc_y_bounds(t) for t in range(MAX_Y_TIME + 1)]

    bound_dict = {y: Bounds(bounds=None) for y in range(VY_MIN, VY_MAX + 1)}

    for i in range(len(vy_bounds)):
        if vy_bounds[i] is not None:
            y_lower = vy_bounds[i][0]
            y_upper = vy_bounds[i][1]
            # TODO: implement the vx_bounds list as a class subclassing List which implements this automatically?
            try:
                x_bounds = vx_bounds[i]
            except IndexError:
                x_bounds = vx_bounds[-1]
            for y in range(y_lower, y_upper + 1):
                bound_dict[y].update(x_bounds)
    return bound_dict


TESTING_X = False
TESTING_Y = False

if __name__ == '__main__':
    sanity_check()
    if TESTING_X:
        test_x()
    if TESTING_Y:
        test_y()

    bound_d = calc_bounds()
    result = sum((j.count() for j in bound_d.values()))
    print(result)
    pass
