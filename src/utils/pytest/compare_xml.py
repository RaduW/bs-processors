
def compare_xml(left, right, error_context = None):
    if error_context is None:
        error_context = ""
    error_context= "{}{}".format(error_context,left.tag)
    elm_id = left.attrib.get('id')
    elm_cls = left.attrib.get('class')
    if elm_id is not None:
        error_context = "{}#{}".format(error_context,elm_id)
    elif elm_cls is not None:
        # we don't have an id but we have some class
        error_context = "{}<{}>".format(error_context,elm_cls)
    if left is None and right is None:
        return True
    if left is None and right is not None:
        return "None object to the left at :{}".format(error_context)
    if left is not None and right is None:
        return "None object to the right at :{}".format(error_context)

    if left.tag != right.tag:
        return "Different tag name at: {}".format(error_context)

    if left.attrib != right.attrib:
        return "Different attributes at: {}".format(error_context)

    text_left = left.text or ''
    text_right = right.text or ''

    if text_left.strip() != text_right.strip():
        return "Different text at: {}".format(error_context)

    tail_left = left.text or ''
    tail_right = right.text or ''

    if tail_left.strip() != tail_right.strip():
        return "Different tail at: {}".format(error_context)

    if len(left) != len(right):
        return "Different number of children at:{}".format(error_context)

    for idx in range(len(left)):
        new_context= "{}->[{}]".format(error_context, idx)
        result = compare_xml(left[idx], right[idx], new_context)
        if result is not None:
            return result
    return None # success
