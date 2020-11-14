from collections import namedtuple
from django.core.exceptions import ObjectDoesNotExist
from taxonomy import NO_PARENT, BIG_DEPTH



DepthNid = namedtuple('DepthNid', ['depth', 'nid'])
DepthNode = namedtuple('DepthNode', ['depth', 'cat'])



class ChoiceIterator:
    def __init__(self, depthNodes):
        self.depthNodes = depthNodes

    def __iter__(self):
        yield (NO_PARENT, 'None (root cat)')
        prev_depth = BIG_DEPTH
        for e in self.depthNodes:
            b = []
            depth = e.depth
            if (depth == 0):
                title = e.cat.name
            elif (prev_depth <= depth):
                title = '\u2007\u2007\u2007\u2007' * (depth - 1) + '\u2007└─\u2007' + e.cat.name
            else:
                title = '\u2007\u2007\u2007\u2007' * (depth - 1) + '\u2007\u2007\u2007\u2007' + e.cat.name
            prev_depth = depth
            yield (e.cat.id, title)


            
class NodeMethods:
    '''
    API for taxonomy models.
    '''
    def __init__(self, 
        model_node, 
        model_nodeparent, 
        cache, 
        node_id
    ):
        self.model_node = model_node 
        self.model_nodeparent = model_nodeparent 
        self.cache = cache
        self.id = node_id

    def node(self):
        return self.cache.node_map()[self.id]
        
    def depth(self):
        pos = self.cache.tree_locations().get(self.id)
        tree = self.cache.ftree()
        return tree[pos].depth

    def id_parent(self):
        pid = self.cache.parent_map()[self.id]
        if (pid == NO_PARENT):
            return None
        else:
            return pid

    def id_children(self):
        # catch NO_PARENT
        nid = self.id if (self.id > 0) else NO_PARENT
        return self.cache.child_map()[nid]
                                
    def parent(self):
        '''
        return
            Cat. If NO_PARENT, None
        '''
        pid = self.cache.parent_map()[self.id]
        if (pid == NO_PARENT):
            return None
        else:
            return self.cache.node_map()[pid]

    def children(self):
        '''
        return
            [Cat, ...]
        '''
        # catch NO_PARENT
        nid = self.id if (self.id != 0) else NO_PARENT
        node_map = self.cache.node_map()
        return [node_map[e] for e in self.cache.child_map()[nid]]

        
    def id_ascendants(self):
        '''
        Category ascendants
        The return is ordered as a single path.
        Includes the original id.
        return
            [id, ....]
        '''
        parent_map = self.cache.parent_map()
        nid = parent_map[self.id]
        b = []
        while (nid != NO_PARENT):
            b.append(nid)
            nid = parent_map[nid]
        return b
        
    def id_descendants(self, include_self=False):
        '''
        Category descendants
        The return is disorganised and does not structure for
        paths.
        Does not include the original id.
        return
            [id, ....]
        '''
        child_map = self.cache.child_map()
        stack = list.copy(child_map[self.id])
        b = []
        while (stack):
            nid = stack.pop()
            b.append(nid)
            stack.extend(list.copy(child_map[nid]))
        if (include_self):
            b.append(self.id)
        return b

    def ascendants(self):
        '''
        Disorganised collection of all ascendants.
        '''
        node_map = self.cache.node_map()
        ascendants = self.id_ascendants()
        return [ node_map[nid] for nid in ascendants ]
        
    def descendants(self, include_self=False):
        '''
        Disorganised collection of all descendants.
        '''
        node_map = self.cache.node_map()
        descendants = self.id_descendants(include_self)
        return [ node_map[nid] for nid in descendants ]
        
    def depth_id_ascendant_path(self, exclude_self=False):
        '''
        Tree ascscendants
        return
            [DepthNid, ....], ordered from root to target category.
        '''
        pos = self.cache.tree_locations().get(self.id)
        tree = self.cache.ftree()
        e = tree[pos]
        b = [e]       
        base_depth = e.depth - 1      
        while (base_depth > -1):
            pos -= 1  
            e = tree[pos]
            if (base_depth >= e.depth):
                b.append(e)
                base_depth -= 1
        b.reverse()
        if (exclude_self):
            b.pop()
        return b

    def depth_id_descendant_paths(self):
        '''
        Tree descendant paths
        Each path is a full route from the Category to a leaf,
        return
            [[DepthNid, ...], ...], ordered
        '''
        tree = self.cache.ftree()
        l = len(tree)
        pos = self.cache.tree_locations().get(self.id)
        e = tree[pos]
        base_depth = e.depth
        current_depth = base_depth
        stack = []
        
        # carries each path as it is built
        b = []
        pos += 1        
        while (pos < l):
            e = tree[pos]
            prev_depth = current_depth
            current_depth = e.depth
            if (current_depth <= base_depth):
                # i.e. if not a descendant of the given nid
                break
            if (current_depth <= prev_depth):
                # path finished, need to build new one
                stack.append(list.copy(b))
                # stem for the new path
                # needs to be relative to nid depth, as the builder path
                # is also
                b = b[:(current_depth - base_depth - 1)]
            b.append(e)
            pos += 1        
        if (b):
            stack.append(b)            
        return stack
        
    def ascendant_path(self, exclude_self=False):
        '''
        Path of Categories 
            [Cat, ....], ordered from root to target category.
        '''
        node_map = self.cache.node_map()
        path = self.depth_id_ascendant_path(exclude_self)
        return [ node_map[e.nid] for e in path ]
    
    def descentant_paths(self):
        node_map = self.cache.node_map()
        paths = self.depth_id_descendant_paths()
        return [ [node_map[e.nid] for e in path] for path in paths]

        
    def depth_id_tree(self, max_depth=None):
        '''
        Tree of depths and category ids.
        
        return
            [DepthNid, ...] depth from 9
        '''
        # depth is from main tree, not relative?
        tree = self.cache.ftree()
        l = len(tree)
        pos = self.cache.tree_locations().get(self.id)
        e = tree[pos]
        base_depth = e.depth
        max_depth = max_depth if max_depth else BIG_DEPTH
        b = [DepthNid(0, e.nid)]
        pos += 1        
        while (pos < l):
            e = tree[pos]
            reldepth = e.depth - base_depth
            if (reldepth < 1):
                # i.e. if not a descendant of the given nid
                break
            if (reldepth < max_depth):
                b.append(DepthNid(reldepth, e.nid)) 
            pos += 1        
        return b      


    def tree(self, max_depth=None):
        '''
        Tree
        return
            [DepthNode(depth, Cat)]
        '''
        node_map = self.cache.node_map()
        tree = self.depth_id_tree(max_depth)
        return [DepthNode(e.depth, node_map[e.nid]) for e in tree]
        
    def delete(self):
        '''
        Delete the Category and contents.
        Removes descendant categories and
        attached elements.
        ''' 
        descendant_nids = self.id_descendants()
        # because base Category is not in the descendants
        descendant_nids.append(self.id)
        self.model_nodeparent.objects.filter(nid__in=descendant_nids).delete()
        self.model_node.objects.filter(id__in=descendant_nids).delete()
        self.cache.clear()

    def reparent_choices(self):
        '''
        choices for a category parent update
        These are limited comared to creation. Updating only allows 
        attachment to categories that are not descendants, to avoid circular 
        references.
        '''
        #? This feels like a shambles. but the slick thing would be
        # tree ids no descendants?
        descendants = self.id_descendants()
        # add in the seed node_id. Don't want to parent on ourself
        descendants.append(self.id)
        # get them all. seems easier right now if sloooooow.
        non_descendant_id_tree = (e for e in self.cache.ftree() if (not(e.nid in descendants)))
        node_map = self.cache.node_map()
        return list(ChoiceIterator([DepthNode(e.depth, node_map[e.nid]) for e in non_descendant_id_tree]))

        
        
        
class NodeTreeAPI:
    '''
    API for taxonomy models.
    '''
    def __init__(self, 
        model_node, 
        model_nodeparent, 
    ):
        self.model_node = model_node 
        self.model_nodeparent = model_nodeparent 
    
        # cache
        self._parents = {}
        self._children = {}
        self._nodes = {}
        self._ftree = None
        self._tree_locations = None

    def generate_base_data(self):
        from django.db import connection
        nodes = {}
        parents = {}
        children = {}
        PID_Weighted_SQL = "SELECT t.*, tp.pid FROM {} tp INNER JOIN {} t ON tp.nid = t.id ORDER BY t.weight".format(
            self.model_nodeparent._meta.db_table,
            self.model_node._meta.db_table,
            )
        with connection.cursor() as cursor:
            cursor.execute(PID_Weighted_SQL)
            for r in cursor.fetchall():
                nid = r[0]
                nodes[nid] = self.model_node(*r[:-1])
                parents[nid] = r[-1]
                # Only set up children for later population.
                # Setup here ensures every nid is accounted for.
                children[nid] = []
        # and ensure NO_PARENTS entry
        children[NO_PARENT] = []
        for (nid, pid) in parents.items():
            children[pid].append(nid)
        self._nodes = nodes
        self._parents = parents
        self._children = children

    #NB self.children will always have a NO_PARENT entry unless cleared.
    def child_map(self):
        if (not self._children):
            self.generate_base_data()
        return self._children 

    def parent_map(self):
        if (not self._children):
            self.generate_base_data()
        return self._parents 

    def node_map(self):
        if (not self._children):
            self.generate_base_data()
        return self._nodes
    
    def _generate_tree(self):
        '''
        return
            [DepthNid] Tree depths are from 0...
        '''
        child_map = self.child_map() 
        stack = [iter(child_map[NO_PARENT])]
        depth = 0
        while (stack):
            depth = len(stack) - 1
            it = stack.pop()
            while(True):
                try:
                    nid = it.__next__()
                except StopIteration:
                    # exhausted. Pop a iter at a previous depth
                    break
                yield DepthNid(depth, nid)
                child_ids = child_map[nid]
                if (child_ids):
                    # append current iter, will return after processing children
                    stack.append(it)
                    # append new depth of iter
                    stack.append(iter(child_ids))
                    break

    def ftree(self):
        '''
        The tree for this taxonomy
        return
              [DepthNid, ...], ordered
        '''
        if (self._ftree is None):
            # list, because we need to run the generator, or it will
            # exhaust on multiple calls
            self._ftree = list(self._generate_tree())
        return self._ftree
    
    # index
    #IdxDepth = namedtuple('IdxDepth', ['idx', 'depth'])

    def tree_locations(self):
        if (self._tree_locations is None):
            self._tree_locations = {e.nid : idx for idx, e in enumerate(self.ftree())}
        return self._tree_locations
                 
    def clear(self):
        '''
        Empty cache for a given taxonomy
        '''
        self._parents = {}
        self._children = {}
        self._nodes = {}
        self._ftree = None
        self._tree_locations = None
        
    def __call__(self, *args, **kwargs):
        if args:
            node_id = args[0]
        else:
            node_id = self.model_node.objects.get(**kwargs).id
        return NodeMethods( 
            self.model_node, 
            self.model_nodeparent, 
            self, 
            node_id
        )

    def save(self, new_parent_id, obj):
        '''
        Save a category.
        Add necessary parentage on new category. Category parent is not checked 
        against taxonomy_id.
        '''
        self.model_node.save(obj)
        try:
            o = self.model_nodeparent.objects.get(nid=obj.id)
            o.pid = new_parent_id
        except ObjectDoesNotExist:
            o = self.model_nodeparent(pid=new_parent_id, nid=obj.id)
        self.model_nodeparent.save(o)
        self.clear()

    def delete(self):
        '''
        Delete the tree.
        Includes categories, and parentage.
        '''
        self.model_nodeparent.objects.all().delete()
        self.model_node.objects.all().delete()
        self.clear()

    def depth_id_tree(self, max_depth=None):
        if (max_depth is None):
            return list.copy(self.ftree())
        else:
            return [e for e in self.ftree() if e.depth < max_depth]

    def tree(self, max_depth=None):
        '''
        Tree
        return
            [(depth, Cat)]
        '''
        node_map = self.node_map()
        return [DepthNode(e.depth, node_map[e.nid]) for e in self.depth_id_tree(max_depth)]
                
    def initial_choices(self):
        '''
        Choices for parenting a category on creation
        '''
        return list(ChoiceIterator((e for e in self.tree())))
