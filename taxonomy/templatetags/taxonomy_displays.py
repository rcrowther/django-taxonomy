from django import template
from taxonomy.inline_templates import FlatTreeRenderer, StackTreeRenderer
from django.utils.safestring import mark_safe


register = template.Library()


class StackedTreeRendererNode(template.Node):
    def __init__(self, tree_data, x_space, data_height):
        self.tree_data = template.Variable(tree_data)
        self.x_space = int(x_space)
        self.data_height = int(data_height)
        
    def render(self, context):
        renderer = StackTreeRenderer()
        
        r = renderer.rend_default( 
            self.tree_data.resolve(context), 
            self.x_space, 
            self.data_height,
            lambda e: e.title
            )
        return mark_safe(r)

@register.tag        
def stacked_tree(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
       tag_name, tree_data, x_space, data_height = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires arguments: tree_data, x_space, data_height" % token.contents.split()[0]
        )

    return StackedTreeRendererNode(tree_data, x_space, data_height)
    


class FlatTreeRendererNode(template.Node):
    def __init__(self, tree_data):
        self.tree_data = template.Variable(tree_data)
        
    def render(self, context):
        renderer = FlatTreeRenderer()
        
        r = renderer.rend( 
            self.tree_data.resolve(context), 
            )
        return mark_safe(r)

@register.tag        
def flat_tree(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
       tag_name, tree_data = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires arguments: tree_data" % token.contents.split()[0]
        )

    return FlatTreeRendererNode(tree_data)


def to_kwargs(token, kwlumps):
    kwargs = {}

    for kw in kwlumps:
        k_v = kw.split("=", 1)
        if (not(len(k_v) == 2)):
            raise template.TemplateSyntaxError("Expected kw argument. tag:{{% {} %}} kw:{}".format(
               token.contents,
               kw
           ))
        k = k_v[0]
        v = k_v[1]
        if not (v[0] == v[-1] and v[0] in ('"', "'")):
           raise template.TemplateSyntaxError(
               "tag keyword argument values must be in quotes. tag:{{% {} %}} kw:{}".format(
               token.contents,
               kw
           ))
        kwargs[k] = v[1:-1]
           
    return kwargs

from django.utils import html

class BreadcrumbNode(template.Node):
    def __init__(self, crumb_terms, url_stub):
        self.crumb_terms = template.Variable(crumb_terms)
        self.url_stub = url_stub
        
    def render(self, context):
        b = ['<ul class="breadcrumb">']
        for e in self.crumb_terms.resolve(context):
            b.append('<li>')
            b.append('<a href="{0}{1}">{2}</a>'.format(
                self.url_stub,
                #? probably not escape, but something else to protect URLs
                e.slug,
                html.escape(e.name),
                )
            )
            b.append('</li>')
        b.append('</ul>')
        #raise Exception
        return mark_safe(''.join(b))

@register.tag        
def breadcrumb(parser, token):
    '''
    Make a breadcrumb from a list of data (presumably Terms).
    Looks for a 'slug' and 'name' field
    
    url_prefix
        prefix to go before the slug in the anchor URL e.g. url_prefix =
        'dvds', rende as href = '/dvds/fred_astaire' 
        default = '/category/'
    '''
    lumps = token.split_contents()
    if(len(lumps) < 2):
        raise template.TemplateSyntaxError(
            "Breadcrumb tag needs one positional argument for data. tag:{{% {} %}}".format(
                token.contents,
            ))
    tag_name = lumps[0]
    crumb_terms = lumps[1]
    kwargs = to_kwargs(token, lumps[2:])
    print('template')
    print(str(kwargs))
    url_prefix = kwargs.get('url_prefix') or '/category/'
    return BreadcrumbNode(crumb_terms, url_prefix)
