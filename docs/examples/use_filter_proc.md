# How to use the filter processor

## Overview
In this example we will use the filter processor to remove unwanted tags from a sample file

Let's say we have the following file that we want to clean up:

### Input

```html

<!DOCTYPE html>
<html>
    <div>First line <font id="not-empty"> not empty</font> </div>
    <div>Second line <font> </font> <span>end.</span></div>
</html>

```

We noticed that the file has some empty `<font>` tags that we want to remove if they do not contain any
text. For that we can use the
[filter_factory](bs-processors/bs_processors/generic_processors.html#bs_processors.generic_processors.filter_factory)
processor.

In the processor we need to pass a filter that checks if an element is a `<font>` element and if it is empty.

Luckily we can construct this predicate from already available building blocks.
The [has_name_pf](bs-processors/bs_processors/predicate.html#bs_processors.predicate.has_name_pf) predicate factory can
be used to check if the passed element is font and the
[is_empty_p](bs-processors/bs_processors/predicate.html#bs_processors.predicate.is_empty_p) can be used to check if
the element is empty (contains at most white spaces).

To construct our predicate we have the following code:

```python

from bs_processors import and_pf, has_name_pf, is_empty_p

is_empty_font_p = and_pf( has_name_pf('font'), is_empty_p)

```

After constructing the predicate all that remains is to use it to create our filter


```python

from bs_processors import filter_factory

filter_empty_font_proc = filter_factory(is_empty_font_p)

```

Now we are ready to pass it our loaded soup and we are done


```python

import util
from bs_processors.utils.file_util import process_file

def main():
    doc_name = util.relative_to_absolute_file_name(__file__, "input/simple_filter.html")
    result_name = util.relative_to_absolute_file_name( __file__, "output/simple_filter_result.html")
    process_file(filter_empty_font_proc,"html.parser",doc_name, result_name)

```

### The result is:

```html

<!DOCTYPE html>
<html>
 <div>
  First line
  <font id="not-empty">
   not empty
  </font>
 </div>
 <div>
  Second line
  <span>
   end.
  </span>
 </div>
</html>

```

