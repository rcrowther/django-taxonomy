from taxonomy.models import Taxonomy, TermParent, TermElement, Term
from collections import namedtuple

# Tree(2).tree()
# Tree(2).data_tree()
# Tree(2).term()
# Tree(2).term(9).tree()
# Tree(2).term(9).data_tree()
# Tree(2).term(9).create()
# Tree(2).term(9).update()
# Tree(2).term(9).delete()

DepthTid = namedtuple('DepthTid', ['depth', 'tid'])


###### cache
# Cache stashes sets of data
# - (tid, parent_id)
# - (tid, child_ids)
# - (tid, term_data)
# - a tree of (depth, tid)
# - an index into the tree (tid, pos)
# It clears with a filter of taxonomy.
    
_parents = {}
_children = {}
_terms = {}
_trees = {}
_tree_locations = {}
         
def generate_base_data(taxonomy_id):
    terms = {term.id : term for term in Term.objects.filter(taxonomy_id=taxonomy_id)}
    tids = terms.keys()
    parents = {tp.tid : tp.pid for tp in TermParent.objects.filter(tid__in=tids)}
    # An inversion of parents removes leaves (no children). Want to 
    # account for all tids, so prebuild from Terms instead
    children = {tid : [] for tid in terms.keys()} 
    # and ensure NO_PARENTS entry
    children[-1] = []
    for (tid, pid) in parents.items():
        children[pid].append(tid)
    _terms[taxonomy_id] = terms
    _parents[taxonomy_id] = parents
    _children[taxonomy_id] = children

def children(taxonomy_id):
    if (not taxonomy_id in _children):
        generate_base_data(taxonomy_id)
    return _children[taxonomy_id] 

def parents(taxonomy_id):
    if (not taxonomy_id in _parents):
        generate_base_data(taxonomy_id)
    return _parents[taxonomy_id] 

def terms(taxonomy_id):
    if (not taxonomy_id in _parents):
        generate_base_data(taxonomy_id)
    return _terms[taxonomy_id]
        
def generate_tree(taxonomy_id):
    child_map = children(taxonomy_id) 
    stack = [iter(child_map[TermParent.NO_PARENT])]
    depth = 0
    while (stack):
        depth = len(stack)
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

def full_tree(taxonomy_id):
    if (not taxonomy_id in _trees):
        # list, because we need to run the generator, or it will
        # exhaust on multiple calls
        _trees[taxonomy_id] = list(generate_tree(taxonomy_id))
    return _trees[taxonomy_id]
    
# index
IdxDepth = namedtuple('IdxDepth', ['idx', 'depth'])

def tree_locations(taxonomy_id):
    if (not taxonomy_id in _tree_locations):
        _tree_locations[taxonomy_id] = {e.tid : idx for idx, e in enumerate(full_tree(taxonomy_id))}
    return _tree_locations[taxonomy_id]
    
     
def cache_clear(taxonomy_id):
    '''
    Empty cache for a given taxonomy
    '''
    # clear base data
    _parents.pop(taxonomy_id, None)
    _children.pop(taxonomy_id, None)
    _terms.pop(taxonomy_id, None)
    # clear location
    _tree_locations.pop(taxonomy_id, None)
    # clear tree
    _trees.pop(taxonomy_id, None)

######

########
# APIs #
########
# The APIs contain the cross-table logic. Unless you have a broken 
# installation, use them.

class ChoiceIterator:
    def __init__(self, taxonomy_id, depthTerms):
        self.taxonomy_id = taxonomy_id
        self.depthTerms = depthTerms

    def __iter__(self):
        yield (TermParent.NO_PARENT, 'None (root term)')
        #queryset = self.queryset
        # Can't use iterator() when queryset uses prefetch_related()
        #if not queryset._prefetch_related_lookups:
        #    queryset = queryset.iterator()
        prev_depth = 99999999
        for e in self.depthTerms:
            print('ChoiceIterator')
            print(str(e.depth))
            # basic
            #title = ' ' * e.depth + terms(self.taxonomy_id)[e.tid].title
            
            b = []
            # ├─ │ └─
            if (e.depth == 0):
                title = terms(self.taxonomy_id)[e.tid].title
            elif (prev_depth <= e.depth):
                title = '\u00A0   ' * (e.depth - 1) + ' └- ' + terms(self.taxonomy_id)[e.tid].title
            else:
                title = '\u00A0   ' * (e.depth - 1) + '    ' + terms(self.taxonomy_id)[e.tid].title
            prev_depth = e.depth
            yield (e.tid, title)
            
class TermAPI():
    def __init__(self, taxonomy_id, term_id):
        self.taxonomy_id = taxonomy_id
        self.id = term_id
        
    def tree(self, max_depth):
        pos = tree_locations(self.taxonomy_id).get(self.id)
        tree = full_tree(self.taxonomy_id)
        e = tree[pos]
        base_depth = e.depth
        b = [e]
        pos += 1        
        e = tree[pos]
        while (base_depth < e.depth):
            if (e.depth - base_depth < max_depth):
                b.append(e) 
            pos += 1        
            e = tree[pos] 
        return b      

    def descendants(self):
        '''
        Term descendants
        return
            [id, ....]
        '''
        child_map = children(self.taxonomy_id)
        stack = list.copy(child_map[self.id])
        b = []
        while (stack):
            tid = stack.pop()
            b.append(tid)
            stack.extend(list.copy(child_map[tid]))
        return b
        
    def descendant_tree(self):
        '''
        Tree descendants
        return
            [DepthTid, ....], ordered
        '''
        pos = tree_locations(self.taxonomy_id).get(self.id)
        tree = full_tree(self.taxonomy_id)
        e = tree[pos]
        base_depth = e.depth
        b = []
        pos += 1        
        e = tree[pos]
        while (base_depth < e.depth):
            # need to trim depth
            e.depth = e.depth - base_depth
            b.append(e) 
            pos += 1        
            e = tree[pos]
        return b

    def ascendent_tree(self):
        '''
        Tree ascscendants
        return
            [DepthTid, ....], ordered
        '''
        pos = tree_locations(self.taxonomy_id).get(self.id)
        tree = full_tree(self.taxonomy_id)
        e = tree[pos]
        base_depth = e.depth - 1      
        b = [e]       
        while (base_depth > -1):
            pos -= 1  
            e = tree[pos]
            if (base_depth >= e.depth):
                b.append(e)
                base_depth -= 1
        return b
                
    def descendant_paths(self):
        '''
        Tree descendant paths
        Each path is a full route from the Term to a leaf,
        return
            [[DepthTid, ...], ...], ordered
        '''
        pos = tree_locations(self.taxonomy_id).get(self.id)
        tree = full_tree(self.taxonomy_id)
        e = tree[pos]
        base_depth = e.depth
        prev_depth = base_depth
        stack = []
        b = []
        pos += 1        
        e = tree[pos]
        current_depth = e.depth
        while (base_depth < current_depth):
            if (current_depth <= prev_depth):
                stack.append(list.copy(b))
                b = b[:current_depth]
            b.append(e)
            pos += 1        
            e = tree[pos]
            prev_depth = current_depth
            current_depth = e,depth
        return b
        
    # an alternative
    def term_descendant_paths(base_pk, term_pk):
        '''
        Return tree-descending paths of data from Terms.
        If the hierarchy is multiple, the return may contain several 
        paths/trails. If the hierarcy is single, the function will only
        return one path. Each trail starts at the given term_pk and ends at
        a root. If the paths are used for display purposes, you may wish to
        reverse() them. 
        
        @param base_pk int or coercable string
        @param term_pk start from the parents of this term. int or coercable string.
        @return list of lists (paths) of terms. Empty list if term_pk has no parents. 
        '''
        children = children(self.taxonomy_id)
        if (children is None):
            return []
        else:
            b = []
            trail = []
            trail_stash = [[c] for c in children[self.id]]
            while(trail_stash):
                trail = trail_stash.pop()  
                head = trail[-1]
                # make current trail
                while(True):
                    children = children[head]
                    if (children is None):
                        # completed a trail
                        # build data for the pks
                        b.append(trail)
                        break
                    # children[1:]; stash a copy of the list with new head
                    for c in children[1:]:
                        trail_stash.append(list.copy(trail).append(c))
                    # child[0] we pursue
                    head = children[0]
                    trail.append(head)
            return b  

    def parent_create(self, new_parent_id):
        '''
        Add necessary parentage on new term
        For maintenence, will not change the term itself.
        '''
        cache_clear(self.taxonomy_id)
        TermParent.objects.create(pid=new_parent_id, tid=self.id)

    def parent(self):
        return parents(self.taxonomy_id)[self.id]
        
    def parent_update(self, new_parent_id):
        '''
        Update parentage on term parent change
        For maintenence, will not change the term itself.
        '''
        cache_clear(self.taxonomy_id)
        o = TermParent.objects.get(tid=self.id)
        o.pid = new_parent_id
        TermParent.save(o)

    def clear(self):
        '''
        Delete all content from the Term.
        Not including the Term. Removes descendant terms and
        attached elements.
        '''
        cache_clear(self.taxonomy_id)
        descendant_tids = (e.tid for e in self.descendant_tree())
        Term.objects.filter(tid__in=descendant_tids).delete()
        TermParent.objects.filter(tid__in=descendant_tids).delete()
        TermElement.objects.filter(tid__in=descendant_tids).delete()
 
    def reparent_choices(self):
        '''
        choices for a a term parent update
        These are limited comared to creation. Updating only allows 
        attachment to terms that are not descendants, to avoid circular 
        references.
        '''
        print('reparent_choices')
        #descendants = self.model.parent_model???.objects.descendants(self.id)
        descendants = self.descendants()
        # add in the seed term_id. Don't want to parent on ourself
        descendants.append(self.id)
        
        # get them all. seems easier right now if sloooooow.
        return ChoiceIterator(self.taxonomy_id, (e for e in full_tree(self.taxonomy_id) if (not(e.tid in descendants))))
                                    
    #! def element_create(self, eid, tid):
    # check unique
        # TermElement.objects.create(eid=eid, tid=tid)
        
    def element_clear(self):  
        return TermElement.objects.filter(tid=self.id).delete()
                        
    def element_count(self):  
        return TermElement.object.filter(tid=self.id).count()                 
                               
                               
                               
class TaxonomyAPI():
    '''
    API for taxonomy models.
    '''
    def __init__(self, taxonomy_id):
        #self.obj = Taxonomy.objects.filter(id=taxonomy_id)
        self.id = taxonomy_id
        
    #def term_create(**kwargs):
   #     Taxonomy.objects.create(*(kwargs)
        
        
    def tree(self, max_depth):
        '''
        The tree for this taxonomy
        return
              [[DepthTid, ...], ...], ordered
        '''
        return [e for e in full_tree(self.id) if e.depth < max_depth]

    def term(self, term_id):
        return TermAPI(self.id, term_id)

    def to_unique(self):
        tree_tids = Terms.filter(taxonomy_id=self.id).values_list('tid', flat=True)
        TermElement.to_unique(tree_tids)
        
    def clear(self):
        '''
        Delete all content from the tree.
        Not including the Taxonomy object. Includes terms and attached 
        elements.
        '''
        cache_clear(self.id)
        tree_tids = Terms.filter(taxonomy_id=self.id).values_list('tid', flat=True)
        Term.objects.filter(tid__in=tree_tids).delete()
        TermParent.objects.filter(tid__in=tree_tids).delete()
        TermElement.objects.filter(tid__in=tree_tids).delete()

    def initial_choices(self):
        '''
        Choices for parenting a term on creation
        '''
        print('initial choices')
        #? A term can be attached to
        # - NO_PARENT 
        # but cannot be attached to
        # - itself (if 'change' not 'add')
        # - descendants (makes circular linkage)
        #return ChoiceIterator(self.model.objects.filter(taxonomy_id=taxonomy_id).values_list('id', 'title'))
        #return ChoiceIterator(self.model.objects.filter(taxonomy_id=taxonomy_id).values_list('id', 'title'))
        return ChoiceIterator(self.id, (e for e in full_tree(self.id)))
