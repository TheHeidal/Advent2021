from collections import deque
from enum import Enum

hex_to_bin = {'0': '0000', '1': '0001', '2': '0010', '3': '0011', '4': '0100', '5': '0101', '6': '0110', '7': '0111',
              '8': '1000', '9': '1001', 'A': '1010', 'B': '1011', 'C': '1100', 'D': '1101', 'E': '1110', 'F': '1111'}


def prod(args):
    val = 1
    for arg in args:
        val = val * arg
    return val


def gt(args):
    assert len(args) == 2
    return args[0] > args[1]


def lt(args):
    assert len(args) == 2
    return args[0] < args[1]


def eq(args):
    assert len(args) == 2
    return args[0] == args[1]


id_to_fn = {0: sum,
            1: prod,
            2: min,
            3: max,
            4: "literal",
            5: gt,
            6: lt,
            7: eq
            }


class TypeID(Enum):
    LITERAL = 4


class Packet:
    def __init__(self, version: int, typeid: int, contents):
        self.version = version
        self.typeid = typeid
        self.contents = contents
        if self.typeid == TypeID.LITERAL.value:
            assert type(contents) is int
        else:
            assert type(contents) is list

    def __str__(self):
        if WANT_VERSION:
            return f"(V:{self.version} Type:{id_to_fn[self.typeid]} Contains:{self.contents})"
        else:
            return f"(Type:{id_to_fn[self.typeid]} Contains:{self.contents})"

    def __repr__(self):
        return str(self)

    def calculate(self):
        if self.typeid == TypeID.LITERAL.value:
            return self.contents
        else:
            calculated_contents = [x.calculate() for x in self.contents]
            return id_to_fn[self.typeid](calculated_contents)

    def version_sum(self):
        if self.typeid == TypeID.LITERAL.value:
            return self.version
        else:
            return self.version + sum(x.version_sum() for x in self.contents)


def mpopleft(q: deque, n: int) -> str:
    """multi-popleft()"""
    ret = "".join(q.popleft() for _ in range(n))
    return ret


def read_single_packet(binary):
    """returns the first complete packet on the list (including sub-packets) and removes it from binary"""
    version = int(mpopleft(binary, 3), base=2)
    typeID = int(mpopleft(binary, 3), base=2)
    if typeID == TypeID.LITERAL.value:
        number = deque()
        while binary[0] == '1':
            binary.popleft()
            number.append(mpopleft(binary, 4))
        binary.popleft()
        number.append(mpopleft(binary, 4))
        number = int("".join(number), base=2)
        return Packet(version, typeID, number)
    else:
        len_typeID = binary.popleft()
        if len_typeID == '0':
            length = int(mpopleft(binary, 15), base=2)
            sub_packets_bin = deque()
            for _ in range(length):
                sub_packets_bin.append(binary.popleft())
            subpackets = read_packets(sub_packets_bin)
            return Packet(version, typeID, subpackets)
        if len_typeID == '1':
            num_subpackets = int(mpopleft(binary, 11), base=2)
            subpackets = [read_single_packet(binary) for _ in range(num_subpackets)]
            return Packet(version, typeID, subpackets)


def read_packets(binary) -> list[Packet]:
    packets: list[Packet] = []
    while any(x == '1' for x in binary):
        packets.append(read_single_packet(binary))
    return packets


def parse_input(filename):
    f = open(filename, 'r')
    hex_input = f.readline().strip()
    f.close()
    return hex_input, deque((bt for h in hex_input for bt in hex_to_bin[h]))


TESTING_Q1 = False
SOLVING_Q1 = False
TESTING_Q2 = False
SOLVING_Q2 = True

WANT_VERSION = False

if __name__ == '__main__':
    if TESTING_Q1:
        for input_file, expected_sum in [('inputs/Day16/test16.txt', 16),
                                         ('inputs/Day16/test12.txt', 12),
                                         ('inputs/Day16/test23.txt', 23),
                                         ('inputs/Day16/test31.txt', 31)]:
            hex_input, bin_input = parse_input(input_file)
            packets = read_packets(bin_input)
            version_sum = sum(x.version_sum() for x in packets)
            print(hex_input[:4], version_sum)
            assert version_sum == expected_sum

    if SOLVING_Q1:
        hex_input, bin_input = parse_input('inputs/Day16/input.txt')
        packets = read_packets(bin_input)
        version_sum = sum(x.version_sum() for x in packets)
        print(hex_input[:4], version_sum)

    if TESTING_Q2:
        for hex_input, expected_val in [('C200B40A82', 3),
                                        ('04005AC33890', 54),
                                        ('880086C3E88112', 7),
                                        ('CE00C43D881120', 9),
                                        ('D8005AC2A8F0', 1),
                                        ('F600BC2D8F', 0),
                                        ('9C005AC2F8F0', 0),
                                        ('9C0141080250320F1802104A08', 1)]:
            bin_input = deque((bt for h in hex_input for bt in hex_to_bin[h]))
            packet = read_single_packet(bin_input)
            calculated_value = packet.calculate()
            print(hex_input[:4], calculated_value)
            assert calculated_value == expected_val

    if SOLVING_Q2:
        hex_input, bin_input = parse_input('inputs/Day16/input.txt')
        packet = read_single_packet(bin_input)
        val = packet.calculate()
        print(hex_input[:4], val)
