"""
Xml comparison utility.

"""
from bs_processors.utils.util import normalize_string, is_empty


def _not_empty(elm):
    """
    duplicates not_empty_p functionality so that it doesn't import predicate
    """
    if elm is None:
        return False
    if elm.name is not None:
        return True
    return not is_empty(elm)



def compare_xml(left, right, error_context = None):
    """
    Compares two elements
    * **left**: the left element
    * **right**: the right element
    * **error_context**: error context should be None at top level
    * **return**: None if contents are identical, an error message if they are not

    >>> from bs4 import BeautifulSoup as bs
    >>> doc1 = bs("<html> hello  </html>", "html.parser")
    >>> doc2 = bs("<html>hello</html>", "html.parser")
    >>> compare_xml(doc1.html, doc2.html) is None
    True

    >>> doc1 = bs("<html> <p>x</p>  </html>", "html.parser")
    >>> doc2 = bs("<html><p>x</p</html>", "html.parser")
    >>> compare_xml(doc1.html, doc2.html) is None
    True

    >>> doc1 = bs("<html><p>x</p><p>x</p></html>", "html.parser")
    >>> doc2 = bs("<html><p>x</p></html>", "html.parser")
    >>> compare_xml(doc1.html, doc2.html)
    'Different number of children at:html'

    >>> doc1 = bs("<html><i>x</i></html>", "html.parser")
    >>> doc2 = bs("<html><p>x</p</html>", "html.parser")
    >>> compare_xml(doc1.html, doc2.html)
    'Different tag name at: html->[0]i'

    >>> doc1 = bs("<html> <p id='1'>x</p>  </html>", "html.parser")
    >>> doc2 = bs('<html><p id="1" class="x">x</p</html>', "html.parser")
    >>> compare_xml(doc1.html, doc2.html)
    'Different attributes at: html->[0]p#1'

    >>> doc1 = bs("<html> hello  </html>", "html.parser")
    >>> doc2 = bs("<html>hello2</html>", "html.parser")
    >>> compare_xml(doc1.html, doc2.html)
    "different string content 'hello'!='hello2' at html->[0]None"
    """
    if error_context is None:
        error_context = ""
    error_context= "{}{}".format(error_context,left.name)

    if left is None and right is None:
        return None

    if left is None :
        return "None object to the left at :{}".format(error_context)
    if right is None:
        return "None object to the right at :{}".format(error_context)

    # check strings
    if left.name is None and right.name is None:
        text_left = normalize_string(left).strip()
        text_right = normalize_string(right).strip()
        if text_left != text_right:
            return f"different string content '{text_left}'!='{text_right}' at {error_context}"
        else:
            return None
    if left.name is None:
        return f"left is string while right is elm left->'{left}' right->'{right.name}' at {error_context}"
    if right.name is None:
        return f"left is elm while right is string left->'{left.name}' right->'{right}' at {error_context}"

    elm_id = left.get('id')
    elm_cls = left.get('class')
    if elm_id is not None:
        error_context = "{}#{}".format(error_context,elm_id)
    elif elm_cls is not None:
        # we don't have an id but we have some class
        error_context = "{}<{}>".format(error_context,elm_cls)

    if left.name != right.name:
        return "Different tag name at: {}".format(error_context)

    if left.attrs != right.attrs:
        return "Different attributes at: {}".format(error_context)

    # remove text children with empty spaces (i.e. format differences) from comparison
    children_left = list(filter(_not_empty, left.children))
    children_right = list(filter(_not_empty, right.children))

    if len(children_left) != len(children_right):
        return "Different number of children at:{}".format(error_context)

    for idx in range(len(children_left)):
        new_context= "{}->[{}]".format(error_context, idx)
        result = compare_xml(children_left[idx], children_right[idx], new_context)
        if result is not None:
            return result
    return None  # success
