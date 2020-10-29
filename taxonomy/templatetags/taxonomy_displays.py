from django import template
from taxonomy.inline_templates import FlatTreeRenderer, StackTreeRenderer
from django.utils.safestring import mark_safe


register = template.Library()

# https://css-tricks.com/scale-svg/
class StackedTreeRendererNode(template.Node):
    def __init__(self, tree_data, x_space, data_height):
        self.renderer = StackTreeRenderer()
        self.tree_data = template.Variable(tree_data)
        self.x_space = int(x_space)
        self.data_height = int(data_height)
        
    def render(self, context):
        r = self.renderer.rend_default( 
            self.tree_data.resolve(context), 
            self.x_space, 
            self.data_height,
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
from django.forms.utils import flatatt

class NodeAnchorNode(template.Node):
    #! not threadsafe
    def __init__(self, node_list, url_id_field, url_stub, kwargs):
        self.node_list = template.Variable(node_list)
        self.url_id_field = url_id_field
        self.url_stub = url_stub
        self.kwargs = kwargs

    def render(self, context):
        b = ['<ul {} />'.format(flatatt(self.kwargs))]
        for e in self.node_list.resolve(context):
            b.append('<li>')
            b.append('<a href="{0}{1}">{2}</a>'.format(
                self.url_stub,
                #? probably not escape, but something else to protect URLs
                getattr(e, self.url_id_field),
                html.escape(e.name),
                )
            )
            b.append('</li>')
        b.append('</ul>')
        return mark_safe(''.join(b))

@register.tag        
def node_anchors(parser, token):
    '''
    Make anchors from a list of data (presumably Nodes).
    Looks for a 'slug' and 'name' field
    Undocumented keyword arguments are rendered as HTML attributes.

    url_prefix
        Prefix to go before the slug in the anchor URL e.g. url_prefix =
        'dvds', rende as href = '/dvds/fred_astaire' 
        Default '/category/'
    url_id_field
        Fieldname for id data for the URL. Default 'slug'
    '''
    lumps = token.split_contents()
    if(len(lumps) < 2):
        raise template.TemplateSyntaxError(
            "Breadcrumb tag needs one positional argument for data. tag:{{% {} %}}".format(
                token.contents,
            ))
    tag_name = lumps[0]
    node_list = lumps[1]
    kwargs = to_kwargs(token, lumps[2:])
    url_prefix = kwargs.pop('url_prefix', None) or '/category/'
    url_id_field = kwargs.pop('url_id_field', None) or 'slug'
    return NodeAnchorNode(node_list, url_id_field, url_prefix, kwargs)
