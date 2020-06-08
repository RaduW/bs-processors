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

**Note** that you don't really need to write this particular predicate since it can be easyly created by composing the existing predicates like so `my_predicate = and_pf( is_tag_or_soup_p, not_pf(has_name_pf('span')))`.

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
TODO
