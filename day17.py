from math import ceil, sqrt


def calc_trajectory(position, velocity, steps):
    x_0, y_0 = position
    v_x0, v_y0 = velocity
    for _ in range(steps):
        new_position = (x_0 + v_x0, y_0 + v_y0)
        new_velocity = (slow(v_x0), v_y0 - 1)
        yield new_position, new_velocity
        x_0, y_0 = new_position
        v_x0, v_y0 = new_velocity


def slow(velocity):
    if velocity > 0:
        return velocity - 1
    if velocity < 0:
        return velocity + 1
    else:
        return velocity


def max_x(position, velocity):
    """the furthest x can ever reach is the sum of the triangular sequence up to x"""
    x, _ = position
    v_x, _ = velocity
    max_pos = (x * (x + 1)) // 2
    if x > 0:
        return max_pos
    else:
        return -max_pos


def process_input(s):
    return [(int(bound[0]), int(bound[1])) for bound in
            [axis.split('..') for axis in s.lstrip('target area: x=').split(', y=')]]


def smallest_triangle_geq(n):
    """returns smallest number x such that tri(x) >= n"""
    return ceil((sqrt((8 * n) + 1) - 1) / 2)


def tri(n):
    """returns the nth term of the triangular sequence"""
    return (n * (n + 1)) // 2


def min_v_x(lower_bound):
    """calculates the minimum velocity to reach lower_bound. Any smaller velocity will stall"""
    return smallest_triangle_geq(lower_bound) - 1


def max_x_v(upper_bound):


def max_v_y(lower_bound):
    """calculates the maximum velocity to reach lower_bound. Anything greater will overshoot"""
    return


TEST_Q1 = False
SOLVE_Q1 = True

if __name__ == '__main__':
    if TEST_Q1:
        data = process_input('target area: x=20..30, y=-10..-5')
        low_bound_y = data[1][0]
        v_y0 = -(low_bound_y + 1)
        max_height = tri(v_y0)
        assert max_height == 45
        print(v_y0, max_height, sep=', ')
        # is it possible there's no v_x value that works with the v_y we generate?

    if SOLVE_Q1:
        input_str = 'target area: x=155..215, y=-132..-72'
        data = process_input(input_str)
        low_bound_y = data[1][0]
        v_y0 = -(low_bound_y + 1)
        max_height = tri(v_y0)
        print(v_y0, max_height, sep=', ')
        pass

# for position, vel in calc_trajectory((0, 0), (6, 3), 10):
#     print(position, vel)
