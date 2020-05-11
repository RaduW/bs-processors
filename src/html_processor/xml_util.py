"""
Utilities for working with lxml Elements
"""


def add_text(elm, text):
    """
    Adds a text to the end of an element
    :param elm: the element
    :param text: the text
    :return: the original with the text added

    >>> from lxml import etree
    >>> elm = etree.XML("<root><a></a></root>")
    >>> _ = add_text(elm[0], "XXX")
    >>> etree.tostring(elm)
    b'<root><a>XXX</a></root>'
    >>> elm = etree.XML("<root><a>ABC_</a></root>")
    >>> _ = add_text(elm[0], "XXX")
    >>> etree.tostring(elm)
    b'<root><a>ABC_XXX</a></root>'
    >>> elm = etree.XML("<root><a>ABC<b/></a></root>")
    >>> _ = add_text(elm[0], "XXX")
    >>> etree.tostring(elm)
    b'<root><a>ABC<b/>XXX</a></root>'
    >>> elm = etree.XML("<root><a>ABC<b/>DEF_</a></root>")
    >>> _ = add_text(elm[0], "XXX")
    >>> etree.tostring(elm)
    b'<root><a>ABC<b/>DEF_XXX</a></root>'
    """

    if len(elm) == 0:
        # no children append to text
        if elm.text is None:
            elm.text = text
        else:
            elm.text += text
    else:
        last_child = elm[len(elm) - 1]
        if last_child.tail is None:
            last_child.tail = text
        else:
            last_child.tail += text
    return elm


def remove_children(elm):
    """
    Removes all children from an element (maintaining everything else)
    :param elm: the element
    :return:
    >>> from lxml import etree
    >>> elm = etree.XML("<root><a><b/><c/><d/></a></root>")
    >>> _ = remove_children(elm[0] )
    >>> etree.tostring(elm)
    b'<root><a/></root>'
    >>> elm = etree.XML("<root><a>ABC_<b/><c/><d/>XYZ</a></root>")
    >>> _ = remove_children(elm[0] )
    >>> etree.tostring(elm)
    b'<root><a>ABC_</a></root>'
    >>> elm = etree.XML("<root><a></a></root>")
    >>> _ = remove_children(elm[0] )
    >>> etree.tostring(elm)
    b'<root><a/></root>'
    >>> elm = etree.XML("<root><a>ABC</a></root>")
    >>> _ = remove_children(elm[0] )
    >>> etree.tostring(elm)
    b'<root><a>ABC</a></root>'
    """
    children = elm.getchildren()
    for child in children:
        elm.remove(child)
    return elm
