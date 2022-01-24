from collections import deque
from enum import Enum

hex_to_bin = {'0': '0000', '1': '0001', '2': '0010', '3': '0011', '4': '0100', '5': '0101', '6': '0110', '7': '0111',
              '8': '1000', '9': '1001', 'A': '1010', 'B': '1011', 'C': '1100', 'D': '1101', 'E': '1110', 'F': '1111'}


def prod(*args):
    val = 1
    for arg in args:
        val = val * arg
    return val


def gt(*args):
    assert len(args) == 2
    return args[0] > args[1]


def lt(*args):
    assert len(args) == 2
    return args[0] < args[1]


def eq(*args):
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
    def __init__(self, version: int, typeid: int, value=None, subpackets=None):
        self.version = version
        self.typeid = typeid
        if self.typeid == TypeID.LITERAL.value:
            if value is not None:
                self.value = value
            else:
                raise TypeError(version, typeid, value, subpackets)
        else:
            if subpackets is not None:
                self.subpackets = subpackets
            else:
                raise TypeError(version, typeid, value, subpackets)

    def __str__(self):
        return f"(Ver:{self.version} Type:{self.typeid} Contains:{self.value if self.value is not None else self.subpackets})"

    def __repr__(self):
        return str(self)

    def calculate(self):
        if self.typeid == TypeID.LITERAL.value:
            return self.value
        else:
            return id_to_fn[self.typeid]([x.calculate() for x in self.subpackets])

    def version_sum(self):
        if self.typeid == TypeID.LITERAL.value:
            return self.version
        else:
            return self.version + sum(x.version_sum() for x in self.subpackets)


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
        return Packet(version, typeID, value=number)
    else:
        len_typeID = binary.popleft()
        if len_typeID == '0':
            length = int(mpopleft(binary, 15), base=2)
            sub_packets_bin = deque()
            for _ in range(length):
                sub_packets_bin.append(binary.popleft())
            subpackets = read_packets(sub_packets_bin)
            return Packet(version, typeID, subpackets=subpackets)
        if len_typeID == '1':
            num_subpackets = int(mpopleft(binary, 11), base=2)
            subpackets = [read_single_packet(binary) for _ in range(num_subpackets)]
            return Packet(version, typeID, subpackets=subpackets)


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
TESTING_Q2 = True

if __name__ == '__main__':
    if TESTING_Q1:
        for input_file in ['inputs/Day16/test16.txt',
                           'inputs/Day16/test12.txt',
                           'inputs/Day16/test23.txt',
                           'inputs/Day16/test31.txt']:
            hex_input, bin_input = parse_input(input_file)
            packets = read_packets(bin_input)
            version_sum = sum(x.version_sum() for x in packets)
            print(hex_input[:4], version_sum)

    if SOLVING_Q1:
        hex_input, bin_input = parse_input('inputs/Day16/input.txt')
        packets = read_packets(bin_input)
        version_sum = sum(x.version_sum() for x in packets)
        print(hex_input[:4], version_sum)

    if TESTING_Q2:
        for hex_input in ['C200B40A82',
                          '04005AC33890',
                          '880086C3E88112',
                          'CE00C43D881120',
                          'D8005AC2A8F0',
                          'F600BC2D8F',
                          '9C005AC2F8F0',
                          '9C0141080250320F1802104A08']:
            bin_input = deque((bt for h in hex_input for bt in hex_to_bin[h]))
            packet = read_single_packet(bin_input)
            print(hex_input[:4], packet.calculate())
