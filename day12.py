class Cave:
    """
    represents a cave.
        name is the string that is the cave's key in the dict
        connected is a list of strings that are keys to connected caves
        large is whether this cave is large or small
    """

    def __init__(self, name, connected):
        self.name = name
        self.connected = [x for x in connected if x != name]
        self.large = name.isupper()

    def extend(self, connected):
        self.connected.extend([x for x in connected if x != self.name])


def dfs1(curr_cave: str, path: list):
    if curr_cave == 'end':
        routes.append(path + [curr_cave])
        return
    connected = cave_dict[curr_cave].connected
    options = sorted([c for c in connected if cave_dict[c].large or c not in path])
    for o in options:
        dfs1(o, path[:] + [curr_cave])


def dfs2(curr_cave: str, path: list, dawdled: bool = False):
    if curr_cave == 'end':
        routes.append(path + [curr_cave])
        return
    if curr_cave == 'start' and 'start' in path:
        return
    connected = cave_dict[curr_cave].connected
    options = []
    for c in connected:
        if cave_dict[c].large or path.count(c) == 0:
            options.append((c, False))
        elif not dawdled and path.count(c) == 1:
            options.append((c, True))
    for o, d in options:
        dfs2(o, path[:] + [curr_cave], dawdled or d)


if __name__ == '__main__':
    f = open('inputs/Day12/D12.txt', 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
    cave_dict = {}
    for route in data:
        locations = route.split('-')
        for loc in locations:
            if loc not in cave_dict:
                cave_dict[loc] = Cave(loc, locations)
            else:
                cave_dict[loc].extend(locations)
    routes = []
    dfs2('start', [])
    print(len(routes))
