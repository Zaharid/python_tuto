% Advanced Python tutorial
% Zahari Kassabov

# Introduction

The fact that Python allows a great amount of customization of various language
constructs, which allow to write libraries with peculiar semantics such as numpy
that however can be integrated together,  is a large component to the success of
Python. The objective of this tutorial is to explore how this customization
works.

The tutorial assumes you have some experience using Python to manipulate
elemental data structures like lists and dictionaries. It it focused instead on
more advanced constructs, mostly related to the Object Oriented Programming
features of the language. These may be useful to understand a bit better how to
read and write *framework code*, where one uses these advanced facilities to
provide convenient interfaces for certain domain specific tasks.

We are not going to focus on how to use a specific libraries, or even how to
build anything mildly useful, but rather on the language building blocks that
might be used to do so. For this reason, following this tutorial doesn't require
anything but a basic Python 3.6+ interpreter and some text editor.

One useful resource for reference is the [Data Model chapter of the Python
reference](https://docs.python.org/3/reference/datamodel.html).

Therefore the tutorial is going to revolve around a mostly dummy project:
`randomvars`.

## Random variables

I find useful to think about probability in terms of [Random
Variables](https://en.wikipedia.org/wiki/Random_variable). One may think of
those in several ways, but one I find particularly useful is as things that have
a `sample()` method, which every time you call it returns a potentially
different thing in some domain. This is a very general view but not one
particularly amenable to analytical treatment other than through Monter Carlo
methods. Good thing that this is what we are doing.

If we further restrict our attention to [independent and identically distributed
random
variables](https://en.wikipedia.org/wiki/Independent_and_identically_distributed_random_variables),
then it should be possible to write the sample method as a function of [0,1] ->
Domain (through the [Quantile
function](https://en.wikipedia.org/wiki/Quantile_function)).

The example project in this tutorial is to build a simple framework that allows
to conveniently compute and express statistics over functions of random
variables in various ways. For example, if X and Y are [standard
normal](https://en.wikipedia.org/wiki/Normal_distribution#Standard_normal_distribution)
random variables, and U and V are [standard
uniform](https://en.wikipedia.org/wiki/Uniform_distribution_%28continuous%29#Standard_uniform),
then we want to compute things like the probability of `U**X + V**(X+Y) < 5`
restricted to the cases where `X+Y>1`, but above all, we want a convenient way
to represent such ideas.

# Classes and instances

Note: The code for this part is at `sec1_classes/randomvars.py`.

It looks quite natural to represent a random variable in the sense discussed
above as an *object*. We might start off with a code like

```python
"""
randomvars.py

A framework to study random variables
"""
import random


class Variable:
    def __init__(self, name):
        self.name = name

    def sample(self):
        raise NotImplementedError()


class Uniform(Variable):
    """A standard uniform random variable"""

    def sample(self):
        return random.random()


class Normal(Variable):
    """A standard normal random variable"""

    def sample(self):
        return random.normalvariate(0, 1)
```


With this we can do things like:

```python
In [1]: import randomvars                                                                                             

In [2]: X = randomvars.Normal('X')                                                                                    

In [3]: X                                                                                                             
Out[3]: X

In [4]: X.sample()                                                                                                    
Out[4]: -1.5988501812175056

In [5]: U = randomvars.Uniform('U')                                                                                   

In [6]: U                                                                                                             
Out[6]: U

In [7]: U.sample()                                                                                                    
Out[7]: 0.3154243631396576
```

In general one customizes Python objects by
overwriting *dunder* methods (for *double underscore*). As we will see in some
detail, `__init__` is called when an object is created, and `__repr__` is used
to specify how an object will look when printed in the interpreter (and also, by
default, how it will be converted to a string).


You might have seen code like this before, but now it is the time to look at it
in some detail. To zeroth order approximation, a *class* is a fancy dictionary.
In fact we can look at the corresponding dict like object with the `__dict__`
attribute:

```python
In [8]: randomvars.Variable.__dict__                                                                                  
Out[8]: 
mappingproxy({'__module__': 'randomvars',
              '__init__': <function randomvars.Variable.__init__(self, name)>,
              'sample': <function randomvars.Variable.sample(self)>,
              '__repr__': <function randomvars.Variable.__repr__(self)>,
              '__dict__': <attribute '__dict__' of 'Variable' objects>,
              '__weakref__': <attribute '__weakref__' of 'Variable' objects>,
              '__doc__': None})
```

We can see the functions we defined above (`__init__`, `sample` and `__repr__`)
as well as several automatically initialized attributes. To zeroth order
approximation, using the dot operator on a class retrieves the corresponding
value from its `__dict__` (we will see that this is in fact more complicated
in a while). For example `Variable.sample` gives the same as
`Variable.__dict__['sample']` which is in turn the function `sample` that we
defined above.

## Class instances

Classes have two important functionalities on top of being a dict. The first is
the ability to create *instances* (or *objects*), which is typically achieved by
calling the class object. Class instances can also be thought as dicts with more
functionality built on top.

```python
In [17]: X = randomvars.Normal('X')                                                                                   

In [18]: X                                                                                                            
Out[18]: X

In [19]: X.__dict__                                                                                                   
Out[19]: {'name': 'X'}
```

The dot operator of an instance also looks into the `__dict__`, e.g. we have
that `X.name == 'X'`. When an instance doesn't find an attribute in its
`__dict__`, it tries to resolve it from its generating class.  For example
`__doc__` doesn't exist in the `__dict__` of the instance `X`, but it exists in
the `__dict__` of its generating class (it was generated based on the string
below the class definition), and so  we have `X.__doc__ == 'A standard normal
random variable'`. It is possible to retrieve the class that defined a given
object using `type(obj)` or `obj.__class__`.

Note: Classes are objects themselves and the class they look at to find
attributes is called *metaclass*. These implement things like the object
creation machinery (e.g. the `__call__` method of classes), and can in principle
be customized, although typically there are easier mechanisms to achieve the
same goals.

## Bound methods

An important special case is that functions in the class
definitions are automatically converted to the so called *bound method* when
viewed as an instance attribute. We have:

```python
In [22]: X.sample                                                                                                     
Out[22]: <bound method Normal.sample of X>
```

which is not the same as:

```python
In [30]: randomvars.Normal.sample                                                                                     
Out[30]: <function randomvars.Normal.sample(self)>
```

In bound methods, the first argument of the corresponding function is replaced
with the calling instance, so we have that `instance.method(arguments)` is
usually equivalent to `type(instance).method(instance, arguments)`. By
convention, we call the first argument of class methods `self`.

Note: this mechanism can be altered with the `@staticmethod` and `@classmethod`
decorator. `@staticmethod` makes the instance lookup return something
equivalent to the actual class function, without any argument substitution, and
`@aclassmethod` caused the first argument to be replaced by the instance's class
rather that the instance itself. Static methods may be used for simple utility
functions that are tightly associated to the class and yet don't need to know
about the instance, while `@classmethods` can be used to implement alternate
constructor.

### Inheritance

The second important functionality of a class is that one can compose the code of
several class with the *inheritance* mechanism. It is the basis of the Object
Oriented Programming. When a class cannot find an attribute in its `__dict__`,
it looks in that of its parent classes. When we write something like `class
Normal (Variable):`, we are specifying that when some attribute is not found in
the `Normal` class, the `Variable` class should be looked up next.

In general, the lookup order may be seen with the `__mro__` attribute of a class
(which stands for *Method Resolution Order*). For example:

```python
In [32]: randomvars.Normal.__mro__                                                                                    
Out[32]: (randomvars.Normal, randomvars.Variable, object)
```

We see the simple hierarchy we have specified as well as `object` in the end,
which is the base class for all Python objects and implements things like for
example a default repr. In general we can specify multiple classes as parents
for a given class, and the way that the mro ends up being computed in the most
general case is [rather non
trivial](https://www.python.org/download/releases/2.3/mro/). However it
ends up doing what you expect in most cases. We will not be doing complicated
hierarchy trees relations here.

We can now see how the initialization of `X` worked in some detail: `X =
Normal('X')` causes the `Normal` *instance* to try to find an attribute called
`__init__` right after being constructed. This is not defined in the instance
dict (which at that point is empty) and also not in the calling class, `Normal`,
so we go up in the method resolution order of `Normal` and find it in the
`Variable` class. Because it is a class function, `__init__` is converted to a
bound method. This is then called with the name as second argument, and the
instance itself as an implicit first argument. The name is put into the instance
dict using `self.name = name`.

# Overloading operations

Note: The code for this part is at `sec2_operators/randomvars.py`.

We have enough functionality to compute basic statistics on random variables.
For example, we might write a function to compute the expected value as follows:

```python
def nexpected(x, n=1000):
    """Compute the expected value of ``x`` based on ``n`` samples"""
    return sum(x.sample() for _ in range(n))/n
```

This allows as to do things like:

```python
In [3]: import randomvars as v                                                  

In [4]: v.nexpected(v.Normal('X'))                                              
Out[4]: 0.022245415256444166

In [5]: v.nexpected(v.Normal('X'), n=100_000)                                   
Out[5]: 0.0018759199081148188
```

which is not all that exciting. We would like to be able to compute expected
values (and other statistics) over various functions of random variables over
various functions of random variables, starting from for example `X + Y` or `X +
1`. This suggests that we should be able to use `sample` on something more
general than a `Varaible`, which we are going to call `Expression`. In typical
object oriented design fashion, we are going to make `Variable` a subclass of
`Expression`:

```python
class Expression:
    def sample(self):
        raise NotImplementedError()


class Variable(Expression):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name
```

Now classes like `Normal` and `Uniform` will look into `Expression` for
attributes:
```python
In [6]:  v.Normal.__mro__                                                                                             
Out[6]: (randomvars.Normal, randomvars.Variable, randomvars.Expression, object)
```

That is not very useful at the moment, since the only attribute we are defining
is `sample`, which is overwritten by both derived classes.

## Implementing Add

The idea is that if we know how to sample from two expressions, then we know how
to sample from the sum of them. Similarly sampling from the sum of an expression
and a constant is easy enough.

```python
class Add(Expression):
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
        return lval + rval

    def __repr__(self):
        return f'{self.left} + {self.right}'
```

with this, we can have things like:

```python

In [11]: Z = v.Add(v.Normal('X'), v.Normal('Y'))                                                                      

In [12]: Z                                                                                                            
Out[12]: X + Y

In [13]: v.nexpected(Z)                                                                                               
Out[13]: -0.0007016267420245575

In [14]: Z = v.Add(v.Normal('X'), 10000)                                                                              

In [15]: v.nexpected(Z)                                                                                               
Out[15]: 10000.047671280006

```

We can enable the `+` symbol to do what we want by implementing the `__add__`
dunder method of `Expression`:

```python
class Expression:
    def __add__(self, other):
        return Add(self, other)

    def sample(self):
        raise NotImplementedError()
```

The way Python processes `a + b` is roughly as follows: First look at the type
of `a`, see if it has and `__add__` method. If that is the case, the method is
called and the result is returned, unless it happens to be the constant
`NotImplemented`. If that is the case, or if the type of `a` doesn't implement
`__add__`, see if `b` has an `__radd__` method. If that one exists and calling
it with `a` as an argument doesn't return `NotImplemented`, then return the
result. Otherwise raise an error.

This means, that at the moment we can do:

```python
n [17]: X = v.Normal('X')                                                                                            

In [18]: Y = v.Normal('Y')                                                                                            

In [19]: X + Y                                                                                                        
Out[19]: X + Y
```

and

```python
In [20]: X + 1                                                                                                        
```

but not

```python

In [21]: 1 + X                                                                                                        
---------------------------------------------------------------------------
TypeError                                 Traceback (most recent call last)
<ipython-input-21-2af25225b693> in <module>
----> 1 1 + X

TypeError: unsupported operand type(s) for +: 'int' and 'Normal'
```

For the last one to work, we write the `__radd__` method:

```python
    def __radd__(self, other):
        return Add(other, self)
```

Note the reverse order of the arguments in Add.

## Implementing other binary operations

There are [a
bunch](https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types)
of binary operations we can implement in the same fashion. We could do that by
copying the `Add` class and slightly modifying it to do other operations such as
difference and multiplication. However we can use inheritance again to abstract
away the common functionality and specialise only where required. Note that the
only things that are specific to the sum operation in the `Add` class are the
last line of `sample` and the `__repr__`. We move everything else to a
`BinaryOp` base class:

```python
import operator

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

```

The `operator` module contains definitions of the various binary operations.
This avoids us having to write something like `op = lambda a,b : a+b`, which in
fact wouldn't work because it would also need a `self` argument (can you see
why?).

Note that we have added parentheses around the repr, which will become useful as
we get more complicated expressions.