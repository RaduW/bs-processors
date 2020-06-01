import functools
from typing import Callable, Any, List, Sequence

from bs_processors.processor_util import single_to_multiple
from bs_processors.xml_util import set_new_children, process_children, copy_element_type


def single_filter_proc(should_filter: Callable[[Any], bool], elm) -> List[Any]:
    """
    Conditionally filters an element based on the passed predicate
    :param should_filter: predicate that returns True if the element should be filtered
    :param elm: the element to check
    :return: an empty array if the element should be filtered or an array with the passed element

    >>> def should_filter(elm):
    ...     if elm.name in ['span', 'a']:
    ...         return True
    ...     return False
    ...
    >>> from bs4 import BeautifulSoup as bs
    >>> doc = bs('<html><div>a<span>b</span> <a></div> <p><span>x</span></p><a></html>')
    >>> filtered = single_filter_proc(should_filter, doc.html)
    >>> filtered
    [<html><body><div>a </div> <p></p></body></html>]

    """
    if should_filter(elm):
        return []
    else:
        new_children = process_children(lambda child: single_filter_proc(should_filter, child), elm)
        set_new_children(elm, new_children)

        return [elm]


def filter_factory(should_filter):
    return single_to_multiple(functools.partial(single_filter_proc, should_filter))


def single_unwrap_proc(should_unwrap: Callable[[Any], bool], elm) -> List[Any]:
    """
    Conditionally unwraps an element and pushes all its unwrapped children to its parent

    :param should_unwrap: predicate that returns true if the element should be unwrapped
    :param elm: the element to be conditionally unwrapped
    :return: either a list containing the element (if it wasn't unwrapped) or a list with all
     the unwrapped children

    >>> from bs4 import BeautifulSoup
    >>> def should_unwrap(elm):
    ...     return elm.name == "x"
    ...

    >>> doc = "<root><x >hello</x> after x <b> in b</b></root>"
    >>> elm = BeautifulSoup(doc, "xml")
    >>> # single_unwrap_proc(should_unwrap, elm.root)
    [<root>hello after x <b> in b</b></root>]

    >>> doc = "<root><x >hello <a> in a</a></x></root>"
    >>> elm = BeautifulSoup(doc, "xml")
    >>> single_unwrap_proc(should_unwrap, elm.root)
    [<root>hello <a> in a</a></root>]

    >>> doc = "<root><x >hello <a> in a <x>in x2</x> after</a></x> 22 <b>in b</b> end</root>"
    >>> elm = BeautifulSoup(doc, "xml")
    >>> single_unwrap_proc(should_unwrap, elm.root)
    [<root>hello <a> in a in x2 after</a> 22 <b>in b</b> end</root>]
    """

    # Note: elm.unwrap() would do the job but the return value is not
    # what I need (it is the node that was unwrapped instead of the
    # children) so we need to do it manually
    new_children = process_children(lambda child: single_unwrap_proc(should_unwrap, child), elm)

    if not should_unwrap(elm):
        set_new_children(elm, new_children)
        return [elm]

    # insert the new children in the parent
    # TODO see if I need to do it this way !!!
    current = elm
    for child in new_children:
        current.insert_after(child)
        current = child
    elm.extract()  # remove current element
    return new_children


def unwrap_factory(should_unwrap):
    return single_to_multiple(functools.partial(single_unwrap_proc, should_unwrap))


def single_flatten_proc(flatten_children: Callable[[Any], bool], is_internal: Callable[[Any], bool], elm) -> List[Any]:
    """
    Flattens an element pulling out 'block' like elements that 'want' to be top level

    :param flatten_children: Predicate that specifies whether the direct children of the current element can be
        flatten (i.e. taken outside of this element) (e.g. html, body and a do not allow their children to escape
        outside)
    :param is_internal: Predicate that specifies whether a child 'wants' to stay inside its parent or not (i.e.
        whether a child behaves like a block and wants out or an inline and stays in)
    :param elm: the element to be flatten
    :return: a list of flattened elements

    >>> from bs4 import BeautifulSoup
    >>> def flatten_children(elm):
    ...     if elm.name is None or elm.name in {'a', 'body', 'html'}:
    ...         return False
    ...     return True
    ...
    >>> def is_internal(elm):
    ...     if elm.name is None:
    ...         return True
    ...     if elm.name in { 'div', 'p', 'br'}:
    ...         return False
    ...     if elm.name == 'a' and "block_a" in elm['class']:
    ...         return False
    ...     return True
    ...

    >>> doc = '<div id="1"> a <br id="2"> b</div>'
    >>> s = BeautifulSoup(doc, "html.parser")
    >>> elm = s.div
    >>> single_flatten_proc(flatten_children, is_internal, elm)
    [<div id="1"> a </div>, <br id="2"/>, <div> b</div>]

    >>> doc = '<div id="1"><i>it</i><br id="2"><b></b></div>'
    >>> s = BeautifulSoup(doc, "html.parser")
    >>> elm = s.div
    >>> single_flatten_proc(flatten_children, is_internal, elm)
    [<div id="1"><i>it</i></div>, <br id="2"/>, <div><b></b></div>]

    >>> doc = '<div id="1">a<a class="block_a">b</a>c</div>'
    >>> s = BeautifulSoup(doc, "html.parser")
    >>> elm = s.div
    >>> single_flatten_proc(flatten_children, is_internal, elm)
    [<div id="1">a</div>, <a class="block_a">b</a>, <div>c</div>]

    >>> doc = '<div id="1"><a class="block_a"><div>inside a</div></a></div>'
    >>> s = BeautifulSoup(doc, "html.parser")
    >>> elm = s.div
    >>> single_flatten_proc(flatten_children, is_internal, elm)
    [<div id="1"></div>, <a class="block_a"><div>inside a</div></a>]
    """
    new_children = process_children(lambda child: single_flatten_proc(flatten_children, is_internal, child), elm)

    if not flatten_children(elm):
        # all children should go inside
        set_new_children(elm, new_children)
        return [elm]

    elm.clear()
    # this element pops out external children
    # remember the current parent
    parent = elm

    result = []
    for child in new_children:
        if is_internal(child):
            if parent is None:
                # we need a new element like elm
                parent = copy_element_type(elm)
            parent.append(child)
        else:
            # we need to pop the element at a higher level, if we have a valid parent
            # append it first
            if parent is not None:
                result.append(parent)
                parent = None
            result.append(child)

    if parent is not None:
        result.append(parent)

    return result


def flatten_factory(flatten_children, is_internal):
    return single_to_multiple(functools.partial(single_flatten_proc, flatten_children, is_internal))


def single_local_modify(modify_func: Callable[[Any], bool], elm):
    """

    :param modify_func:
    :param elm:
    :return:
    """
    modify_func(elm)
    process_children(lambda child: single_local_modify(modify_func, child), elm)
    return [elm]


def local_modify_factory(modify_func):
    return single_to_multiple(functools.partial(single_local_modify, modify_func))


def single_join_children(join_children: Callable[[Any, Any], Any], elm):
    new_children = process_children( join_children, elm)

    def reducer(accumulator, new_child):
        if len(accumulator) > 0:
            # try to see if we can join the last child with the new child
            result = accumulator[:-1] + list(join_children(accumulator[-1], new_child))
        else:
            # this is the first element just store it (noting to join it to)
            result = [new_child]
        return result

    # try to join adjacent children
    joined_children = functools.reduce(reducer, new_children, [])
    set_new_children(elm, joined_children)
    return [elm]


def join_children_factory(join_children):
    return single_to_multiple(functools.partial(single_join_children, join_children))


def lateral_effect(lateral_effect_func, elms: Sequence[Any]) -> Sequence[Any]:
    lateral_effect_func()
    return elms


def lateral_effect_factory(lateral_effect_func):
    return functools.partial(lateral_effect, lateral_effect_func)
