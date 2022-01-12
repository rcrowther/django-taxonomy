import math
from django.utils.safestring import mark_safe
from django.utils import html
from django.forms.utils import flatatt
from taxonomy import BIG_DEPTH



# NEW
class FlatTreeRenderer():
    '''
    Render a tree  as list items with depth as sublists
    Template needs to add outer list elements.
    '''
    sublist_attrs={}
    listitem_attrs={}
    data_attrs={}
    
    def data_template(self, data, dataattr_str):
        return data.name
            
    def rend(self, 
        tree, 
        sublist_attrs={},
        listitem_attrs={},
        data_attrs={}
        ):
        '''
        tree
            [(depth, Term)]
        '''
        self.sublist_attrs.update(sublist_attrs)
        self.listitem_attrs.update(listitem_attrs)
        self.data_attrs.update(data_attrs)
        b = []
        prev_depth = 0
        list_str = '<ul {} />'.format(flatatt(self.sublist_attrs))
        listitem_str = '<li {} />'.format(flatatt(self.listitem_attrs))
        dataattr_str = '{}'.format(flatatt(self.data_attrs))
        first_item = True
        
        for depth, data in tree:
            rend_data = self.data_template(data, dataattr_str) 
            if (prev_depth == depth):
                if (first_item == False):
                    b.append('</li>')
                else:
                    first_item = False
                b.append(listitem_str)
                b.append(rend_data)
            elif (prev_depth < depth):
                b.append(list_str)
                b.append(listitem_str)
                b.append(rend_data)
            else:
                b.append('</li>')
                i = prev_depth - depth
                while (i > 0):
                    b.append('</ul>')
                    b.append('</li>')
                    i -= 1
                b.append(listitem_str)
                b.append(rend_data)
            prev_depth = depth

        # close what we are on
        b.append('</li>')            
            
        # Need close codes for unclosed depths (likely!)
        while (prev_depth > 0):
            b.append('</ul>')
            b.append('</li>')
            prev_depth -= 1            
            
        return ''.join(b)
           
           
              
class FlatTreeRendererAsLinks(FlatTreeRenderer):
    '''
    Render a tree  as list items containing anchors, with depth as 
    sublists.
    Template needs to add outer list elements.
    '''
    url_prefix ='/category/'

    def data_template(self, 
        data,
        dataattr_str
        ):
        return '<a href="{url_prefix}{url_id}" {attrs}>{text}</a>'.format(
            url_prefix=self.url_prefix,
            #! probably not escape, but something else to protect URLs
            url_id = data.slug,
            attrs = dataattr_str,
            text= html.escape(data.name),
        )



class NodeListRenderer():
    '''
    Render a node list as list items.
    Template needs to add outer list elements.
    '''
    listitem_attrs={}
    data_attrs={}
    
    def data_template(self, data, dataattr_str):
        return data.name

    def rend(self, 
        node_list, 
        listitem_attrs={},
        data_attrs={}
        ):
        '''
        node_list
            [taxonomy_nodes]
        '''
        self.listitem_attrs.update(listitem_attrs)
        self.data_attrs.update(data_attrs)
        b = []
        listitem_str = '<li {} />'.format(flatatt(self.listitem_attrs))
        dataattr_str = '{}'.format(flatatt(self.data_attrs))
        for e in node_list:
            b.append(listitem_str)
            b.append(self.data_template(e, dataattr_str))
            b.append('</li>')
        return ''.join(b)    



class NodeListRendererAsLinks(NodeListRenderer):
    '''
    Render a node list as list items containing anchors.
    Template needs to add outer list elements.
    '''
    url_prefix ='/category/'

    def data_template(self, 
        data,
        dataattr_str
        ):
        return '<a href="{url_prefix}{url_id}" {attrs}>{text}</a>'.format(
            url_prefix=self.url_prefix,
            #! probably not escape, but something else to protect URLs
            url_id = data.slug,
            attrs = dataattr_str,
            text = html.escape(data.name),
        )
           
           
           
             
# OLD

## code-level templates
class AnchorNodeListRenderer():
    url_prefix ='/category/'

    def data_template(self, ctx):
       return '<a href="{url_prefix}{url_id}">{text}</a>'.format(
            url_prefix=ctx['url_prefix'],
            #? probably not escape, but something else to protect URLs
            url_id=ctx['url'],
            text=ctx['text'],
        )

    def get_context(self, data):
        return {
            'text': html.escape(data.name),
            'url_prefix' : self.url_prefix,
            'url' : data.slug,
        }
        
    def rend(self, node_list, klass='breadcrumb'):
        '''
        tree
            [(depth, Cat)]
        '''
        b = ['<ul class="{}">'.format(klass)]
        for e in node_list:
            b.append('<li>')
            b.append(self.data_template(self.get_context(e)))
            b.append('</li>')
        b.append('</ul>')
        return ''.join(b)    


    
#? add attributes for wrapping tags.
class FlatTreeRendererMark():
    '''
    Render a tree  as list items with depth indications
    '''
    def data_template(self, ctx):
        return ctx['text']

    def get_context(self, data):
        return {
            'text': html.escape(data.name)
            }
            
    def rend(self, tree, klass='tree'):
        '''
        tree
            [(depth, Term)]
        '''
        b = ['<ul class="{}">'.format(klass)]
        prev_depth = BIG_DEPTH

        for depth, data in tree:
            rend_data = self.data_template(self.get_context(data)) 
            if (depth == 0):
                text = rend_data
            elif (prev_depth <= depth):
                # 9492,'u25114'' 9472 '\u2500'
                text = '\u2007\u2007\u2007\u2007' * (depth - 1) + '\u2007<span>└─</span>\u2007' + rend_data
            else:
                text = '\u2007\u2007\u2007\u2007' * (depth - 1) + '\u2007\u2007\u2007\u2007' + rend_data
            prev_depth = depth
            b.append('<li>')
            b.append(text)
            b.append('</li>')
        b.append('</ul>')
        return ''.join(b)

class AnchorFlatTreeRendererMark(FlatTreeRendererMark):
    '''
    Requires the callback on the renders to deliver
    tuples [(href, text)]
    '''
    url_prefix ='/category/'

    def data_template(self, ctx):
        return '<a href="{url_prefix}{url_id}">{text}</a>'.format(
            url_prefix=ctx['url_prefix'],
            #! probably not escape, but something else to protect URLs
            url_id=ctx['url'],
            text=ctx['text'],
        )

    def get_context(self, data):
        return {
            'text': html.escape(data.name),
            'url_prefix' : self.url_prefix,
            'url' : data.slug,
        }    


   
    
class StackTreeRenderer():
    '''
    Render tree iters as a 2D graphics tree in HTML/SVG.
    
    The styles should be provides as SVG format e.g. 
    'stroke:rgb(0,220,126);stroke-width:4;'
    '''
    text_style=''
    beam_style = 'stroke:black;stroke-width:4;stroke-linecap:square;'
    stem_style = 'stroke:black;stroke-width:2;'
    
    def data_template(self, x, y, ctx):
        '''
        SVG template forr data extracted from the tree.
        Builtin assumes given data will be text.
        '''
        return ('<text x="{0}" y="{1}"style="{text_style}">{text}</text>').format(
            x, 
            y,             
            text=ctx['text'],
            text_style=self.text_style,
            )

    def get_context(self, data):
        return {
            'text': html.escape(data.name)
            }
        
    def rend_default(
            self, 
            tree, 
            x_space,
            data_height,
        ):
        '''
        Render the tree with a set of defaults based on the height of
        the data to be displayed.
        x_space
            box width in SVG units
        data_height
            A box height. Also used to calculate stem and beam
            proportions in a default
        '''
        return self.rend(
          tree, 
          x_space, 
          data_height * 4, 
          data_height * 1.5, 
          data_height * 2.5, 
          data_height,
        )

    def rend(self, 
        tree, 
        x_space, 
        y_space, 
        stem_offset,
        beam_offset,
        graphic_offset,
        ):
        '''
        Render a tree as 2D SVG.
        
        This is an approximation towards a tree as humans like to see
        a tree, as roots of a plant. As such it transposes the usual
        computer representation of a "a sequence downwards, with depth"
        to "a sequence downwards, children horizontal". Since cildren 
        expand horizontally, it uses limited horizontal space very 
        quickly.

        The tree is rendered as side-by-side boxes of x_xpace/y_space
        dimensions. The beam and stem marks are sketched in afterwards.
                
        Height and width of the finished tree are calculated on the fly
        (can not be provided as initial constraints).

        Default setup requires a tree (depth, Node) where Nodes carry 
        a 'name' field. Use 'get_context' to override data retrieval.
            
        tree
            [(depth, data)]
        @param x_space at least the largest width of data to be printed
        @param y_space at least the largest height of data to be 
        printed, plus beam/stem space. For horizontal text, 4 * text hight
        is a good start.
        @param stem_offset height above data before the stem starts. For
        horizontal text, 1.5 * text hight is a good start.
        @param beam_offset height above data for the beam. For
        horizontal text, 2.5 * text hight is a good start.
        @param graphic_offset x offset of all stem/beam graphics. For
        horizontal text, text hight is a good start.
        data_callback 
            function to extract data from each element in the tree. 
            Default returns the data itself, which assumes the data is 
            text. 
        return 
            An SVG definition, suitable for embedding in an HTML
            document. The default sizes to it's container.
            Text scales with the x,y sizes, not the webpage. It will
            resize with the image. Default data template escapes data.
        '''
        depth = 0
        ## Where items of data will be printed
        x = 0
        y = 0
        ## The dummy tag will be set later when the dimensions can be
        # calculated 
        b = ['dummy_svg_tag']
        # excessive, but I see no other way.
        depth_x_memory = [0 for x in range(len(tree))]
        prev_depth = -1
        ## track of the extent of the virtual area.
        # Note this is the left of the text area
        x_max = x
        y_max = y

        for depth, data in tree:
            y = ((depth) * y_space)
            y_max = max(y_max, y)
            if(depth > prev_depth):
                # it's a child
                # remember where prev layer was positioned
                depth_x_memory[prev_depth] = x
                # do not move x 
            # elif(depth == 0):
                # # it's a root item
                # x = x_max + x_space
                # # note the max extent
                # x_max = x
                # # needs no beam (or stem)                
            elif(depth < prev_depth):
                # it's a return to lower taxonomies (but not a root)
                # need to go one beyond current max
                x = x_max + x_space
                # note the max extent
                x_max = x
                # need a beam line from the previous position. This item
                # is always a sibling
                x_start = depth_x_memory[depth]
                b.append('<line x1="{0}" y1="{2}" x2="{1}" y2="{2}" style="{3}" />'.format(
                    x_start + graphic_offset, 
                    x + graphic_offset, 
                    y - beam_offset, 
                    self.beam_style
                ))
            else:
                # it's a sibling
                # move x along
                x_start = x
                x = x + x_space
                x_max = max(x_max, x)
                # print beam line from prev x to this
                b.append('<line x1="{0}" y1="{2}" x2="{1}" y2="{2}" style="{3}" />'.format(
                    x_start + graphic_offset, 
                    x + graphic_offset, 
                    y - beam_offset, 
                    self.beam_style
                ))
            #  print a stem line
            b.append('<line x1="{0}" y1="{1}" x2="{0}" y2="{2}" style="{3}" />'.format(
                x + graphic_offset, 
                y - stem_offset, 
                y - beam_offset, 
                self.stem_style
                ))
            # Now append the data  
            b.append(self.data_template(x, y, self.get_context(data)))   
            prev_depth = depth
        b.append('</svg>')
        # replacing 'dummy_div'
        # Need to be very tricky with the viewbox, Im afraid.
        # First x_max means left pos of the last text, so needs extra 
        # padding to the right, to cover the text itself. Also needs 
        # padding to the left, to balance that visually.
        # Next, y_max starts at 0, as depths start at zero. So a 
        # symetrical problem to x-axis, must start with padding to cover
        # the opening text. 
        # finally, to reduce the amount of padding this implies, I've 
        # halved the space, but that can not be done with y start...
        x_padding = math.floor(x_space / 2)
        y_padding = math.floor(y_space / 2)
        b[0] =  '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="{x_min} {y_min} {x_width} {y_max}" height="100%">'.format(
            x_min = -x_padding,
            y_min = -y_space,
            x_width=x_max + (2 * x_padding),
            y_max=y_max + (y_space + y_padding)
        )
        return ''.join(b)
  
     
      
class AnchorStackTreeRenderer(StackTreeRenderer):
    '''
    Render an SVG Stacktree with web anchors.
    Default setup requires a tree (depth, Node) where Nodes carry 'name' 
    and 'slug' fields. Use 'get_context' to override data retrieval.
    '''
    text_style='fill:cornflowerblue;'
    url_prefix ='/category/'

    def data_template(self, x, y, ctx):
        return ('<a xlink:href="{url_prefix}{url_id}"><text x="{0}" y="{1}" style="{text_style}">{text}</text></a>').format(
            x, 
            y, 
            url_prefix=ctx['url_prefix'],
            url_id=ctx['url'],
            text=ctx['text'],
            text_style=self.text_style,
        )

    def get_context(self, data):
        return {
            'text': html.escape(data.name),
            'url' : data.slug,
            'url_prefix' : self.url_prefix
        }
