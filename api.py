from collections import namedtuple
from django.core.exceptions import ObjectDoesNotExist

 

# constants
NO_PARENT = -1
BIG_DEPTH = 9999999999

DepthTid = namedtuple('DepthTid', ['depth', 'tid'])
DepthTerm = namedtuple('DepthTerm', ['depth', 'term'])

# class NoTermElementTable(AttributeError):
    # pass

class ChoiceIterator:
    def __init__(self, depthTerms):
        self.depthTerms = depthTerms

    def __iter__(self):
        #yield (TermParent.NO_PARENT, 'None (root term)')
        yield (NO_PARENT, 'None (root term)')
        prev_depth = 99999999
        for e in self.depthTerms:
            #print('ChoiceIterator')
            #print(str(e.depth))
            b = []
            depth = e.depth
            if (depth == 0):
                #title = terms(self.taxonomy_id)[e.tid].name
                title = e.term.name
            elif (prev_depth <= depth):
                title = '\u2007\u2007\u2007\u2007' * (depth - 1) + '\u2007└─\u2007' + e.term.name
            else:
                title = '\u2007\u2007\u2007\u2007' * (depth - 1) + '\u2007\u2007\u2007\u2007' + e.term.name
            prev_depth = depth
            yield (e.term.id, title)


            
class TermMethods:
    '''
    API for taxonomy models.
    '''
    def __init__(self, 
        model_term, 
        model_termparent, 
        cache, 
        term_id
    ):
        self.model_term = model_term 
        self.model_termparent = model_termparent 
        self.cache = cache
        self.id = term_id

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
        tid = self.id if (self.id > 0) else NO_PARENT
        return self.cache.child_map()[tid]
                                
    def parent(self):
        '''
        return
            Term. If NO_PARENT, None
        '''
        pid = self.cache.parent_map()[self.id]
        if (pid == NO_PARENT):
            return None
        else:
            return self.cache.term_map()[pid]

    def children(self):
        '''
        return
            [Term, ...]
        '''
        # catch NO_PARENT
        tid = self.id if (self.id != 0) else NO_PARENT
        term_map = self.cache.term_map()
        return [term_map[e] for e in self.cache.child_map()[tid]]

        
    def id_ascendants(self):
        '''
        Term ascendants
        The return is ordered as a single path.
        Includes the original id.
        return
            [id, ....]
        '''
        parent_map = self.cache.parent_map()
        tid = parent_map[self.id]
        b = []
        while (tid):
            b.append(tid)
            tid = parent_map[tid]
        return b
        
    def id_descendants(self):
        '''
        Term descendants
        The return is disorganised and does not structure for descendant
        paths.
        Does not include the original id.
        return
            [id, ....]
        '''
        child_map = self.cache.child_map()
        stack = list.copy(child_map[self.id])
        b = []
        while (stack):
            tid = stack.pop()
            b.append(tid)
            stack.extend(list.copy(child_map[tid]))
        return b

    def depth_id_ascendent_path(self):
        '''
        Tree ascscendants
        return
            [DepthTid, ....], ordered from root to target term.
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
        return b

    def depth_id_descendant_paths(self):
        '''
        Tree descendant paths
        Each path is a full route from the Term to a leaf,
        return
            [[DepthTid, ...], ...], ordered
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
                # i.e. if not a descendant of the given tid
                break
            if (current_depth <= prev_depth):
                # path finished, need to build new one
                stack.append(list.copy(b))
                # stem for the new path
                # needs to be relative to tid depth, as the builder path
                # is also
                b = b[:(current_depth - base_depth - 1)]
            b.append(e)
            pos += 1        
        if (b):
            stack.append(b)            
        return stack
        
    def ascendent_path(self):
        '''
        Path of Terms 
            [Term, ....], ordered from root to target term.
        '''
        term_map = self.cache.term_map()
        path = self.depth_id_ascendent_path()
        return [ term_map[e.tid] for e in path ]
    
    def descentant_paths(self):
        term_map = self.cache.term_map()
        paths = self.depth_id_descendant_paths()
        return [ [term_map[e.tid] for e in path] for path in paths]

    def depth_id_tree(self, max_depth=None):
        '''
        Tree of depths and term ids.
        
        return
            [DepthTid, ...] depth from 9
        '''
        # depth is from main tree, not relative?
        tree = self.cache.ftree()
        l = len(tree)
        pos = self.cache.tree_locations().get(self.id)
        e = tree[pos]
        base_depth = e.depth
        max_depth = max_depth if max_depth else BIG_DEPTH
        b = [DepthTid(0, e.tid)]
        pos += 1        
        while (pos < l):
            e = tree[pos]
            reldepth = e.depth - base_depth
            if (reldepth < 1):
                # i.e. if not a descendant of the given tid
                break
            if (reldepth < max_depth):
                b.append(DepthTid(reldepth, e.tid)) 
            pos += 1        
        return b      


    def tree(self, max_depth=None):
        '''
        Tree
        return
            [(depth, Term)]
        '''
        term_map = self.cache.term_map()
        tree = self.depth_id_tree(max_depth)
        return [DepthTerm(e.depth, term_map[e.tid]) for e in tree]
        
    def delete(self):
        '''
        Delete the Term and contents.
        Removes descendant terms and
        attached elements.
        ''' 
        descendant_tids = self.id_descendants()
        # because base Term is not in the descendants
        descendant_tids.append(self.id)
        self.model_termparent.objects.filter(tid__in=descendant_tids).delete()
        self.model_term.objects.filter(id__in=descendant_tids).delete()
        self.cache.clear()

    def reparent_choices(self):
        '''
        choices for a a term parent update
        These are limited comared to creation. Updating only allows 
        attachment to terms that are not descendants, to avoid circular 
        references.
        '''
        print('API reparent_choices')
        #? This feels like a shambles. but the slick thing would be
        # tree ids no descendants?
        descendants = self.id_descendants()
        # add in the seed term_id. Don't want to parent on ourself
        descendants.append(self.id)
        # get them all. seems easier right now if sloooooow.
        non_descendant_id_tree = (e for e in self.cache.ftree() if (not(e.tid in descendants)))
        term_map = self.cache.term_map()
        return list(ChoiceIterator([DepthTerm(e.depth, term_map[e.tid]) for e in non_descendant_id_tree]))

        
        
        
class TaxonomyAPI:
    '''
    API for taxonomy models.
    '''
    def __init__(self, 
        model_term, 
        model_termparent, 
    ):
        self.model_term = model_term 
        self.model_termparent = model_termparent 
    
        # cache
        self._parents = {}
        self._children = {}
        self._terms = {}
        self._ftree = None
        self._tree_locations = None

    def generate_base_data(self):
        from django.db import connection
        terms = {}
        parents = {}
        children = {}
        PID_Weighted_SQL = "SELECT t.*, tp.pid FROM {} tp INNER JOIN {} t ON tp.tid = t.id ORDER BY t.weight".format(
            self.model_termparent._meta.db_table,
            self.model_term._meta.db_table,
            )
        with connection.cursor() as cursor:
            cursor.execute(PID_Weighted_SQL)
            for r in cursor.fetchall():
                tid = r[0]
                terms[tid] = self.model_term(*r[:-1])
                parents[tid] = r[-1]
                # Only set up children for later population.
                # Setup here ensures every tid is accounted for.
                children[tid] = []
        # and ensure NO_PARENTS entry
        children[NO_PARENT] = []
        for (tid, pid) in parents.items():
            children[pid].append(tid)
        self._terms = terms
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

    def term_map(self):
        if (not self._children):
            self.generate_base_data()
        return self._terms
    
    def _generate_tree(self):
        '''
        return
            [DepthTid] Tree depths are from 0...
        '''
        child_map = self.child_map() 
        stack = [iter(child_map[NO_PARENT])]
        depth = 0
        while (stack):
            depth = len(stack) - 1
            it = stack.pop()
            while(True):
                try:
                    tid = it.__next__()
                except StopIteration:
                    # exhausted. Pop a iter at a previous depth
                    break
                yield DepthTid(depth, tid)
                child_ids = child_map[tid]
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
              [DepthTid, ...], ordered
        '''
        if (self._ftree is None):
            # list, because we need to run the generator, or it will
            # exhaust on multiple calls
            self._ftree = list(self._generate_tree())
        return self._ftree
    
    # index
    IdxDepth = namedtuple('IdxDepth', ['idx', 'depth'])

    def tree_locations(self):
        if (self._tree_locations is None):
            self._tree_locations = {e.tid : idx for idx, e in enumerate(self.ftree())}
        return self._tree_locations
                 
    def clear(self):
        '''
        Empty cache for a given taxonomy
        '''
        self._parents = {}
        self._children = {}
        self._terms = {}
        self._ftree = None
        self._tree_locations = None
        
    def __call__(self, term_id):
        return TermMethods( 
            self.model_term, 
            self.model_termparent, 
            self, 
            term_id
        )

    def save(self, new_parent_id, obj):
        '''
        Save a term.
        Add necessary parentage on new term. Term parent is not checked 
        against taxonomy_id.
        '''
        self.model_term.save(obj)
        try:
            o = self.model_termparent.objects.get(tid=obj.id)
            o.pid = new_parent_id
        except ObjectDoesNotExist:
            o = self.model_termparent(pid=new_parent_id, tid=obj.id)
        self.model_termparent.save(o)
        self.clear()

    def delete(self):
        '''
        Delete the tree.
        Includes terms, and parentage.
        '''
        self.model_termparent.objects.all().delete()
        self.model_term.objects.all().delete()
        self.clear(self.id)

    def depth_id_tree(self, max_depth=None):
        if (max_depth is None):
            return list.copy(self.ftree())
        else:
            return [e for e in self.ftree() if e.depth < max_depth]

    def tree(self, max_depth=None):
        '''
        Tree
        return
            [(depth, Term)]
        '''
        term_map = self.term_map()
        return [DepthTerm(e.depth, term_map[e.tid]) for e in self.depth_id_tree(max_depth)]
                
    def initial_choices(self):
        '''
        Choices for parenting a term on creation
        '''
        print('initial choices')
        return list(ChoiceIterator((e for e in self.tree())))
