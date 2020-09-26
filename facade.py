from .models import Base, Term, BaseTerm, TermParent, Element
from taxonomy import cache
 
## Facade for cache and Model/Model manager methods for consistent 
# interface
# Django doesn't usually do traits/APIs/Facades etc., but here it is.

# constants
#ROOT = TermParent.NO_PARENT
#FULL_DEPTH = cache.FULL_DEPTH
#UNPARENT = TermParent.UNPARENT
# Cache-based

#def base(base_pk):
    #return cache.base(base_pk)
    
#def term(term_pk):
    #return cache.term(term_pk)

#def term_parents(base_pk, term_pk):
    #return cache.term_parents(base_pk, term_pk)

#def term_parent_pks(base_pk, term_pk):
    #return cache.term_parent_pks(base_pk, term_pk)

#def term_children(base_pk, term_pk):
    #return cache.term_children(base_pk, term_pk)

#def term_child_pks(base_pk, term_pk):
    #return cache.term_child_pks(base_pk, term_pk)
    
#def term_ancestor_paths(base_pk, term_pk):
    #return cache.term_ancestor_paths(base_pk, term_pk)
      
#def term_descendant_paths(base_pk, term_pk):
    #return cache.term_descendant_paths(base_pk, term_pk)

#def term_ancestor_pks(base_pk, term_pk):
    #return cache.term_ancestor_pks(base_pk, term_pk)

#def term_descendant_pks(base_pk, term_pk):
    #return cache.term_descendant_pks(base_pk, term_pk)
    
#def base_term_pks(base_pk):
    #return cache.base_term_pks(base_pk)

#def terms_flat_tree(base_pk, parent_pk=ROOT, max_depth=FULL_DEPTH):
    #return cache.terms_flat_tree(base_pk, parent_pk, max_depth)


## Model-based
#def base_create(title, slug, description, is_single, weight):
    #return Base.system.create(title, slug, description, is_single, weight)
    
#def base_update(base_pk, title, slug, description, is_single, weight):
    #cache.base_clear(base_pk)
    #return Base.system.update(base_pk, title, slug, description, is_single, weight)

#def base_delete(base_pk):
    #cache.base_and_tree_clear(base_pk)
    #return Base.system.delete(base_pk)


#def base_terms_ordered(base_pk):
    #return BaseTerm.system.terms_ordered(base_pk)
    
#def base_set_is_single(base_pk, is_single):
    #cache.base_and_tree_clear(base_pk)
    #Base.system.set_is_single(base_pk, is_single)

#def term_create(base_pk, parent_pks, title, slug, description, weight):
    #cache.tree_parentage_clear(base_pk)
    #return Term.system.create(base_pk, parent_pks, title, slug, description, weight)

#def term_update(parent_pks, term_pk, title, slug, description, weight):
    #cache.term_and_tree_clear(term_pk)
    #return Term.system.update(parent_pks, term_pk, title, slug, description, weight)
      
#def term_delete(term_pk):
    #cache.tree_clear(term_pk)
    #return Term.system.delete(term_pk)

#def term_by_title(title):
#    return Term.objects.get(title__exact=title)

#? and a base?
#def term_base_pk(term_pk):
    #return BaseTerm.system.base_pk(term_pk)
    
#def term_title_search(base_pk, pattern):
#    return Term.system.title_search(base_pk, pattern)
    
#def element_add(term_pk, element_pk):
    #cache.element_clear_term(term_pk)
    #return Element.system.add(term_pk, element_pk)
         
#def element_delete(term_pk, element_pk):
    #cache.element_clear_term(term_pk)
    #return Element.system.delete(term_pk, element_pk)

#def element_bulk_merge(term_pks, element_pk):
    #cache.element_clear_all()
    #return Element.system.bulk_merge(term_pks, element_pk)
            
#def element_base_delete(base_pk, element_pks):
    #cache.element_clear_all()
    #return Element.system.delete(base_pk, element_pks)
    
#def element_terms(base_pk, element_pk): 
#    return Element.system.terms(base_pk, element_pk)

#def term_elements(term_pk, model): 
#    pks = Element.objects.filter(term=term_pk)
#    return model.objects.filter(pk__in=pks)

# Theres a difference between a DB API and a collection API?
class TreeAPI():
    '''
    Tree as a collection of terms.
    '''
    def __init__(self, tree_pk):
        '''
        Create a tree
        '''
        self.pk = int(tree_pk)
        
    def tree(self):
        '''The full model of data '''
        pass

        
    def subtract(self, term_pk):
        pass
        
    def __isub__(self, term):
        self.subtract(term)

    def subtractAll(self, term_pks):
        # inefficient. Should usually override.
        for pk in term_pks:
            self.subtract(pk)
            
    #? use an obj
    #def update(self, title, slug, description, is_single, weight):
    #    pass

    # def _set_is_single(self, is_single):
        # pass

    # def _get_is_single(self):
         # pass
                 
    # is_single = property(_get_is_single, _set_is_single)

    # def _get_is_unique(self):
         # pass

    # def _set_is_unique(self, is_single):
        # pass
        
    # is_unique = property(_get_is_unique, _set_is_unique)

    # def _get_weight(self):
         # pass

    # def _set_weight(self, is_single):
        # pass
        
    # weight = property(_get_weight, _set_weight)
    
    # def delete(self):
        # pass

        
    def term_pks(self):
        '''Set of all (non-duplicated) term pks'''
        pass

    def terms_ordered(self):
        ''' list of tuples of all term data, ordered'''
        pass

        
    def children(self):
        '''
        Children of the tree (the base, not all children?).
        '''
        pass
        
    # def flat_tree(self, parent_pk=ROOT, max_depth=FULL_DEPTH):
        # pass

    # def flat_tree_pks(self, parent_pk=ROOT, max_depth=FULL_DEPTH):
        # return cache.flat_tree_pks(self.pk, parent_pk, max_depth)
        
    
    # def stacked_tree(self, parent_pk=TermParent.NO_PARENT, max_depth=FULL_DEPTH):
        # return cache.stacked_tree_iter(self.pk, parent_pk, max_depth)
        
    # def element_terms(self, element_pk): 
        # return Element.system.terms(self.pk, int(element_pk))
                    
    def element_subtract(self, elem_pk):
        pass

    def terms_collect(self, element_pk):
        pass
        
    def clear(self):
        '''
        Remove all contents
        '''
        pass
        
        
class TermAPI():
    '''
    Term as collection and element in a tree
    '''
    def __init__(self, term_pk):
        '''
        term_pk
            id of a term
        '''
        pass

    def term(self):
        '''The full model of data '''
        return cache._term_cache.get(self.pk)
    
    def tree_pk(self):
        return self._base_pk 

    def __iadd__(self, term):
        self.add(term)   

    def add(self, term):
        '''
        Add new term pareented to this.
        '''
        pass
        
    def addAll(self, terms):
        '''
        Add new terms pareented to this.
        '''
        pass

    def subtract(self, term_pk):
        pass
        
    def __isub__(self, term_pk):
        self.subtract(term_pk)

    def subtractAll(self, term_pks):
        # inefficient. Should usually override.
        for pk in term_pks:
            self.subtract(pk)
                        
    #? use an obj
    # def update(self, parent_pks, title, slug, description, weight):
        # cache.term_and_tree_clear(self.pk)
        # return Term.system.update(parent_pks, self.pk, title, slug, description, weight)
          
    # def delete(self):
        # cache.tree_clear(self.pk)
        # return Term.system.delete(self.pk)
        

    #def base(self):
    #    return base(self._base_pk)
            
    def parents(self):
        '''Full models of data '''
        pass
    
    def parent_pks(self):
        pass
        
    #! dont throw errors on leaves
    def children(self):
        '''Children as full models of data. '''
        pass
        
    #! don't throw errors on leaves
    def child_pks(self):
        pass
        
    def ancestor_paths(self):
        '''Select full models of term ancestors.
        return
            A list of lists of models, each list representing an 
            ancestor path. If the term is in a single parent tree, the 
            list will contain one path only
        '''
        pass
          
    def ancestor_pks(self):
        '''Select pks of term ancestors.
        return
            A list of lists of pks, each list representing an 
            ancestor path. If the term is in a single parent tree, the 
            list will contain one path only
        '''
        pass
        
    def descendant_paths(self):
        '''Select full models of term descendants.
        return 
            A list of lists of models, each list representing a 
            possible descendant path
        '''
        pass
    
    def descendant_pks(self):
        '''Select pks of term descendants.
        return
            A list of lists of pks, each list representing a 
            possible descendant path
        '''
        pass
        
    def elements(self, model): 
        '''
        Elements attached to this term.
        '''
        pass
        
    def element_add(self, elem__pk):
        pass
             
    def element_subtract(self, elem_pk):
        pass

# class ElementAPI():
    # def __init__(self, term_pk):

    # def terms(self, base_pk): 
        # return Element.system.terms(int(base_pk), self.pk)
     
    # def add(self, term_pk):
        # cache.element_clear_term(term_pk)
        # return Element.system.add(term_pk, self.pk)
             
    # def delete(self, term_pk):
        # cache.element_clear_term(term_pk)
        # return Element.system.delete(term_pk, self.pk)
    
    # def merge(self, term_pks):
        # #! test for int?
        # cache.element_clear_all()
        # return Element.system.bulk_merge(term_pks, self.pk)
                
    # def tree_delete(self, base_pk):
        # cache.element_clear_all()
        # return Element.system.base_delete(int(base_pk), self.pk)
       
      
# def _base_ordered():
    # return Base.system.ordered()

# def _base_create(title, slug, description, is_single, weight):
    # return Base.system.create(title, slug, description, is_single, weight)

# def _cache_clear():
    # return cache.clear()
    
# def Taxonomy(title):
    # '''
    # Factory for BaseAPI.
    # Usage:
    # Taxonomy(title)
    # Taxonomy.pk(base_pk)
    # Taxonomy.slug(slug)
    # Taxonomy.term(term_pk)
    # Taxonomy.base(base_pk)
    # also:
    # Taxonomy.base_ordered() returns a QuerySet of bases
    # Taxonomy.base_create() 
    # Taxonomy.cache_clear() 
    # @throws Base.DoesNotExist
    # @return an BaseAPI object
    # '''
    # # taxonomy.models.DoesNotExist:
    # return BaseAPI(Base.objects.get(title=title).pk)
    
# Taxonomy.pk = lambda base_pk : BaseAPI(base_pk)
# Taxonomy.slug = lambda slug : BaseAPI(Base.objects.get(slug=slug).pk)
# Taxonomy.term = lambda term_pk : cache._term_cache.get(term_pk)
# Taxonomy.base = lambda base_pk : cache._base_cache.get(base_pk)
# Taxonomy.ordered = _base_ordered
# Taxonomy.base_create = _base_create
# Taxonomy.cache_clear = _cache_clear

