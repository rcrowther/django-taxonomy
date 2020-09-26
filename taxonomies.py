#from .models import Tree, Term, TermParent, BaseTerm, Element
import sys
from collections import namedtuple


# storage tuple
TermFTData = namedtuple('TermFT', ['pk', 'title', 'slug', 'description', 'depth'])

class Taxonomy():
    
    def child_tids(self, tid):
        pass

    def parent_tids(self, tid):
        pass

    def element_count(self, tid):
        pass


    def _term_delete(term_id):
        '''
        Delette one term.
        This works across the database, but can leave inconsistencies
        such as orphaned children. 
        '''
        pass
        # # elems
        # TermElement.objects.filter(tid=term_id).delete()
        # # hierarchy
        # TermParent.objects.filter(tid=term_id).delete()
        # # term
        # Term.objects.filter(id=term_id).delete()

#        children = TermParent.objects.children(tid)
#            parent_count = TermParent.objects.filter(tid=cid).count()    
# Needs a parents and children functions
    def term_delete(term_ids):
        '''
        term_ids
            A list of term ids
        '''
        stash=list(term_ids)
        while stash:
            tid = stash.pop()
            children = self.child_tids(tid)
        
            for cid in children:
                parent_count = self.parent_tids(cid).count()
                # i.e the child has only one parent, this term, so stash
                # for removal, and further child testing.
                if ( parent_count < 2 ):
                    stash.append(cid)
            
            self._term_delete(tid)
        # Alternatively, stash the tids then make this a bulk delete?
        
    def flat_tree(self, tid=TermParent.NO_PARENT, max_depth=FULL_DEPTH):
        '''
        Return term pk data as a flat tree.
        '''
        stack = self.child_tids(tid)
        depth = 0
        while (stack):
            depth = len(stack)
            it = stack.pop()
            while(True):
                try:
                    pk = next(it)
                except StopIteration:
                    # exhausted. Pop a iter at a previous depth
                    break
                yield (depth, pk)
                child_pks = self.child_tids(pk)
                if (child_pks and (depth < _max_depth)):
                    # append current iter, will return after processing children
                    stack.append(it)
                    # append new depth of iter
                    stack.append(iter(child_pks))
                    break
        return tree

    def term_ancestor_paths(self, tid):
        '''
        Return tree-ascending paths of data from Terms.
        If the hierarchy is multiple, the return may contain several 
        paths/trails. If the hierarcy is single, the function will only
        return one path. Each trail starts at the given term_pk and ends at
        a root. If the paths are used for display purposes, you may wish to
        reverse() them. 
        
        @param base_pk int or coercable string
        @param term_pk start from the parents of this term. int or coercable string.
        @return list of lists (paths) of terms. Empty list if term_pk has no parents. 
        '''
        trail = []
        stash = [[p] for p in self.parent_tids(tid)]
        #print('trail_stash') 
        #print(str(trail_stash)) 
        while(stash):
            trail = stash.pop()
            head = trail[-1]
            parents  = self.parent_tids(head)
            if (not parents):
                b.append(trail)
            else:
                for p in parents:
                      #print('fork') 
                      #print(str(p)) 
                    stash.append(list.copy(trail).append(p))                   
          return b
          
    def term_descendant_paths(self, tid):
        trail = []
        stash = [[p] for p in self.child_tids(tid)]
        while(stash):
            trail = stash.pop()
            head = trail[-1]
            children  = self.child_tids(head)
            if (not children):
                b.append(trail)
            else:
                for c in children:
                      #print('fork') 
                      #print(str(p)) 
                    stash.append(list.copy(trail).append(c))                   
          return b
          
          
    def descendant_set(self, tid):
        pass
        
    def descendant_element_count(self, tid):
        count = self.element_count(tid)
        for tpk in self.descendant_set(tid):
            count += self.element_count(tpk)
        return count

