def part1(lst):
    h_pos, depth = 0, 0
    for instruction in lst:
        if instruction[0] == 'forward': h_pos += int(instruction[1])
        if instruction[0] == 'down': depth += int(instruction[1])
        if instruction[0] == 'up': depth -= int(instruction[1])
    return h_pos * depth


def part2(lst):
    h_pos, depth, aim = 0, 0, 0
    for instruction in lst:
        if instruction[0] == 'down': aim += int(instruction[1])
        if instruction[0] == 'up': aim -= int(instruction[1])
        if instruction[0] == 'forward':
            h_pos += int(instruction[1])
            depth += int(instruction[1]) * aim
    return h_pos * depth


if __name__ == '__main__':
    f = open('D2.txt', 'r')
    input = [x.split() for x in f.readlines()]
    f.close()
    print(part1(input))
    print(part2(input))
