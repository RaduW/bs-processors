# Working with bs-processors

## Overview
bs-processors is a library for modifying/cleaning htm/xml files with minimum fuss.

It is meant to be used as an alternative to something like XSLT for cases when achieving the desired result with XSLT is not possible or very difficult.

The general idea is that one can combine the provided blocks and maybe write a moderate amount of custom code to create powerful document processors.

## The processors
At the base of the library is a set of processors that can be configured to achieve typical processing steps.

Processors can be assembled toghether into one combined processor in order to create the desired effect.

Anybody can write a processor that can interoperate with the provided processors with relative ease.

A processor is a function of the following signature:

```python
def processor(elms: List[Any])->List[Any]
```

That is a processor takes a list of elements and returns a list of elements.

Typically the processor will be passed just one element, the top level document (the BeautifulSoup object). 

It may seem an odd choice that the processor has the above signature since it would probably be more ergonomic to take a single element as input but the choice was made in order to easyly compose a chain of processors.

Since a processor may return a list of elements (and there are real world cases when this is useful) a decision was taken to also accept as parameter a list of elements making it trivial to compose processors at the expense of the slight annoyance that instead of initially passing the top level element as `elm` one would pass it as `[elm]`.

The library contains a set of processor factories that take specific configurations and return processor functions.

As an example, the library contains a processor factory that can generate filter processors, that is processors that selectively filter documents of certain elements. By passing a filtering function to the filter factory one gets a processor that filters the desired elements.

```python
filter_div_and_span = filter_factory(has_name_pf(['div', 'span']))
```

In the example above `filter_div_and_span` is a processor that will remove all elements of type `div` or `span` from the passed elms ( **Note** that the filtering is going to be deep, the processor will descend all the way down looking for elements to filter).

For a list of all available processors check the Api.

For examples of using them check the examples section.



## The predicates
Predicates are functions that receive an argument of one of the BeautifulSoupe types ( i.e. `BeautifulSoup` `TagElement` or `NavigableString` ) and return a boolean value.  Predicates are used by most processor factory to configure their behaviour.



## Writing your own predicates
Although there are a lot of predicates and predicate factories that can be combined to achive most common functionality it is quite trivial to write one yourself.

In this example we will create a predicate that checks if the elment is a tag or the soup element and if the element is not span.

**Note** that you don't really need to write this particular predicate since it can be easily created by composing the existing predicates like so:

```python
my_predicate = and_pf( 
    is_tag_or_soup_p, 
    not_pf(
        has_name_pf('span')
    )
)
```

The desired predicate can be written from scratch like so:

```python
def my_predicate(elm)->bool:
  if elm is None:
    return False  # just to be sure we don't raise
  if elm.name is None:
    return False # this is a NavigableString (a tag or a soup have name)
  if elm.name == 'span'
    return False # we don't want span elements
  return True # anything else is fine
```

Of course one can combine the custom predicate with already build predicates and predicate factories like so:

```python
is_span_p = has_name_pf('span')
def my_predicate(elm)->bool:
  if not is_tag_or_soup_p(elm):
    return False
  return not is_span_p(elm)
```



## Writing your own processors
Writing your own processors is not much more complicated than writing custom predicates.

In order for a custom processor to interact with other processors the custom processor has to have the following signature:

```python
def processor(elms: List[Any])->List[Any]
```

For our example let's make a processor that adds a class attribute to all elements of type `<div>` from the passed elements as long as they do not have an id set. This is a rather contrived example that could be easyly implemented using the existing processors.

We will only implement a simplified form that takes only one element and returns a list of elements and then we will use an already existing adaptor function to create the final processor

Here's how one would write this:

```python
from bs_processors.xml_util import set_new_children, process_children
from bs_processors.processor_util

def add_classes_to_div_single( elm: Any) -> List[Any]:
  if not is_tag_or_soup_p(elm):
    return [elm]  # nothing to proess further
  if elm.name == 'div' and not elm.attrs.get("id"):
    clss = elm.attrs.get("class", [""])
    if not 'my-class' in clss:
      clss.append('my-class')
      elm.attrs.["class"] = clss
      
  for child in elm.children:
    new_children = process_children(lambda child: single_filter_proc(should_filter, child), elm)
    set_new_children(elm, new_children)

  return [elm]
  
add_classes_to_div = single_to_multiple(add_classes_to_div_single)
```

## Composing processors in processor chains

Often we need to process documents in complex ways. Often a complex process can be broken down in a series of simple processes. As an example we may want to filter some elements, unwrap some other elements, add some attributes to other elements and finally flatten the whole result.

bs-processors is designed to work with exactly this type of scenarios.

All we need to do is create our processors and then chain them toghether to obtain a processor that will call all configured processors.

In the example below we create a few processors and finally we chain them toghether to obtain our final processor.

```python
filter_bad_p = and_pf( 
    is_tag_p, 
    has_name_pf(['span', 'div'),
    has_class_pf(['bad-element'])
)

filter_bad_proc = filter_factory(filter_bad_p)

should_unwrap_p = has_name_pf['font', 'i', 'b']

unwrap_proc = unwrap_factory(should_unwrap)

is_internal_child_p = has_name_pf(['span', 'a'])
flatten_children_p = has_name_pf(['div'])

flatten_proc = flatten_factory(flatten_clhildren_p, is_internal_child_p)

clean_html_proc = join([filter_bad_proc, unwrap_proc, flatten_proc])

```

