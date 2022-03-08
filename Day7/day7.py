def getcost_constant(pos):
    return sum([abs(pos - i) for i in positions])


def getcost_triangle(pos):
    return sum([triangle(pos, i) for i in positions])


def triangle(a, b):
    diff = abs(a - b)
    return (diff * (diff + 1)) // 2


def checkslope(pos, costfunc=getcost_constant):
    """-1 means less than the min, 1 means more than min, 0 means min"""
    cost = costfunc(pos)
    l_cost = costfunc(pos - 1)
    r_cost = costfunc(pos + 1)
    if cost < l_cost:
        if cost < r_cost:
            return 0
        else:
            return -1
    else:
        return 1


def findmin(costfunc=getcost_constant):
    rbound = max(positions)
    lbound = min(positions)
    cnt = 0
    while True:
        cnt += 1
        guess = (rbound + lbound) // 2
        slope = checkslope(guess, costfunc=costfunc)
        if slope == 1:
            rbound = guess
        elif slope == -1:
            lbound = guess
        elif slope == 0:
            print(cnt)
            return guess


if __name__ == '__main__':
    f = open('D7.txt', 'r')
    data = f.readline()
    f.close()
    costfunc = getcost_triangle
    positions = [int(x) for x in data.split(',')]
    print(costfunc(findmin(costfunc=costfunc)))
