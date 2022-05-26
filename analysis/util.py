from operator import itemgetter
import random


def count(hist):
    return sum(map(itemgetter(1), hist))

def median(hist):
    tot = sum(map(itemgetter(1), hist))
    count = 0
    pos = (tot + 1) / 2 if tot % 2 > 0 else (tot) / 2

    for value, occurences in hist:
        count += occurences
        if count >= pos:
            return value

def mean(hist):
    num = 0
    sum_ = 0
    for value, occurences in hist:
        sum_ += value*occurences
        num += occurences
    return sum_/num

def std(hist, mu):
    num = 0
    sum_ = 0
    for value, occurences in hist:
        sum_ += ((value-mu)**2) * occurences
        num += occurences
    return (sum_/num)**0.5

def cov(hist):
    mu = mean(hist)
    sigma = std(hist, mu)

    return sigma/mu

def rand(hist):
    seq = list(map(itemgetter(0), hist))
    weights = list(map(itemgetter(1), hist))
    return random.choices(seq, weights=weights)[0]

def tosec(value, scoreunit):
    unit = scoreunit.split('/')[0]
    if unit == 'ns':
        value = value / 10**9
    elif unit == 'us':
        value = value / 10**6
    elif unit == 'ms':
        value = value / 10**3

    return value

def overlap(ci1, ci2):
    return not (ci1[1] < ci2[0] or ci1[0] > ci2[1])

def arpc(ci):
    lb, ub = ci
    if lb <= 1 <= ub:
        return 0
    center = (lb + ub)/2
    return abs(center - 1)