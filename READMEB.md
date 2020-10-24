# Django Taxonomy
Create categories in a tree structure.

This app is called 'django-taxonomy', but internally the module is called 'taxonomy'.

## Alternatives

- [django-packages](https://github.com/callowayproject/django-categories)
    This project is mature with many commits. It uses an MPTT implementation.

- [django-treebeard](https://github.com/django-treebeard/django-treebeard)
    Django Treebeard is mature, has multiple tree implementations, an API, and AJAX Admin. It's a legendary Django package. It can do everything this package can do and more.

- [django-modelcluster](https://github.com/wagtail/django-modelcluster)
    This is a chunk of the Wagtail CMS. It allows you to join model objects together, even as they are created, then save in a chink. Not quite the same thing as a taxonomy, but it does define relations between models, so if you are looking for that, it may be a direct fit.
 
## Why you may or may not want this app
Pro
- It's simple.
- It can be subclassed
- It's got displays and effective Admin builtin 

Con
- No multiparent (node map) option
- Poor at finding descending node elements, so poor it has not been implemented

If you want the standard, get [TreeBeard](https://github.com/django-treebeard/django-treebeard). If you are building a shopping site, you want an MPTT structure. Or maybe Treebeard's PathTree implementation. This is not that app.

This app has only one (non)feature over the heavyweights here. It is simple. 
It has no dependencies. It has only 800 (or near) lines of core code. It has a bone-simple SQL layout, so simple you can fix it with 'dbshell'. So if you don't need the weight, but want to catalogue some uploads, or gather pages on a website, you may prefer this.

## Overview
![overview diagram](screenshots/overview.svg?raw=true&sanitize=true)

Taxonomy has a model 'TermBase', which you can extend with whatever data you want. Every subclass of TermBase becomes a tree of terms. An element is any Django object/Model which joins to a Term. The join is usually through a Foreign key.


## If you have done this before

## Install

## Creating a Taxonomy
Usually, one taxonomy would be associated with one model. Otherwise, if elements come from mpore than one model, you will run into difficulties identifying which model is returned from categories. Not an impossible situation, but these instructions will not cover that possibility further.

Because of this, taxonomies would usually be created in the model to be associated with or, possibly, as a freestanding app.

To include multiple models in one taxonomy, you could use a base model. This would include an id field???

An example of a declaration. This adds a 'description' field, so the taxonomy can be used for more helpful user display. It also includes a 'slug' field, so the term titles can be used in URLs. That means the model has an get_absolute_url method too (see below),
        
    class Category(TermBase):

        # Not unique. Terms may be in different taxonomies. They may
        # be duplicated at different places in a hierarchy e.g. 'sports>news'
        # 'local>news'.
        slug = models.SlugField(
            max_length=64,
            help_text="Short name for use in urls.",
        )
      
        description = models.CharField(
            max_length=255,
            blank=True,
            default='',
            help_text="Description of the category. Limited to 255 characters.",
        )
          
        def get_absolute_url(self):
            return reverse("category_detail", kwargs={"slug": self.slug})

        api = None

        def __repr__(self):
            return "Term(id:{}, name:{}, slug:{}, weight:{})".format(
                self.id,
                self.name,
                self.slug,
                self.weight,
            ) 



    # Always the same, but a new one needed for every taxonomy.
    class CategoryParent(TermParentBase):
            pass
                    

    # Always this format, but a new one needed for every taxonomy.
    Category.api = TaxonomyAPI(
                Category, 
                CategoryParent, 
             ) 

Then migrate.


## Admin
You need a special admin from taxonomy.admins. As usual, the admin needs a 'fields' attribute. One comment here, if you do not have a 'fields' statement, the 'parent' field is placed at the bottom of the form. Almost certainally, this is not what you want. Also, you do want the 'parent' field to show in most cases, so put 'parent' in the 'fields' list. 

You can customise as usual. Here I've added a 'prepopulate' attribute for the slug field in the example above,

    from django.contrib import admin
    from taxonomy.models import Category
    from taxonomy import admins



    class CategoryAdmin(admins.TermAdmin):
        fields = ('parent', 'name', 'slug', 'description', 'weight')
        prepopulated_fields = {"slug": ("name",)}
    admin.site.register(Term, TermAdmin)

[image]

## The API
As an app, Taxonomy is spread across DB tables which need code to manipulate them. So the code is gathered into a manager. Since this is not the same as a Django (QuerySet) Manager, I've called it an API, not a manager. You'll use it for access to taxonomy data (unless you're hacking or have a broken installation). 

The api hangs off any model based on TermBase, and can also be acessed from any TermBase class. Using the builtin model Term,

    from taxonomy.models import Term

    api = Term.api

Like the queryset manager 'objects', the api is also present on any TermBased object,

    from taxonomy.models import Term

    obj = Term.objects.get(id=1)
    obj,api

The attribute 'api' gives you some methods for one tree,

    delete() (whole tree)
    save() (a Term)
    tree()

And a few more. You can call the API with a Term id, which gives you methods for a single TermBase,

    from taxonomy.models import Term

    api_for_term_4 = Term.api(4)

This gets you many methods. For making pages, the simple-named methods return full term data,

    parent()
    children()
    ascendent_path()
    descendent_paths()
    tree(self, max_depth=None)

Some of the other methods only deal with DB ids.

The structure of tree data is worth mentioning. It is usually a flat tree of depth and Termdata coupled in a Tuple, gathered into a list,

    [
        (0, Term1)
        (1, Term2)
        (1, Term3)
        (0, Term4)
        (1, Term5)
        (2, Term6)
        (3, Term7)
        ...
    ]

This is the kind of data the app uses to render the select boxes in Admin.

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
            ctx['breadcrumb'] = str(self.obj.api(self.obj.id).ascendent_path())
            return ctx

and in the template 'page_detail.html',

    <nav class="topbar">
        <ul>
            {% for term in breadcrumb %}
            <li class="menu-item">
                <a href="/category/{{ term.title }}">{{ term.title }}</a>
            </li>
            {% endfor %}
        </ul>
    </nav>

## Attaching objects to Terms
### Term recorded in object
This is the way most people think about this. A Page has a category of 'Psychology'.

You'll need to add a field to your Model. Usually you would use a ForeignKey (unless your data can fall into many categories, use a ManyToManyField).

    from taxonomy.models import Term

    class MyModel(models.Model):
        category = models.ForeignKey(
            Term,
            on_delete=models.CASCADE,
        )

You'll get the usual Django setup in Admin like this. If you have a lot of Terms you may want to try [autocomplete](https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.autocomplete_fields) or [raw id](https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.raw_id_fields) widgets.

#### A list of siblings
In the view context,

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['siblings'] = Page.objects.filter(category=self.get_object().category)
        return ctx

Then render 'siblings' somehow.


### Notes
I would point out the above is not the only way. Objects can be recorded against Terms. Not only is the above not the only way, I don't like it. I don't think category data should intrude on objects.

Hoever, the nice way to say this, Django has no ability. The ORM, the model fields, the Admin, and the form-building all have no ability to organise the data otherwise. I've stuck with the above, which plays ok with Django. What I wold prefer is make an object--term table, and a form for it. But in Django, that requires hand-crafting model specifics, and cannot be part of the main app. 

## URLs for Taxonomies
Not all taxonomies will need URLs, but a taxonomy with URLs can make the base of a site. For example, a few CMS assume that pages on a site are organised as a tree.

First, you need to decide how your URLs will look. Will they include a subject? There is advice [they should not](https://www.w3.org/Provider/Style/URI). But then the URL is not so hackable, which is also a case.

I've not worked on a full URL solution. Here is a 'distracted' URL solution, that retains objects at their Django URLs (e.g. host/page/xxx) but provides breadgrumbs and category listings.

### Declare a term model with a slug field
So it can be used in URLs with a nice escaped URL 'name'.

### Breadcrumbs
In the view context, something like,

    from taxonomy.models import Term

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['crumb_terms'] = Term.api(ctx['object'].category.id).ascendent_path()
        return ctx

Then render 'crumb_terms' somehow. If you would like anchors, and the Term model has a field 'slug', there is a templatetag,

<nav>
    {% breadcrumb crumb_terms %}
</nav>

which accepts optional args,

    url_prefix
        to go before the slug. default = '/category/'

Of course, this is not much control over rendering, but maybe you dont need that. The tag above renders as,

    <ul class="breadcrumb">
        <li><a href="/category/term_1">term 1</a></li>
        <li><a href="/category/term_2">term 2</a></li>
        ...
    </ul>


### Category links
Now the links need to go somewhere. All kinds of fancy pages nowadays, but classic web would be category links. Most sites add lists of attached objects. But if you have search enabled on your site, maybe you would want to got straight to that?

The more traditional non-search goes something like this. The usual Django shennanigans. Add a link in your URLs file,

    from taxonomy.views import CategoryDetailView

    urlpatterns = [
        path('category/<slug:slug>',  CategoryDetailView.as_view(), name='category_detail'), 
    ]

Then a DetailView. Note this isn't a ListView. Sure, we are listing things, but the basic idea here is 'something to do with a single category', not 'list categories',


    from django.views.generic import DetailView
    from taxonomy.models import Term
    from article.models import Page


    class CategoryDetailView(DetailView):
        model = Term
        context_object_name = 'category'
        # You chould shovel in some breadcrumb data
        ctx['crumb_terms'] = Term.api(ctx['object'].id).ascendent_path()
        # ...or element data from this category (this could use a related query if you have set up like that)
        ctx['elements'] = Page.objects.filter(category=ctx['object'])

Then a reverse URL on the model,

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('category_detail', kwargs={'slug': self.slug})

And a template, category_detail.py. That's entirely up to you.

This will do not much at all. Maybe you could print the term title, to cheer yourself up? But it is a blank page to go crazy on; load with search bars, gadget images, manipulative headlines, entrapment buttons; you could see it that way,



## Whole tree rendering
It's not often you see a whole tree rendered. Think of those sitemap modules that are always written and never used. Still, you may have reason for printing the tree, and there are a few ways.

### Flat Trees
Trees that are made of term data plus a depth. As used in the selector boxes in admin.

The tags and classes return HTML.

#### Template tags
There's a template tag that prints a depth tree in HTML. It uses a class FlatTreeRenderer but is easy to use, though operation is limited,

Use a view to send a tree (the usual depth-Term type),

    from taxonomy.taxonomy import TaxonomyAPI
        ....
        ctx['nav_bar'] = TaxonomyAPI(1).term(1).tree()

Render that data in a template with this tag,

    {% load taxonomy_displays %}
        ...
        {% flat_tree %}


#### FlatTreeRenderer
The tag uses a class inlintemplates.FlatTreeRenderer, which is more flexible than the tags. But, as it's a renderer, if you use that you need to render blocks inside the views, more or less bypassing the Django template engine. But maybe you don't mind.


### Stacked Trees
Trees that display terms on top of each other, extending downwards like roots on a plant. These displays use a lot of visual space. Only a small taxonomy can be displayed on a display.

The classes and tags return SVG graphics.

SVG graphics have advantages and disadvanatages.

Pros
- They are part of the webpage, so can be manipulated and searched like HTML
- They react structurally to DOM commands, such as zoom.
- they compress very small
- They have a full range of graphic manipulation available, can be customised with colour, sizing, and effects such as blur (expensive)

Cons
- They are part of the webpage, so add extra load to browser DOM manipulation
- They work with an absolute internal sizing. Font sizes are inherited, but no inheritance of CSS layout.


#### Template tags
There's a template tag that prints a tree in SVG. It uses StackTree but is easy to use, though operation is limited,

Use a view to send a tree (the usual depth-Term type),

    from taxonomy.taxonomy import TaxonomyAPI
        ....
        ctx['nav_bar'] = TaxonomyAPI(1).term(1).tree()

Then render that data with this tag,

    {% load taxonomy_displays %}
        ...
        {% stacked_tree nav_bar 400 12 %}

The two parameters define a ''box' size into which to write titles. As this is SVG, the text scales. To make text smaller, try make the sizes larger (which then get scaled down further. Sorry, not worked out my optimal solution for this, but it's fun).


#### StackTreeRenderer
The tags use a class inline_templates.Stacktree, which is more flexible than the tags. But, as it's a renderer, if you use that you need to render blocks inside the views, more or less bypassing the Django template engine. But maybe you don't mind.

    from django.utils.safestring import mark_safe
    from django.utils import html
    from taxonomy import api
    from taxonomy.inline_templates import TreeRender

    def get_title(pk):
        return html.escape(api.Taxonomy.term(pk).title)
    ...
    # 1. Get the tree
    api = TaxonomyAPI(1).term(1).tree()
    t = api.flat_tree()

    #3. Rend (needs a callback for data delivery into the template)
    tree = tr.rend_default_horizontal(t, 200, 14, get_title)
    
    #4. Deliver into the template
    article.body = mark_safe(tree)
    return render(request, 'article.html', {'article': article})


## Implementation notes
There are a few ways to implement a tree. Here is our version.

### Creating a Root Term
You can set any number of terms at base. If you would like a taxonomy where elements can be attached to a singular base, start a single term which will be the 'root term'. Build from there e.g. ::

    base = 'car categories'
    - Cars
    -- saloon 
    -- hatchback 
    -- sport
    ...
  
etc.

## EndNote
### The evironment
The Django system presents substancial difficulties to anyone implementing structures like this. The builtin admin may be customisable, but it's great blob of code is hard to extend. Then there is the issue of the ORM and foreign keys, about which you can say nothing, or write a book. Finally, though that would be unusual, Python has no support and there is no presentation logic. The only functionality on the coder's side is the model building, and hackability. It's clear other projects have wrestled with these issues. I'm just working as I can to make something usable.

### Straight vs. MPTT etc. implementation
Django-taxonomy uses direct links between its tree nodes. This is fundamentally different to an MPTT structure, which links tree nodes as a list, or a path structure. It's something like the difference between an array and a linked list. They both present a similar API, but the underlying implementation is different. There are advantages to both. An MPTT structure is excellent at gathering data from multiple categories, say 'cars', and all sub-categories. It is also capable of ordering it's categories and references exactly. Whereas the straight structure is poor at this, and I have not implemented either functionality. But the straight structure is simple to create and maintain, and good at displaying the categories themselves.
