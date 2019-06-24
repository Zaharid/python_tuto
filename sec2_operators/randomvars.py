"""
randomvars.py

A framework to study random variables
"""
import operator
import random


class Expression:
    def __add__(self, other):
        return Add(self, other)

    def __radd__(self, other):
        return Add(other, self)

    def sample(self):
        raise NotImplementedError()


class Variable(Expression):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


class Uniform(Variable):
    """A standard uniform random variable"""

    def sample(self):
        return random.random()


class Normal(Variable):
    """A standard normal random variable"""

    def sample(self):
        return random.normalvariate(0, 1)


class BinaryOp(Expression):
    op = None  # To be specizliced

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def sample(self):
        if hasattr(self.left, 'sample'):
            lval = self.left.sample()
        else:
            lval = self.left
        if hasattr(self.right, 'sample'):
            rval = self.right.sample()
        else:
            rval = self.right
        return self.op(lval, rval)


class Add(BinaryOp):
    op = operator.add

    def __repr__(self):
        return f'({self.left} + {self.right})'


def nexpected(x, n=1000):
    """Compute the expected value of ``x`` based on ``n`` samples"""
    return sum(x.sample() for _ in range(n)) / n
