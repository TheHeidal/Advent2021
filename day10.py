opening = ['(', '[', '{', '<']
closing = [')', ']', '}', '>']
score_corr = {')': 3, ']': 57, '}': 1197, '>': 25137}
score_comp = {'(': 1, '[': 2, '{': 3, '<': 4}


def matches(a, b):
    return opening.index(a) == closing.index(b)


def score_corrupted(line):
    expected = []
    for char in line:
        if char in opening:
            expected.append(char)
        elif char in closing:
            if matches(expected[-1], char):
                expected.pop(-1)
            else:
                return score_corr[char]
    return 0


def get_completion(line):
    expected = []
    for char in line:
        if char in opening:
            expected.append(char)
        elif char in closing:
            if matches(expected[-1], char):
                expected.pop(-1)
            else:
                return []
    return expected


def score_completion(line):
    score = 0
    for i in range(len(line)-1, -1, -1):
        score = (score * 5) + score_comp[line[i]]
    return score

if __name__ == "__main__":
    test = 2
    f = open("inputs/Day10/D10.txt", 'r')
    data = [l.strip() for l in f.readlines()]
    f.close()
    if test == 1:
        scores = (score_corrupted(l) for l in data)
        print(sum(scores))
    if test == 2:
        completions_scores = [i for i in sorted([score_completion(get_completion(l)) for l in data]) if i != 0]
        print(completions_scores[len(completions_scores)//2])
