""" generator processor

Utilities to compose generators

"""
from functools import reduce


def process(elm, processors):
    """
    Processes an element through a list of processors.
    Loosely process(elm, [p1,p2]) is p1(p2(elm) ... but
    this needs work with processors that are generators
    so the composition is applied for all elements of the
    previous processor
    :param elm: the elment to be processed (like an html elm)
    :param processors: a list of generator functions the last one
    taking a list (iterator) of elements
    :return: a generator of elements

    >>> from pprint import pprint
    >>> def p1(elm):
    ...     yield "p1-1 {}".format(elm)
    ...     yield "p1-2 {}".format(elm)
    ...
    >>> def p2(elm):
    ...     yield "p2-1 {}".format(elm)
    ...     yield "p2-2 {}".format(elm)
    ...
    >>> def p3(elm):
    ...     yield "p3-1 {}".format(elm)
    ...     yield "p3-2 {}".format(elm)
    >>> def p_empty(elm):
    ...     return []
    >>> result = process('xXx', [p1,p2])
    >>> [x for x in result]
    ['p2-1 p1-1 xXx', 'p2-2 p1-1 xXx', 'p2-1 p1-2 xXx', 'p2-2 p1-2 xXx']
    >>> result = process('xXx', [p1,p2,p3])
    >>> pprint([x for x in result])
    ['p3-1 p2-1 p1-1 xXx',
     'p3-2 p2-1 p1-1 xXx',
     'p3-1 p2-2 p1-1 xXx',
     'p3-2 p2-2 p1-1 xXx',
     'p3-1 p2-1 p1-2 xXx',
     'p3-2 p2-1 p1-2 xXx',
     'p3-1 p2-2 p1-2 xXx',
     'p3-2 p2-2 p1-2 xXx']
    >>> result = process('xXx', [p1,p2,p_empty])
    >>> [x for x in result]
    []

    """
    # apply functions in the given order so we need
    # to compse them in reverse order
    procs = reversed(processors)
    processing_fn = reduce(compose_generators, procs)
    yield from processing_fn(elm)


def compose_generators(f1, f2):
    """
    Equivalent to f1(f2(x)) but for generators

    >>> def p1(elm):
    ...     yield "p1-1 {}".format(elm)
    ...     yield "p1-2 {}".format(elm)
    ...
    >>> def p2(elm):
    ...     yield "p2-1 {}".format(elm)
    ...     yield "p2-2 {}".format(elm)
    ...
    >>> x = compose_generators(p1,p2)
    >>> [val for val in x("XXX")]
    ['p1-1 p2-1 XXX', 'p1-2 p2-1 XXX', 'p1-1 p2-2 XXX', 'p1-2 p2-2 XXX']
    """
    def composed(x):
        for elm in f2(x):
            yield from f1(elm)
    return composed
