"""
randomvars.py

A framework to study random variables
"""
import operator
import random


class Expression:
    def __init__(self):
        self.unique_vars = set()

    def __add__(self, other):
        return Add(self, other)

    def __radd__(self, other):
        return Add(other, self)

    def __sub__(self, other):
        return Sub(self, other)

    def __rsub__(self, other):
        return Sub(other, self)

    def __mul__(self, other):
        return Mul(self, other)

    def __rmul__(self, other):
        return Mul(other, self)

    def __truediv__(self, other):
        return Div(self, other)

    def __rtruediv__(self, other):
        return Div(other, self)

    def __pow__(self, other):
        return Pow(self, other)

    def __rpow__(self, other):
        return Pow(other, self)

    def __lt__(self, other):
        return Lt(self, other)

    def __gt__(self, other):
        return Gt(self, other)

    def __or__(self, other):
        return Or(self, other)

    def __ror__(self, other):
        return Or(other, self)

    def __and__(self, other):
        return And(self, other)

    def __rand__(self, other):
        return And(other, self)

    def sample(self):
        # We are relying on each of unique_vars implementing sample
        # differently here.
        values = {k: k.sample() for k in self.unique_vars}
        return self.subs(values)

    def subs(self, values):
        raise NotImplementedError()


class Variable(Expression):
    def __init__(self, name):
        self.name = name
        super().__init__()
        self.unique_vars.add(self)

    def subs(self, values):
        return values.get(self, self)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.name == other.name

    def __hash__(self):
        return hash((self.__class__, self.name))

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
        super().__init__()
        left_vars = getattr(left, 'unique_vars', set())
        right_vars = getattr(right, 'unique_vars', set())
        self.unique_vars |= left_vars | right_vars

    def subs(self, values):
        if hasattr(self.left, 'subs'):
            lval = self.left.subs(values)
        else:
            lval = self.left
        if hasattr(self.right, 'subs'):
            rval = self.right.subs(values)
        else:
            rval = self.right
        if hasattr(lval, 'subs') or hasattr(rval, 'subs'):
            return self.__class__(lval, rval)
        else:
            return self.op(lval, rval)


class Add(BinaryOp):
    op = operator.add

    def __repr__(self):
        return f'({self.left} + {self.right})'


class Sub(BinaryOp):
    op = operator.sub

    def __repr__(self):
        return f'({self.left} - {self.right})'


class Mul(BinaryOp):
    op = operator.mul

    def __repr__(self):
        return f'({self.left} * {self.right})'


class Div(BinaryOp):
    op = operator.truediv

    def __repr__(self):
        return f'({self.left} / {self.right})'


class Pow(BinaryOp):
    op = operator.pow

    def __repr__(self):
        return f'({self.left} ** {self.right})'


class Lt(BinaryOp):
    op = operator.lt

    def __repr__(self):
        return f'({self.left} < {self.right})'


class Gt(BinaryOp):
    op = operator.gt

    def __repr__(self):
        return f'({self.left} > {self.right})'


class Or(BinaryOp):
    op = operator.or_

    def __repr__(self):
        return f'({self.left} | {self.right})'


class And(BinaryOp):
    op = operator.and_

    def __repr__(self):
        return f'({self.left} & {self.right})'


def nexpected(x, n=1000):
    """Compute the expected value of ``x`` based on ``n`` samples"""
    return sum(x.sample() for _ in range(n)) / n


def nprobability(x, n=1000):
    """Compute the probability of ``x`` based on ``n`` samples"""
    return sum(bool(x.sample()) for _ in range(n)) / n
