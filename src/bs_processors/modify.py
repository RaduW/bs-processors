"""
Generic modification factories.

This module contains factories that can be used to easily construct modification functions that can be
used as arguments to the local_modify function

"""
from typing import Any, Callable

from bs_processors import is_tag


def modify_if_f(modifier: Callable[[Any], None], predicate: Callable[[Any], bool]) -> Callable[[Any], None]:
    """
    Adaptor for a local modifier, it will be called only if the predicate returns True

    This modifier permits writing simple modifiers that apply their modification logic to all elements
    that they receive and delegate the selection logic to the predicate

    If, for example, we need a modifier that sets a certain class to all elements of type `p` we can create
    a modifier that sets the class to all elements that it receives and then use this function togehter with
    the `has_name_pf('p') to obtain the same result.

    :param modifier: a modifier that applies the modification to all elements it is called with
    :param predicate: a predicate that selects the elements to be modified
    :return: a modifier that applies the modification to the elements selected by the predicate

    >>> from bs4 import BeautifulSoup
    >>> from bs_processors.predicate import has_name_pf
    >>> from bs_processors.generic_processors import local_modify_factory
    >>> doc = '<html><span>s1</span><span class="c1">s2</span><div><span>s3</span></div></html>'
    >>> s = BeautifulSoup(doc, 'html.parser')
    >>> is_span = has_name_pf('span')
    >>> def modifier(elm):
    ...     clss = elm.get('class')
    ...     if clss is not None:
    ...         clss.append("my_class")
    ...     else:
    ...         elm['class'] = 'my_class'
    >>> modif_span = modify_if_f( modifier, is_span)
    >>> processor = local_modify_factory(modif_span)
    >>> result = processor([s])
    >>> result[0]
    <html><span class="my_class">s1</span><span class="c1 my_class">s2</span><div><span \
class="my_class">s3</span></div></html>
    """

    def inner(element):
        if predicate(element):
            modifier(element)


    return inner


def toggle_class(class_name_gen):
    """
    Toggles a class on a HTML element

    **Important**: this works with the assumption that the element is processed with 'html.parser' or something
    similar, that is the 'class' attribute is a list of classes. If processing with the 'html' parser the 'class'
    attribute is treated as a simple string and toggle_class will not function correctly.

    * **class_name_gen**: something that can be converted into a class name
        * st4 the string is the class name
        * Callable[[Any], str] a function that receives an element and returns a string, the class name to be toggled
    * **return**: a local modification function ( a function that can be applied on an element)

    >>> from bs4 import BeautifulSoup
    >>> doc = '<html><div></div><span id="1" class="s1 s2"/><span><p  class="a1"/><p></html>'
    >>> x = BeautifulSoup(doc, 'html.parser')
    >>> tc = toggle_class('bubu')
    >>> tc(x.div)
    >>> x.div
    <div class="bubu"></div>
    >>> tc(x.div)
    >>> x.div
    <div class=""></div>
    >>> tc(x.span)
    >>> x.span
    <span class="s1 s2 bubu" id="1"></span>
    >>> tc(x.span)
    >>> x.span
    <span class="s1 s2" id="1"></span>
    >>> tc(x.p)
    >>> x.p
    <p class="a1 bubu"></p>
    >>> tc(x.p)
    >>> x.p
    <p class="a1"></p>
    >>> class_name_gen = lambda x: x.name
    >>> tc = toggle_class(class_name_gen)
    >>> tc(x.div)
    >>> x.div
    <div class="div"></div>
    >>> tc(x.div)
    >>> x.div
    <div class=""></div>
    >>> tc(x.span)
    >>> x.span
    <span class="s1 s2 span" id="1"></span>
    >>> tc(x.span)
    >>> x.span
    <span class="s1 s2" id="1"></span>

    """
    class_name_gen = to_string_gen(class_name_gen)
    def inner(elm):
        if not is_tag(elm):
            return

        clss = elm.get("class")
        class_name = class_name_gen(elm)
        if clss is None:
            elm['class'] = [class_name]
        else:
            if class_name in clss:
                elm['class']= [cls for cls in clss if cls != class_name]
            else:
                clss.append(class_name)

    return inner

def remove_class(class_name_gen):
    """
    Removes a class on a HTML element

    **Important**: this works with the assumption that the element is processed with 'html.parser' or something
    similar, that is the 'class' attribute is a list of classes. If processing with the 'html' parser the 'class'
    attribute is treated as a simple string and toggle_class will not function correctly.

    * **class_name_gen**: something that can be converted into a class name
        * st4 the string is the class name
        * Callable[[Any], str] a function that receives an element and returns a string, the class name to be toggled
    * **return**: a local modification function ( a function that can be applied on an element)

    >>> from bs4 import BeautifulSoup
    >>> doc = '<html><div></div><span id="1" class="s1 s2"/><span></html>'
    >>> x = BeautifulSoup(doc, 'html.parser')
    >>> tc = remove_class('s1')
    >>> tc(x.div)
    >>> x.div
    <div></div>
    >>> tc(x.span)
    >>> x.span
    <span class="s2" id="1"></span>
    """
    class_name_gen = to_string_gen(class_name_gen)
    def inner(elm):
        if not is_tag(elm):
            return

        clss = elm.get("class")
        class_name = class_name_gen(elm)
        if clss is not None:
            elm['class']= [cls for cls in clss if cls != class_name]

    return inner

def set_class(class_name_gen):
    """
    Sets a class (does not duplicate the class if it already exists).

    Unlike add_class it will not add a class multiple times (if the class is already set it will not add it again)

    **Important**: this works with the assumption that the element is processed with 'html.parser' or something
    similar, that is the 'class' attribute is a list of classes. If processing with the 'html' parser the 'class'
    attribute is treated as a simple string and toggle_class will not function correctly.

     * **class_name_gen**: something that can be converted into a class name
        * st4 the string is the class name
        * Callable[[Any], str] a function that receives an element and returns a string, the class name to be toggled
    * **return**: local modification function

    >>> from bs4 import BeautifulSoup
    >>> doc = '<html><div></div><span id="1" class="s1 s2"/><span></html>'
    >>> x = BeautifulSoup(doc, 'html.parser')
    >>> tc = set_class('s1')
    >>> tc(x.div)
    >>> x.div
    <div class="s1"></div>
    >>> tc(x.span)
    >>> x.span
    <span class="s1 s2" id="1"></span>
    """
    class_name_gen = to_string_gen(class_name_gen)
    def inner(elm):
        if not is_tag(elm):
            return

        clss = elm.get("class")
        class_name = class_name_gen(elm)
        if clss is None:
            elm['class'] = [class_name]
        else:
            if class_name not in clss:
                clss.append(class_name)

    return inner

def add_class(class_name_gen):
    """
    Toggles a class on a HTML element

    Unlike set_class it will add a class multiple times (if the class is already set it will add it again)

    **Important**: this works with the assumption that the element is processed with 'html.parser' or something
    similar, that is the 'class' attribute is a list of classes. If processing with the 'html' parser the 'class'
    attribute is treated as a simple string and toggle_class will not function correctly.

    * **class_name_gen**: something that can be converted into a class name
        * st4 the string is the class name
        * Callable[[Any], str] a function that receives an element and returns a string, the class name to be toggled
    * **return**: a local modification function ( a function that can be applied on an element)

    >>> from bs4 import BeautifulSoup
    >>> doc = '<html><div></div><span id="1" class="s1 s2"/><span></html>'
    >>> x = BeautifulSoup(doc, 'html.parser')
    >>> tc = add_class('s1')
    >>> tc(x.div)
    >>> x.div
    <div class="s1"></div>
    >>> tc(x.span)
    >>> x.span
    <span class="s1 s2 s1" id="1"></span>
    >>> tc(x.span)
    >>> x.span
    <span class="s1 s2 s1 s1" id="1"></span>
    """

    class_name_gen = to_string_gen(class_name_gen)
    def inner(elm):
        if not is_tag(elm):
            return

        clss = elm.get("class")
        class_name = class_name_gen(elm)
        if clss is None:
            elm['class'] = [class_name]
        else:
            clss.append(class_name)

    return inner


def change_tag_name(tag_name_gen):
    """
    Changes the tag name of a tag (e.g. change `div` to `p`)


    * **tag_name_gen**: something that can be converted into a class name
        * st4 the string is the new tag name
        * Callable[[Any], str] a function that receives an element and returns a string, the new tag name to be set
    * **return**: a local modification function ( a function that can be applied on an element)

    >>> from bs4 import BeautifulSoup
    >>> doc = '<html><div></div><span id="1" class="s1 s2"></span></html>'
    >>> x = BeautifulSoup(doc, 'html.parser')
    >>> tc = change_tag_name('p')
    >>> tc(x.div)
    >>> x
    <html><p></p><span class="s1 s2" id="1"></span></html>
    >>> tc(x.span)
    >>> x
    <html><p></p><p class="s1 s2" id="1"></p></html>
    """
    tag_name_gen = to_string_gen(tag_name_gen)
    def inner(elm):
        if not is_tag(elm):
            return

        elm.name = tag_name_gen(elm)

    return inner


def to_string_gen(gen) -> Callable[[Any], str]:
    """
    Accepts a string or a function that returns a string and returns a function that returns a string

    :param gen: either the string to be returned or a generator that accepts an element and returns a string
    :return:  a string generator that accepts an element

    >>> s_gen = to_string_gen("some_constant")
    >>> s_gen(1)
    'some_constant'
    >>> s_gen("hello")
    'some_constant'
    >>> echo_gen = to_string_gen( lambda x: str(x))
    >>> echo_gen(1)
    '1'
    >>> echo_gen("hello")
    'hello'
    """
    if gen is None:
        return lambda x: ""
    if isinstance(gen, str):
        return lambda x: gen
    else:
        return gen

