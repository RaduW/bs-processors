# How to unwrap unwanted tags

## Overview
In this example we will use the flatten_factory processor to unwrap unwanted tags.

This covers the case when we have a source file that has deeply nested structures that we would like to flatten.

This type of problem can be seen when we want to clean documents that were exported as html from various text editors.

In our example the useful information is buried deep inside nested `<div>` that have various classes.
To make matters worse some information is also buried inside `<font>` elements.

We would like to remove all superfluous `<div>` elements and all `<font>` elements while preserving the content
inside them.

Let's say we have the following file that we want to clean up:

### Input

```html

<!DOCTYPE html>
<html>
<body>
<div>
    <div class="useless-1 bold">
        First line <font><font> inside double font</font></font> outside font.
        <div class="useless-2">
            <p>
                Second line
            </p>
        </div>
    </div>
    <div>
        <p>
            Third line
        </p>
    </div>
</div>
<div>
    Forth line <font> inside font </font> <span>end.</span>
</div>
</body>
</html>

```

We noticed that the file has some empty `<font>` tags that we want to remove if they do not contain any
text. For that we can use the
[filter_factory](bs-processors/bs_processors/generic_processors.html#bs_processors.generic_processors.unwrap_factory)
processor.

In the processor we need to pass a predicate that checks if an element is a `<font>` or if it is a `<div> with a
marker class that designates it as not necessary.

Luckily we can construct this predicate from already available building blocks.

To construct our predicate we have the following code:

```python

from bs_processors import and_pf, has_name_pf, is_empty_p, or_pf, has_class_pf

should_uwrap_p = or_pf(
    has_name_pf('font'),
    and_pf(
        has_name_pf('div'),
        has_class_pf(['useless-1', 'useless-2'])
    )
)

```

After constructing the predicate all that remains is to use it to create our processor


```python

from bs_processors import unwrap_factory

remove_unnecessary_wrappers = unwrap_factory(should_uwrap_p)

```

Now we are ready to pass it our loaded soup and we are done


```python

import util

def main():
    doc = util.load_relative_html_file(__file__, "input/deeply_nested.html")
    result = remove_unnecessary_wrappers([doc])
    util.save_relative_result(result, __file__, "output/deeply_nested_result.html")

```

### The result is:

```html

<!DOCTYPE html>


```

