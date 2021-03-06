# How to use file utilities

## Overview
In this example we will use the process_directory utility function to process a directory.

In order to simplify the application of filters bs-processor contains utilities for processing documents saved
in files.

The file_util module has two main entry points: `process_file` and `process_directory`.

[process_file](/bs-processors/bs_processors/utils/file_util.html#bs_processors.utils.file_util.process_file)
takes as parameters the processor and the input and output file names.

[process_directory](/bs-processors/bs_processors/utils/file_util.html#bs_processors.utils.file_util.process_directory)
is slightly more complex and it will be used in this example.

In this example we will use the input directory used by all other examples and we will output the result to
a new directory `output2` at the same level with `input`.

To keep the focus on the directory function we will keep things simple and use a filter processor that
filters empty tags.


```python

from bs_processors.predicate import is_empty_p
from bs_processors import filter_factory
filter_empty = filter_factory(is_empty_p)

```

In order to do our processing we'll use the following code:


```python

import util
from bs_processors.utils.file_util import process_directory

def main():
    input_dir = util.relative_to_absolute_path_name(__file__, "input")
    output_dir = util.relative_to_absolute_path_name(__file__, "output2")
    process_directory(filter_empty,'html.parser', input_dir, output_dir,"*.html")

```

This will run all files that match `*.html` through the `filter_empty` processor and put the result in the `output2`
directory.

`process_directory` will recreate the structure of the input directory in the output directory ( subdirectories from
input will become subdirectories in output).

