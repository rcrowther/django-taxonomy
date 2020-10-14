from collections import namedtuple
from django.db import transaction

#from .models import Base, Term, BaseTerm, TermParent, Element
 

# constants
# ROOT = TermParent.NO_PARENT
# FULL_DEPTH = cache.FULL_DEPTH
# UNPARENT = TermParent.UNPARENT
NO_PARENT = -1

DepthTid = namedtuple('DepthTid', ['depth', 'tid'])

DepthTerm = namedtuple('DepthTerm', ['depth', 'term'])

class ChoiceIterator:
    def __init__(self, taxonomy_id, depthTerms):
        #??? self.taxonomy_id = taxonomy_id
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
        model_element,
        cache, 
        taxonomy_id,
        term_id
    ):
        #self.model_taxonomy = model_taxonomy
        self.model_term = model_term 
        self.model_termparent = model_termparent 
        self.model_element = model_element 
        self.cache = cache
        self.taxonomy_id = taxonomy_id
        self.id = term_id

    def depth(self):
        pos = self.cache.tree_locations(self.taxonomy_id).get(self.id)
        tree = self.cache.tree(self.taxonomy_id)
        return tree[pos].depth

    def id_parent(self):
        pid = self.cache.parent_map(self.taxonomy_id)[self.id]
        if (pid == NO_PARENT):
            return None
        else:
            return pid

    def id_children(self):
        # catch NO_PARENT
        tid = self.id if (self.id > 0) else NO_PARENT
        return self.cache.child_map(self.taxonomy_id)[tid]
                                
    def parent(self):
        '''
        return
            Term. If NO_PARENT, None
        '''
        pid = self.cache.parent_map(self.taxonomy_id)[self.id]
        if (pid == NO_PARENT):
            return None
        else:
            return self.cache.term_map(self.taxonomy_id)[pid]

    def children(self):
        '''
        return
            [Term, ...]
        '''
        # catch NO_PARENT
        tid = self.id if (self.id != 0) else NO_PARENT
        term_map = self.cache.term_map(self.taxonomy_id)
        return [term_map[e] for e in self.cache.child_map(self.taxonomy_id)[tid]]

        
    def id_ascendants(self):
        '''
        Term ascendants
        The return is ordered as a single path.
        Includes the original id.
        return
            [id, ....]
        '''
        parent_map = self.cache.parent_map(self.taxonomy_id)
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
        child_map = self.cache.child_map(self.taxonomy_id)
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
            [DepthTid, ....], ordered
        '''
        pos = self.cache.tree_locations(self.taxonomy_id).get(self.id)
        tree = self.cache.tree(self.taxonomy_id)
        e = tree[pos]
        b = [e]       
        base_depth = e.depth - 1      
        while (base_depth > 0):
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
        tree = self.cache.tree(self.taxonomy_id)
        l = len(tree)
        pos = self.cache.tree_locations(self.taxonomy_id).get(self.id)
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
        term_map = self.cache.term_map(self.taxonomy_id)
        path = self.depth_id_ascendent_path()
        return [ term_map[e.tid] for e in path ]
    
    def descentant_paths(self):
        term_map = self.cache.term_map(self.taxonomy_id)
        paths = self.depth_id_descendant_paths()
        return [ [term_map[e.tid] for e in path] for path in paths]

    def depth_id_tree(self, max_depth=None):
        tree = self.cache.tree(self.taxonomy_id)
        l = len(tree)
        pos = self.cache.tree_locations(self.taxonomy_id).get(self.id)
        e = tree[pos]
        base_depth = e.depth
        max_depth = max_depth if max_depth else 999999
        rel_max_depth = max_depth + base_depth
        b = [e]
        pos += 1        
        while (pos < l):
            e = tree[pos]
            if (e.depth <= base_depth):
                # i.e. if not a descendant of the given tid
                break
            if (e.depth < rel_max_depth):
                b.append(e) 
            pos += 1        
        return b      


    def tree(self, max_depth=None):
        '''
        Tree
        return
            [(depth, Term)]
        '''
        term_map = self.cache.term_map(self.taxonomy_id)
        tree = self.depth_id_tree(max_depth)
        return [DepthTerm(e.depth, term_map[e.tid]) for e in tree]
        
    def delete(self):
        '''
        Delete the Term and contents.
        Removes descendant terms and
        attached elements.
        '''
        descendant_tids = self.id_descendants()
        # Term is not in the descendants
        descendant_tids.append(self.id)
        with transaction.atomic():
            self.model_element.objects.filter(tid__in=descendant_tids).delete()
            self.model_termparent.objects.filter(tid__in=descendant_tids).delete()
            self.model_term.objects.filter(id__in=descendant_tids).delete()
        self.cache.clear(self.taxonomy_id)

    def parent_update(self, new_parent_id):
        '''
        Update parentage on term parent change
        For maintenence, will not change the term itself.
        '''
        o = self.model_termparent.objects.get(tid=self.id)
        o.pid = new_parent_id
        self.model_termparent.save(o)
        cache_clear(self.taxonomy_id)

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
        #! not generating tree?
        descendants = self.id_descendants()
        # add in the seed term_id. Don't want to parent on ourself
        descendants.append(self.id)
        # get them all. seems easier right now if sloooooow.
        non_descendant_id_tree = (e for e in self.cache.tree(self.taxonomy_id) if (not(e.tid in descendants)))
        term_map = self.cache.term_map(self.taxonomy_id)
        return list(ChoiceIterator(self.taxonomy_id, [DepthTerm(e.depth, term_map[e.tid]) for e in non_descendant_id_tree]))
        #return list(ChoiceIterator(self.taxonomy_id, (e for e in self.api.tree() if (not(e.term.id in descendants)))))
             
             
             
                  
class TaxonomyMethods:
    def __init__(self, 
        model_taxonomy,
        model_term, 
        model_termparent, 
        model_element, 
        cache,
        taxonomy_id
    ):
        self.model_taxonomy = model_taxonomy
        self.model_term = model_term 
        self.model_termparent = model_termparent 
        self.model_element = model_element         
        self.cache = cache    
        self.id = taxonomy_id         


    def term(self, term_id):
        return TermMethods( 
            self.model_term, 
            self.model_termparent, 
            self.model_element,
            self.cache, 
            self.id,
            term_id
        )

    def depth_id_tree(self, max_depth=None):
        '''
        The tree for this taxonomy
        return
              [[DepthTid, ...], ...], ordered
        '''
        max_depth = max_depth if max_depth else 999999
        max_depth += 1
        return [e for e in self.cache.tree(self.id) if e.depth < max_depth]

    def tree(self, max_depth=None):
        '''
        Tree
        return
            [(depth, Term)]
        '''
        term_map = self.cache.term_map(self.id)
        tree = self.depth_id_tree(max_depth)
        return [DepthTerm(e.depth, term_map[e.tid]) for e in tree]
                
    def delete(self):
        '''
        Delete the tree and contents.
        Including the Taxonomy object. Also terms, parentage, and attached 
        elements.
        '''
        with transaction.atomic():
            tree_tids = self.model_terms.filter(taxonomy_id=self.id).values_list('tid', flat=True)
            self.model_element.objects.filter(tid__in=tree_tids).delete()
            self.model_termparent.objects.filter(tid__in=tree_tids).delete()
            self.model_term.objects.filter(tid__in=tree_tids).delete()
            #self.model_taxonomy.objects.filter(id=self.id).delete()
            self.cache.clear(self.id)
        
    def initial_choices(self):
        '''
        Choices for parenting a term on creation
        '''
        print('initial choices')
        return list(ChoiceIterator(self.id, (e for e in self.tree())))
        
        
        
class TaxonomyAPI:
    '''
    API for taxonomy models.
    '''
    def __init__(self, 
        model_taxonomy,
        model_term, 
        model_termparent, 
        model_element, 
    ):
        self.model_taxonomy = model_taxonomy
        self.model_term = model_term 
        self.model_termparent = model_termparent 
        self.model_element = model_element 
    
        # cache
        self._parents = {}
        self._children = {}
        self._terms = {}
        self._trees = {}
        self._tree_locations = {}

    # def contribute_to_class(self, model, name):
        # self.model_taxonomy = model
        # setattr(model, name, self)

    def generate_base_data(self, taxonomy_id):
        from django.db import connection
        terms = {}
        parents = {}
        children = {}
        PID_Weighted_SQL = "SELECT t.*, tp.pid FROM {} tp INNER JOIN {} t ON tp.tid = t.id WHERE t.taxonomy_id = {} ORDER BY t.weight".format(
            self.model_termparent._meta.db_table,
            self.model_term._meta.db_table,
            int(taxonomy_id)
            )
        #print('PID_Weighted_SQL')
        #print(PID_Weighted_SQL)
        with connection.cursor() as cursor:
            cursor.execute(PID_Weighted_SQL)
            for r in cursor.fetchall():
                # 1, 1, 0, 'term 1', 'term_1', 'term 1',
                print(str(r))
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
        self._terms[taxonomy_id] = terms
        self._parents[taxonomy_id] = parents
        self._children[taxonomy_id] = children
        
    # def generate_base_data(self, taxonomy_id):
        # terms = {term.id : term for term in self.model_term.objects.filter(taxonomy_id=taxonomy_id)}
        # tids = terms.keys()
        # parents = {tp.tid : tp.pid for tp in self.model_termparent.objects.filter(tid__in=tids)}
        # # An inversion of parents removes leaves (no children). Want to 
        # # account for all tids, so prebuild from Terms instead
        # children = {tid : [] for tid in terms.keys()} 
        # # and ensure NO_PARENTS entry
        # children[NO_PARENT] = []
        # for (tid, pid) in parents.items():
            # children[pid].append(tid)
        # self._terms[taxonomy_id] = terms
        # self._parents[taxonomy_id] = parents
        # self._children[taxonomy_id] = children

    def child_map(self, taxonomy_id):
        if (not taxonomy_id in self._children):
            self.generate_base_data(taxonomy_id)
        return self._children[taxonomy_id] 

    def parent_map(self, taxonomy_id):
        if (not taxonomy_id in self._parents):
            self.generate_base_data(taxonomy_id)
        return self._parents[taxonomy_id] 

    def term_map(self, taxonomy_id):
        if (not taxonomy_id in self. _terms):
            self.generate_base_data(taxonomy_id)
        return self._terms[taxonomy_id]
    
    def _generate_tree(self, taxonomy_id):
        '''
        return
            [DepthTid]
        '''
        child_map = self.child_map(taxonomy_id) 
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

    def tree(self, taxonomy_id):
        if (not taxonomy_id in self._trees):
            # list, because we need to run the generator, or it will
            # exhaust on multiple calls
            self._trees[taxonomy_id] = list(self._generate_tree(taxonomy_id))
        return self._trees[taxonomy_id]
    
    # index
    IdxDepth = namedtuple('IdxDepth', ['idx', 'depth'])

    def tree_locations(self, taxonomy_id):
        if (not taxonomy_id in self._tree_locations):
            self._tree_locations[taxonomy_id] = {e.tid : idx for idx, e in enumerate(self.tree(taxonomy_id))}
        return self._tree_locations[taxonomy_id]
                 
    def clear(self, taxonomy_id):
        '''
        Empty cache for a given taxonomy
        '''
        # clear base data
        self._parents.pop(taxonomy_id, None)
        self._children.pop(taxonomy_id, None)
        self._terms.pop(taxonomy_id, None)
        # clear location
        self._tree_locations.pop(taxonomy_id, None)
        # clear tree
        self._trees.pop(taxonomy_id, None)
    
    def __call__(self, taxonomy_id):
        return TaxonomyMethods( 
            self.model_taxonomy,
            self.model_term, 
            self.model_termparent, 
            self.model_element, 
            self,
            taxonomy_id
        )

    def taxonomy_save(self, obj):
        self.model_taxonomy.save(obj)

    def term_save(self, new_parent_id, obj):
        '''
        Add a term.
        Add necessary parentage on new term. Term parent is not checked 
        against taxonomy_id.
        '''
        with transaction.atomic():
            self.model_taxonomy.save(obj)
            self.model_termparent.objects.create(pid=new_parent_id, tid=obj.id)
            self.clear(obj.taxonomy_id)


