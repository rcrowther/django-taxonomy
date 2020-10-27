## code-level templates
# (Mr. Lazy)

from django.utils.safestring import mark_safe
from django.utils import html
import math



class CrumbRenderer():
    def data_template(self, data):
        d = '<a href="{1}">{0}</a>'.format(
            html.escape(data.name),
            #? probably not escape, but something else to protect URLs
            html.escape(data.slug),
        )
        return d

    def rend(self, category, spacer="\u2007>\u2007"):
        '''
        tree
            [(depth, Cat)]
        '''
        b = ['<ul class="breadcrumb">']
        for e in category.api.ascendant_path().reverse():
            depth = e[0]
            b.append('<li>')
            b.append(self.data_template(e))
            b.append('</li>')
        b.append('</ul>')
        return ''.join(b)    


    
#? add attributes for wrapping tags.
class FlatTreeRenderer():
    def data_template(self, data):
        return html.escape(data.name)

    def rend(self, tree):
        '''
        tree
            [(depth, Term)]
        '''
        b = ['<ul class="tree">']
        prev_depth = 99999999

        for e in tree:
            depth = e[0]
            if (depth == 0):
                text = self.data_template(e[1])
            elif (prev_depth <= depth):
                # 9492,'u25114'' 9472 '\u2500'
                text = '\u2007\u2007\u2007\u2007' * (depth - 1) + '\u2007<span>└─</span>\u2007' + self.data_template(e[1])
            else:
                text = '\u2007\u2007\u2007\u2007' * (depth - 1) + '\u2007\u2007\u2007\u2007' + self.data_template(e[1])
            prev_depth = depth
            b.append('<li>')
            b.append(text)
            b.append('</li>')
        b.append('</ul>')
        return ''.join(b)
    

      
class AnchorFlatTreeRenderer(FlatTreeRenderer):
    '''
    Requires the callback on the renders to deliver
    tuples [(href, text)]
    '''
    def data_template(self, data):
        d = '<a href="{1}">{0}</a>'.format(
            html.escape(data.name),
            #? probably not escape, but something else to protect URLs
            html.escape(data.slug),
        )
        return html.escape(d)


        
        
    
class StackTreeRenderer():
    '''
    Render tree iters as a 2D graphics tree in HTML/SVG.
    
    The styles should be provides as SVG format e.g. 
    'stroke:rgb(0,220,126);stroke-width:4;'
    '''
    text_style = ''
    beam_style = 'stroke:black;stroke-width:4;stroke-linecap:square;'
    stem_style = 'stroke:black;stroke-width:2;'
    
    def text_template(self, x, y, cb_data):
        return ('<text x="{0}" y="{1}">{2}</text>').format(x, y, html.escape(cb_data))

    def rend_default(
            self, 
            tree, 
            x_space,
            data_height,
            data_callback = lambda d: d
        ):
        '''
        Render the tree with a set of defaults based on the height of
        the data to be displayed.
        '''
        return self.rend(
          tree, 
          x_space, 
          data_height * 4, 
          data_height * 1.5, 
          data_height * 2.5, 
          data_height,
          data_callback
        )

    def rend(self, 
        tree, 
        x_space, 
        y_space, 
        stem_offset,
        beam_offset,
        graphic_offset,
        data_callback = lambda d: d
        ):
        '''
        Render a tree as 2D SVG.
        
        This is an approximation towards a tree as humans like to see
        a tree, as roots of a plant. As such it transposes the usual
        computer representation of a ''sequence of items downwards"
        to "a sequence sideways". So it uses limited horizontal
        space very quickly.

        The tree is rendered as side-by-side boxes of x_xpace/y_space
        dimensions. The beam and stem marks are sketched in afterwards.
                
        Height and width of the finished tree are calculated on the fly
        (can not be provided as initial constraints).
        
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
            function to accept data from each element in the tree then 
            return some text. Default returns the data itseelf, which 
            assumes the data is text. 
        return 
            An SVG definition, suitable for embedding in an HTML
        document. The default uses a ViewPort, which means it sizes to
        it's container. Note an odd effect, though, text scales with the
        image, not flows (like CSS), All data is escaped.
        '''
        depth = 0
        ## Where items of data will be printed
        x = 0
        y = 0
        ## The dummy tag will be filled later when the dimensions can be
        # calculated 
        b = ['dummy_svg_tag']
        depth_x_memory = [0 for x in range(20)]
        prev_depth = 0
        ## track of the extent of the virtual area.
        x_max = x
        y_max = y

        for depth, data in tree:
            y = ((depth) * y_space)
            y_max = max(y_max, y)
            if(depth > prev_depth):
                # it's a child
                # remember where this layer was positioned
                depth_x_memory[prev_depth] = x
                # do not move x 
            elif(depth < prev_depth):
                # it's a return to lower taxonomies
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
            text = data_callback(data)
            b.append(self.text_template(x, y, text))   
            prev_depth = depth
        b.append('</svg>')
        # replacing 'dummy_div'
        #b[0] = self.svg_template(x_max + x_space, y_max + math.floor(y_space / 2))
        b[0] =  '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {0} {1}">'.format(
            x_max + x_space,
            y_max + math.floor(y_space / 2)
        )
        return ''.join(b)
  
     
      
class AnchorStackTreeRenderer(StackTreeRenderer):
    '''
    Requires the callback on the renders to deliver
    tuples [(href, text)]
    '''
    def text_template(self, x, y, cb_data):
        return ('<a xlink:href="{2}"><text x="{0}" y="{1}">{3}</text></a>').format(
            x, 
            y, 
            cb_data[0], 
            cb_data[1]
        )
