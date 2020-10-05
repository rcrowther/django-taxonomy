# Django Taxonomy
Create categories in a tree structure.

This app is called 'django-taxonomy', but internally the module is called 'taxonomy'.

## Alternatives

- [django-packages](https://github.com/callowayproject/django-categories)
    This project is mature with many commits. It uses an MPTT implementation.

- [django-modelcluster](https://github.com/wagtail/django-modelcluster)
This is a chunk of the Wagtail CMS. It allows you to join model objects togrether, even as they are created, then save in a chink. Not quite the same thing as a taxonomy, but it does define relations between models, so if you are looking for that, it may be a direct fit.
 
## Why you may or may not want this app
Pro
- Simple to maintain
- Displays category titles and contents efficiently
- Several display and support options builtin 

Con
- Can't define term information
- No multiparent (node map) option
- Poor at finding descending node elements, so poor it has not been implemented

If you are building a shopping site, you will want an MPTT structure. But if you are creating a categorisation system, or gathering pages on a website, you may prefer this.

## Overview
![overview diagram](screenshots/overview.svg?raw=true&sanitize=true)

The taxonomy presents a model 'Taxonomy' which works as a root to any tree of categories. Then you add 'Terms' (categories) to the root. To any term you can attach any number of elements. An element is a number, and would usually be a model id.


## If you have done this before

## Install

## Admin

## The API
As an app, Taxonomy is spread across several DB tables which need code to manipulate them. So the code is gathered into a manager. Since this is not the same as a Django (QuerySet) Manager, I've called the manager TaxonomyAPI. You'll use it for access to taxonomy data (unless you're hacking or haave a broken installation). 

For working with data in the taxonomy, this gets you to methods for a single taconomy,

    from taxonomy.taxonomy import TaxonomyAPI

    TaxonomyAPI(1)

This gets you to methods for aa single term,


    from taxonomy.taxonomy import TaxonomyAPI

        TaxonomyAPI(1).term(3)

As for the methods, there's a lot of them. For making pages, the simple-named methods return full term data,

    parent
    children
    ascendent_path
    descendent_paths

Many of the other methods only deal with DB ids (the methods above populate these trees with term data after the shape of the data has been generated).

Some methods build from the tree, so come with added data, the depth a term should be rendered at. These kinds of collections are mode from tuples (depth_in_tree, term_id).  This is the code the app uses to render the select boxes in Admin.

One point worth knowing is that, since these taxonomies are single-parent, there can be only one path back to the taxonomy root. But there can be several paths towards leaves. Ask for descendant_paths() and you will get a list of lists.



## Rendering
There are a lot of options which are nothing to do with this app, they are conceptual. What do you want to render?

Let's say...

### A model view
Some stock Django. Add some taxonomy data to a View, 

    from django.views.generic import ListView, DetailView
    from article.models import Page
    from taxonomy.taxonomy import TaxonomyAPI

    class ArticleDetailView(DetailView):
        model = Page
        context_object_name = 'page'
        
        def get_context_data(self, **kwargs):
            ctx = super().get_context_data(**kwargs)
            ctx['top_bar'] = str(TaxonomyAPI(1).term(2).ascendent_path())
            return ctx

anD in the template 'page_detail.html',

    <nav class="topbar">
        {% for term in nav_bar %}
        <div class="menu-item">
            <a href="/category/{{ term.title }}">{{ term.title }}</a>
        </div>
        {% endfor %}
    </nav>

## Template tags

## Implementation notes
There are a few ways to implent a tree, as there are lists. Here is our version.

You can only attach data elements to terms, not the 'taxonomy' instance at the base. If you would like a taxonomy where elements can be attached to the base, start a base then add a single term which will be the 'root term'. Build from there e.g. ::

    base = 'car categories'
    - Cars
    -- saloon 
    -- hatchback 
    -- sport
    ...
  
etc. now you can attach an unclassified car to the generic term 'cars'.

## EndNote
### The evironment
The Django system presents substancial difficulties to anyone implementing structures like this. The builtin admin may be customisable, but it's great blob of code is hard to extend. Then there is the issue of the ORM and foreign keys, about which you can say nothing, or write a book. Finally, though that would be unusual, Python has no support and there is no presentation logic. The only functionality on the coder's side is the model building, and hackability. It's clear other projects have wrestled with these issues. I'm just working as I can to make something usable.

### Straight vs. MPTT implementation
Django-taxonomy uses direct links between its tree nodes. This is fundamentally different to an MPTT structure, which links tree nodes as a list. It's something like the difference between an array and a linked list. They both present the same structure, maybe a similar API, but the underlying implementation is different. There are advantages to both. An MPTT structure is excellent at gathering data from multiple categories, say 'cars', and all sub-categories. It is also capable of ordering it's categories and references exactly. Whereas the straight structure is so poor at this I have not implemented either functionality. But the straight structure is simple to create and maintain, and is good at displaying the categories themselves.
