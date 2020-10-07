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
