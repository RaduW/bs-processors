"""
Contains generally useful predicates to be used with Beautiful Soup objects (i.e. strings, tags, BeautifulSoup
"""
from typing import Callable, Any, Sequence

from bs_processors.xml_util import is_tag


def true_p(elm):
    """
    Returns True regardless of the argument

    >>> true_p(None)
    True
    >>> true_p(1)
    True
    """
    return True


def false_p(elm):
    """
    Returns False regardless of the argument

    >>> false_p(None)
    False
    >>> false_p(1)
    False
    """
    return False


def not_pf(predicate: Callable[[Any], bool]):
    """
    Negates the predicate
    :param predicate: predicate to be tested
    :return: the negated value returned by the predicate

    >>> p = not_pf(true_p)
    >>> p(1)
    False
    >>> p = not_pf(false_p)
    >>> p(1)
    True

    """

    def internal(elm):
        return not predicate(elm)

    return internal


def or_pf(*args: Callable[[Any], bool]):
    """
    Does a logical or of the results of the predicates, it shortcuts the processing (returns True as
    soon as one predicate succeeds). If no predicate is passed it returns False
    :param args: the predicates
    :return: a logical or of the results of the predicates applied on the passed elment

    >>> p = or_pf(true_p, true_p)
    >>> p(1)
    True
    >>> p = or_pf(true_p, false_p)
    >>> p(1)
    True
    >>> p = or_pf(false_p, true_p)
    >>> p(1)
    True
    >>> p = or_pf(false_p, false_p)
    >>> p(1)
    False
    >>> p = or_pf()
    >>> p(1)
    False

    """

    def internal(elm):
        for predicate in args:
            if predicate(elm):
                return True
        return False

    return internal


def and_pf(*args: Callable[[Any], bool]):
    """
    Does a logical and of the results of the predicates, it shortcuts the processing (returns False as
    soon as one predicate fails). If no predicate is passed it returns True
    :param args: the predicates
    :return: a logical or of the results of the predicates applied on the passed elment

    >>> p = and_pf(true_p, true_p)
    >>> p(1)
    True
    >>> p = and_pf(true_p, false_p)
    >>> p(1)
    False
    >>> p = and_pf(false_p, true_p)
    >>> p(1)
    False
    >>> p = and_pf(false_p, false_p)
    >>> p(1)
    False
    >>> p = and_pf()
    >>> p(1)
    True

    """

    def internal(elm):
        for predicate in args:
            if not predicate(elm):
                return False
        return True

    return internal


def is_tag_p(elm):
    """
    Tries to check if the element is a tag
    It checks by verifying that the element has a  not None name that is not the string '[doc]'.
    :param elm: the element to be checked
    :return: True if the element looks like a tag
    """
    if elm is not None and elm.name is not None and elm.name != "[doc]":
        return True
    return False


def is_soup_p(elm):
    """
    Tries to check if the element is a tag
    It checks by verifying that the element has a  not None name that is the string '[doc]'.
    :param elm: the element to be checked
    :return: True if the element looks like a BeautifulSoup object
    """
    return elm is not None and elm.name is not None and elm.name == "[doc]"


def is_tag_or_soup(elm):
    """
    Tries to check if the element is either a Tag or a BeautifulSoup element
    It checks by verifying that the element has a non None name.
    :param elm: the element
    :return: True if the element is either a Tag or a BeautifulSoup element
    """
    return elm is not None and elm.name is not None


def is_string(elm):
    """
    Tries to check if the element is a NavigableString
    It checks by verifying that the element has a None name
    :param elm: the element
    :return: True if the element looks like a NavigableString
    """
    return elm is not None and elm.name is None


def has_name_pf(name_p, ignore_case=True):
    """
    Predicate factory, returns true if the element name matches the pred parameter
    :param name_p: something that can be converted into a string compare predicate

    :param ignore_case: should the comparison be case sensitive (default: ignore case)
    :return:

    >>> from bs4 import BeautifulSoup
    >>> doc = '<html><span>s1</span><SPAN>s2</SPAN></html>'
    >>> s = BeautifulSoup(doc, 'xml')
    >>> e1 = s.html.span
    >>> e2 = s.html.SPAN
    >>> p1 = has_name_pf('span')
    >>> p2 = has_name_pf('span', False)
    >>> p3 = has_name_pf('x')
    >>> p4 = has_name_pf('X', False)
    >>> p1(e1)
    True
    >>> p2(e1)
    True
    >>> p1(e2)
    True
    >>> p2(e2)
    False
    >>> p3(e1)
    False
    >>> p4(e1)
    False

    """
    # pred is a string
    pred = to_string_compare_predicate(name_p, ignore_case)

    def internal(elm):
        if not is_tag_or_soup(elm):
            return False
        return pred(elm.name)

    return internal


def has_attribute_pf(attr_p):
    """
    Predicate factory that checks that the element has a particular attribute
    :param attr_p: something that can be converted to a string compare predicate
    :return: a predicate that checks if the current element has the required attribute

    >>> from bs4 import BeautifulSoup
    >>> doc = ('<html><span id="s1" class="c1 c2 c3" style="margin: 3">s1</span>'+
    ... '<div data-x="abc" id="d1">d1</div></html>')
    >>> s = BeautifulSoup(doc, 'html.parser')
    >>> e1 = s.html.span
    >>> e2 = s.html.div
    >>> p1 = has_attribute_pf("id")
    >>> p1(e1)
    True
    >>> p1(e2)
    True
    >>> p2 = has_attribute_pf(["class", "data-w"])
    >>> p2(e1)
    True
    >>> p2(e2)
    False
    >>> p3 = has_attribute_pf( lambda x: x in ["data-x","data-xx"])
    >>> p3(e1)
    False
    >>> p3(e2)
    True

    """
    pred = to_string_compare_predicate(attr_p, ignore_case=False)

    def internal(elm):
        if not is_tag(elm):
            return False
        for attr_name in elm.attrs.keys():
            if pred(attr_name):
                return True
        return False

    return internal


def has_attribute_value_pf(attr_p, value_p, ignore_case_value=False):
    """
    Predicate factory that checks that the element has an attribute that passes
    the predicate attr_p(<attribute_name>) and attr_v(<attribute_value)
    :param attr_p: something that can be converted to a string compare predicate
    :param value_p:  something that can be converted to a string compare predicate
    :return: a predicate that checks if the current element has an attribute with a specific value

    >>> from bs4 import BeautifulSoup
    >>> doc = ('<html><span id="s1" class="c1 c2 c3" style="margin: 3">s1</span>'+
    ... '<div data-x="abc" id="d1">d1</div></html>')
    >>> s = BeautifulSoup(doc, 'html.parser')
    >>> e1 = s.html.span
    >>> e2 = s.html.div
    >>> p1 = has_attribute_value_pf("id", "s1")
    >>> p1(e1)
    True
    >>> p1(e2)
    False
    >>> p2 = has_attribute_value_pf(["id", "data-w"], ["s1", "d1"])
    >>> p2(e1)
    True
    >>> p2(e2)
    True
    >>> p3 = has_attribute_value_pf( lambda x: x in ["data-x","data-xx"], "abc")
    >>> p3(e1)
    False
    >>> p3(e2)
    True

    """
    pred_a = to_string_compare_predicate(attr_p, ignore_case=False)
    pred_v = to_string_compare_predicate(value_p, ignore_case=ignore_case_value)

    def internal(elm):
        if not is_tag(elm):
            return False
        for attr_name, attr_value in elm.attrs.items():
            if pred_a(attr_name) and pred_v(attr_value):
                return True
        return False

    return internal


def has_class_pf( class_p):
    """
    A predicate factory that checks that an element has the desired class
    :param class_p: something that can be converted to a string predicate
    :return: a predicate that returns True for elements that have classes that satisfy class_p

    >>> from bs4 import BeautifulSoup
    >>> doc = ('<html><span class="c1 c2 c3" >s1</span><div id="d1">d1</div></html>')
    >>> s = BeautifulSoup(doc, 'html.parser')
    >>> e1 = s.html.span
    >>> e2 = s.html.div
    >>> p = has_class_pf("c2")
    >>> p(e1)
    True
    >>> p(e2)
    False
    >>> p = has_class_pf(["c5","c2"])
    >>> p(e1)
    True
    >>> p(e2)
    False
    >>> p = has_class_pf(["c5","c6"])
    >>> p(e1)
    False

    """
    pred = to_string_compare_predicate(class_p)

    def internal(elm):
        if not is_tag(elm):
            return False

        clss = elm.attrs.get("class", [""])
        for cls in clss:
            if pred(cls):
                return True
        return False

    return internal


def has_children_of_type_pf(name_p, ignore_case=True):
    """
    Creates a predicate that checks if the immediate descendents of the element have a name that
    satisfies name_p
    :param name_p: something that can be converted into a string predicate
    :return: true if the current element has children that satisfy the predicate

    >>> from bs4 import BeautifulSoup
    >>> doc = '<html><span>s1</span><div>d1 <p>hello</p></div></html>'
    >>> s = BeautifulSoup(doc, 'html.parser')
    >>> e = s.html
    >>> pred = has_children_of_type_pf("span")
    >>> pred(e)
    True
    >>> pred = has_children_of_type_pf("div")
    >>> pred(e)
    True
    >>> pred = has_children_of_type_pf("p")
    >>> pred(e)
    False
    >>> pred = has_children_of_type_pf("a")
    >>> pred(e)
    False

    """
    pred = to_string_compare_predicate(name_p, ignore_case)

    def internal(elm):
        if not is_tag_or_soup(elm):
            return False

        for child in elm.children:
            if is_tag_or_soup(child) and pred(child.name):
                return True
        return False

    return internal


def has_descendents_of_type_pf(name_p, ignore_case=True):
    """
    Creates a predicate that checks if the descendents of the element have a name that
    satisfies name_p (it will go deep looking for the elements).
    :param name_p: something that can be converted into a string predicate
    :return: true if the current element has children that satisfy the predicate

    >>> from bs4 import BeautifulSoup
    >>> doc = ('<html><span id="s1" class="c1 c2 c3" style="margin: 3">s1</span>'+
    ... '<div data-x="abc" id="d1">d1</div></html>')
    >>> s = BeautifulSoup(doc, 'html.parser')
    >>> e1 = s.html.span
    >>> e2 = s.html.div

    """
    pred = to_string_compare_predicate(name_p, ignore_case)

    def internal(elm):
        if not is_tag_or_soup(elm):
            return False

        for child in elm.children:
            if is_tag_or_soup(child) and pred(child.name):
                return True
            if internal(child):
                return True
        return False

    return internal


def to_string_compare_predicate(pred, ignore_case=True):
    """
    Turns the passed parameter into a string compare predicate
    :param name_p: can be one of:
        - a string ( will compare to the string) (e.g. has_name_pf( 'div') ... predicate checking if the tag is a <div>
        - a list,tuple,set,frozenset : will create a predicate that checks if the tag is one of the passed tags
            (e.g.  has_name_pf(['div','span','p') checks if the tag is one of <div>,<span>,<p>)
        - a predicate Callable[[string,bool],bool], checks if the passed element has a name that satisfies the predicate
            where the second parameter is the ignore_case param from the factory.

    :param ignore_case: should the comparison be case sensitive (default: ignore case)
    :return: a predicate that expects a string like object

    >>> e1 = 'span'
    >>> e2 = 'SPAN'
    >>> e3 = "ul"
    >>> p1 = to_string_compare_predicate('span')
    >>> p2 = to_string_compare_predicate('span', False)
    >>> p3 = to_string_compare_predicate('x')
    >>> p4 = to_string_compare_predicate('X', False)
    >>> p1(e1)
    True
    >>> p2(e1)
    True
    >>> p1(e2)
    True
    >>> p2(e2)
    False
    >>> p3(e1)
    False
    >>> p4(e1)
    False

    >>> p5 = to_string_compare_predicate(['i','span','a'])
    >>> p6 = to_string_compare_predicate(['i','span','a'], False)
    >>> p7 = to_string_compare_predicate(['i','x','a'])
    >>> p5(e1)
    True
    >>> p5(e2)
    True
    >>> p6(e1)
    True
    >>> p6(e2)
    False
    >>> p7(e1)
    False
    >>> p8 = to_string_compare_predicate({'i','span','a'})
    >>> p8(e1)
    True
    >>> p9 = to_string_compare_predicate(('i','span','a'))
    >>> p9(e1)
    True
    >>> p10 = to_string_compare_predicate(frozenset(['i','span','a']))
    >>> p10(e1)
    True
    >>> p10(e2)
    True
    >>> def pred(elm_name):
    ...    if elm_name == 'span' or elm_name == 'x':
    ...        return True
    ...    return False
    >>> p11 = to_string_compare_predicate(pred)
    >>> p12 = to_string_compare_predicate(pred, ignore_case=False)
    >>> p11(e1)
    True
    >>> p11(e2)
    True
    >>> p11(e3)
    False
    >>> p12(e1)
    True
    >>> p12(e2)
    False

    """
    if pred is None:
        return False
    # pred is a string
    if isinstance(pred, str):
        name = pred.lower() if ignore_case else pred

        def case_sensitive_compare(elm_name):
            return elm_name == name

    # pred is a list like object
    elif isinstance(pred, (tuple, list, set, frozenset)):
        names = frozenset([name.lower() for name in pred]) if ignore_case else frozenset(pred)

        def case_sensitive_compare(elm_name):
            return elm_name in names
    # pred must be a predicate, use it as is
    else:
        case_sensitive_compare = pred

    if ignore_case:
        def ret_val(elm_name):
            return case_sensitive_compare(elm_name.lower())
    else:
        ret_val = case_sensitive_compare

    return ret_val
