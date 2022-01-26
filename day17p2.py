import math

import numpy as np

ORIGIN_X = 0
ORIGIN_Y = 0

UB_X = 30
LB_X = 20
UB_Y = -5
LB_Y = -10


def sanity_check():
    assert UB_X > LB_X
    assert UB_Y > LB_Y


def tri(n):
    return (n * (n + 1)) // 2


def min_tri_geq(n):
    """returns smallest number x such that tri(x) >= n"""
    return math.ceil((math.sqrt((8 * n) + 1) - 1) / 2)


def xpos(v0, time):
    if time < 0:
        return ORIGIN_X  # allows calculating xpos(v0, 0)
    if time >= v0:
        return tri(v0)
    else:
        # return tri(v0) - tri(v0 - time)
        return time * v0 - tri(time - 1)


def vx(v0, t):
    if t < 0:
        return v0  # allows calculating vx(v0, 0)
    if t > v0:
        return 0
    else:
        return v0 - t


def x_will_hit(v0, t):
    """don't actually use this, just check if xpos(v0,t) is in new_bounds"""
    return LB_X <= xpos(v0, t - 1) + vx(v0, t - 1) <= UB_X


VX_MAX = UB_X  # greatest velocity that will ever have an xpos <= UB_X
VX_MIN = min_tri_geq(LB_X - ORIGIN_X)  # smallest velocity that will ever end up past LB_X

# what is the fastest v0 (vx_max_inf) that will still be inside the target when it runs out of momentum?
# let v_max be the greatest v s.t. xpos(v, v) <= UB_X
# xpos(a,a) = tri(a)
# therefore v_max is the greatest v s.t. tri(v) <= UB_X
#                and the greatest v s.t. tri(v)  < UB_X + 1
# let w = v_max + 1
# w is the smallest integer s.t. tri(w) >= UB_X + 1
# w = min_tri_geq(UB_X + 1), by definition of min_tri_geq
# therefore v_max = min_tri_geq(UB_X + 1) - 1
VX_MAX_INF = min_tri_geq(UB_X + 1) - 1

# note: v_max is not necessarily the greatest v s.t. xpos(v, min_tri_geq(UB_X + 1) - 1) <= UB_X
#       i.e. there can still be projectiles in new_bounds that started with more velocity that v_max.
#       They just must still have momentum.
#       But by next turn, xpos(v_max+1, v_max+1) must be > UB_X, or else v_max+1 would = v_max
#       so at time v_max+1, the projectile with the greatest initial velocity still within new_bounds must be v_max
MAX_X_TIME = VX_MAX_INF + 1  # when t = MAX_X_TIME, every velocity that will overshoot has overshot


def max_vx(time):
    """
    Finds the greatest vx such that xpos(vx, t) <= UB
        if we could have non-int velocities, we would be able to hit the UB every time.
        So we calculate what that would be, then round down
    """
    if time == 0:
        return None
    if time >= MAX_X_TIME:
        return VX_MAX_INF
    else:
        return (UB_X + tri(time - 1)) // time


def min_vx(time):
    if time == 0:
        return None
    overall_min = min_tri_geq(LB_X)
    if time >= overall_min:
        return overall_min
    else:
        return math.ceil((LB_X + tri(time - 1))
                         / time)


def calc_x_bounds(t):
    min_x, max_x = min_vx(t), max_vx(t)
    if min_x is not None and max_x is not None:
        return min_x, max_x
    else:
        return None


VY_MAX = abs(LB_Y)  # the highest VY possible without immediately overshooting the target on the way back down
MAX_Y_TIME = (VY_MAX * 2)  # the time when a projectile shot at VY_MAX hits the mirror point
VY_MIN = LB_Y


def ypos(v0, time):
    return time * v0 - tri(time - 1)


def ypos_neg(v0, time):
    """numpy can't do arrays with negative indexes, so this is my hack"""
    return ypos(-v0, time)


def vy(v0, t):
    return v0 - t


def max_vy(t):
    """Finds the greatest vy such that ypos(vy, t) <= UB"""
    if t == 0:
        return None
    return (UB_Y + tri(t - 1)) // t


def min_vy(t):
    """finds the smallest vy such that ypos(vy,t) >= LB"""
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


def y_will_hit(v0, t):
    return LB_Y <= ypos(v0, t - 1) + vy(v0, t - 1) <= UB_Y


class Bounds:
    def __init__(self, bounds=None):
        if bounds is None:
            self.initialized = False
        elif type(bounds) is tuple:
            self.initialized = True
            self.min, self.max = bounds

    def update(self, new_bounds=None):
        if new_bounds is None:
            return
        elif self.initialized:
            if self.min <= new_bounds[0] <= self.max or self.min <= new_bounds[1] <= self.max:
                self.min = min(self.min, new_bounds[0])
                self.max = max(self.max, new_bounds[1])
            else:
                raise NotImplementedError
        else:
            self.min = new_bounds[0]
            self.max = new_bounds[1]
            self.initialized = True

    def count(self):
        if self.initialized:
            return self.max - self.min + 1
        else:
            return 0

    def __repr__(self):
        if self.initialized is False:
            return '(,)'
        else:
            return f'({self.min},{self.max})'


xpos_v = np.vectorize(xpos)
ypos_v = np.vectorize(ypos)
ypos_neg_v = np.vectorize(ypos_neg)

TESTING_X = False
TESTING_Y = False

if __name__ == '__main__':
    sanity_check()
    if TESTING_X:
        max_vxs = [max_vx(t) for t in range(MAX_X_TIME + 1)]
        min_vxs = [min_vx(t) for t in range(MAX_X_TIME + 1)]
        x_table = np.fromfunction(xpos_v, (VX_MAX + 1, MAX_X_TIME + 1), dtype=int)  # +1 to correct for 0 indexing
        x_table_hit = np.logical_and(x_table <= UB_X, LB_X <= x_table)
        pass

    if TESTING_Y:
        max_vys = [max_vy(t) for t in range(MAX_Y_TIME + 1)]
        min_vys = [min_vy(t) for t in range(MAX_Y_TIME + 1)]
        y_table = np.fromfunction(ypos_v, (31, 31), dtype=int)
        y_table_hit = np.logical_and(LB_Y <= y_table, y_table <= UB_Y)
        y_table_neg = np.fromfunction(ypos_neg_v, (12, 31), dtype=int)
        y_table_neg_hit = np.logical_and(LB_Y <= y_table_neg, y_table_neg <= UB_Y)
        pass

    vx_bounds = [calc_x_bounds(t) for t in range(MAX_X_TIME + 1)]
    vy_bounds = [calc_y_bounds(t) for t in range(MAX_Y_TIME + 1)]
    count_dict = {y: Bounds(bounds=None) for y in range(VY_MIN, VY_MAX + 1)}
    for i in range(len(vy_bounds)):
        if vy_bounds[i] is not None:
            y_lower = vy_bounds[i][0]
            y_upper = vy_bounds[i][1]
            try:
                x_bounds = vx_bounds[i]
            except IndexError:
                x_bounds = vx_bounds[-1]
            for y in range(y_lower, y_upper + 1):
                count_dict[y].update(x_bounds)
    result = sum((j.count() for j in count_dict.values()))
    pass
