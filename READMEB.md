# Django Taxonomy
Create categories in a tree structure.

This app is called 'django-taxonomy', but internally the module is called 'taxonomy'.

## Alternatives

- [django-packages](https://github.com/callowayproject/django-categories)
    This project is mature with many commits. It uses an MPTT implementation.

- [django-modelcluster](https://github.com/wagtail/django-modelcluster)
This is a chunk of the Wagtail CMS. It allows you to join model objects togrether, rvrn as they are createdm then save in a chink. Not quite the same thing as a taxonomy, but it does define relations between models, so if you are looking for that, it may be a direct fit.
 
## Why you may or may not want this app
Django-taxonomy uses direct links between its tree nodes. This is fundamentally different to an MPTT structure, which links tree nodes in a list. It's something like the difference between an array and a linked list. They both present the same structure, maybe a similar API, but the underlying implementation is different. There are advantages to both. An MPTT structure is excellent at gathering data from multiple categories, say 'cars', and all sub-categories. It is also capable of ordering it's categories and references exactly. Whereas the straight structure is so poor at this I have not implemented either functionality. But the straight structure is very simple to create and maintain, and is good at displaying the categories themselves. So if you are building a shopping site, you will want an MPTT structure. But if you are creating a categorisation system, or gathering pages on a website, you may prefer this.

## Overview
![overview diagram](screenshots/overview.svg?raw=true&sanitize=true)

The taxonomy presents a model 'Tree' which works as a root to any taxonomy. Then you add 'Terms' to the root. To any term you can attach any number of elements. An element is a number, and would usually be a model id.


## If you have done this before

## Install

## Admin

## Code manipulation of Trees

## Template tags


## EndNote
The Django system presents substancial difficulties to anyone implementing structures like this. The builtin admin may be customisable, but it's great blob of code is hard to extend. Then there is the issue of the ORM and foreign keys, about which you can say nothing, or write a book. Finally, though that would be unusual, Python has no support and there is no presentation logic. The only functionality on the coder's side is the model building, and hackability. It's clear other projects have wrestled with these issues. I'm just working as I can to make something usable.
