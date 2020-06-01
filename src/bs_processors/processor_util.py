"""
Generic util for processors
"""
from typing import Sequence, Callable, Any, List


def join(processors: Sequence[Callable[[List[Any]], List[Any]]])-> Callable[[List[Any]], List[Any]]:
    """
    Creates a processor from a list of processor.
    The processor created is equivalent to applying each of the passed processor
    in sequence over the result of the previous processor (after the result is
    flattened)
    :param processors: a list of processors
    :return: a join processor

    >>> def double( elms):
    ...     result = []
    ...     for elm in elms:
    ...         result += [elm, elm]
    ...     return result
    ...
    >>> def add_one( elms):
    ...     result = []
    ...     for elm in elms:
    ...         result.append(elm + 1)
    ...     return result
    ...
    >>> pr = join([add_one, double])
    >>> pr( [1,100])
    [2, 2, 101, 101]
    >>> pr = join([double, add_one])
    >>> pr([1, 100])
    [2, 2, 101, 101]
    >>> pr = join([double, add_one, double])
    >>> pr([1, 100])
    [2, 2, 2, 2, 101, 101, 101, 101]
    """
    def inner(elms):
        result = elms
        for processor in processors:
            result = processor(result)
        return result
    return inner


def single_to_multiple(processor: Callable[[Any], List[Any]])->Callable[[List[Any]], List[Any]]:
    """
    Converts a processor that handles one element and returns a list of elements into
    a processor that handles a list of elements and returns a list of elements by calling
    each element in the list in turn and joining the intermediate results into one result
    :param processor: a processor that operates on one element
    :return: a processor that operates on a list of elements

    >>> def square_pair(x):
    ...     return[x , x*x]
    >>> mult = single_to_multiple(square_pair)
    >>> mult([1,2,3,4])
    [1, 1, 2, 4, 3, 9, 4, 16]
    """

    def inner( elms: List[Any])-> List[Any]:
        result = []
        for elm in elms:
            if elm is not None:
                result += processor(elm)
        return result

    return inner

