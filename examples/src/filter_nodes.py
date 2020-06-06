"""
# How to use the filter processor

## Overview
In this example we will use the filter processor to remove unwanted tags from a sample file

Let's say we have the following file that we want to clean up.

### The input is
{{ inject_file html simple_filter.html }}

we would like to

### The code is
{{ inject_code main }}

### The result is

{{ inject_file html simple_result.html}}

"""

from bs_processors import filter_factory

# section_start main
def main():
    print("Hello from main")
# section_end

if __name__ == '__main__':
    main()
