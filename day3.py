def mostcommonvalue(lst):
    counters = ([0] * len(lst[0]))
    for s in lst:
        for i in range(len(s)):
            if s[i] == '1':
                counters[i] += 1
            else:
                counters[i] -= 1
    return "".join(["1" if i >= 0 else "0" for i in counters])


def findpower(lst):
    gamma_str = mostcommonvalue(lst)
    epsilon_str = "".join(["0" if b == "1" else "1" for b in gamma_str])
    return int(gamma_str, base=2) * int(epsilon_str, base=2)


def find_life_support(lst):
    o2_cnt = 0
    o2_lst = lst
    while len(o2_lst) > 1:
        o2_lst1 = [i for i in o2_lst if i[o2_cnt] == mostcommonvalue(o2_lst)[o2_cnt]]
        o2_lst = o2_lst1
        o2_cnt += 1

    co2_cnt = 0
    co2_lst = lst
    while len(co2_lst) > 1:
        co2_lst_1 = [i for i in co2_lst if i[co2_cnt] != mostcommonvalue(co2_lst)[co2_cnt]]
        co2_lst = co2_lst_1
        co2_cnt += 1
    return int(o2_lst[0], base=2) * int(co2_lst[0], base=2)


if __name__ == '__main__':
    f = open('inputs/Day3/D3.txt', 'r')
    input_data = [x.rstrip() for x in f.readlines()]
    f.close()
    print(findpower(input_data))
    print(find_life_support(input_data))
