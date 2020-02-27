from random import randint

def sum(x,n):
    return sum(randint(1, x) for _ in range(n))

def dice(x,n):
    return [randint(1, x) for _ in range(n)]