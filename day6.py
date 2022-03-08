def readinput(file):
    f = open(file, 'r')
    data = f.readline()
    f.close()
    numbers = [data.count(str(n)) for n in range(9)]
    return numbers


def main(fishdist):
    num = fishdist
    for _ in range(256):
        newnum = num[1:]
        newnum[6] += num[0]
        newnum.append(num[0])
        num = newnum
    print(sum(num))


if __name__ == '__main__':
    num = readinput('inputs/Day6/D6.txt')
    main(num)
