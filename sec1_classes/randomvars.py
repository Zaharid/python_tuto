"
randomvars.py

A framework to study random variables
"""
import random


class Variable:
    def __init__(self, name):
        self.name = name

    def sample(self):
        raise NotImplementedError()

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
