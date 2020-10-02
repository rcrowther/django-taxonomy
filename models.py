from django.db import models
from django.urls import reverse
from django.db import connection




#class  ElementManager(models.Manager):
#    def element_count(self, term_id):  
#        return self.object.filter(tid=term_id).count()    



class TermElement(models.Model):
    '''
    Attach elements to terms
    '''
    tid = models.IntegerField(
        "term id",
        db_index=True,
        help_text="A category associated with an element.",
    )
      
    eid = models.IntegerField(
        "element id",
        db_index=True,
        help_text="An element associated with a category.",
    )

    def to_unique(self, tree_tids):
        '''
        Turn a non-unique taxonomy into a unique taxonomy.
        This is done by removing duplicate parents. Only the first
        parent is retained.
        After this surgery the tree will be fully parented. But it may 
        display an odd shape.
        
        tree_tids
             Every tid in a tree. This query must be done somewhere else.
        return 
            count of element associations removed
        '''
        # if 'eid' is repeated, it must have multiple entries, so:
        # get every tid in a tree
        # check all eids
        # If there is more than one entry for any eid, it is removed.
        #? This is a inverse set() operation. Maybe even by SQL DISTINCT
        seen = []
        duplicates = []
        xo = self.objects.filter(tid__in=tree_tids)
        for o in xo:
            if o.eid in seen:
                duplicates.append(o.id)
            else:
                seen.append(o.eid)
                  
        # remove entries containing duplicates
        self.objects.filter(id__in=duplicates).delete()
        return len(duplicates)
        
    #objects = ElementManager()
    #objects = ElementManager

    def __repr__(self):
        return  "TermElement(tid:{}, eid:{})".format(
            self.tid,
            self.eid
        ) 
    
    def __str__(self):
        return "TermElement({0}-{1})".format(
            self.tid, 
            self.eid, 
        )



#class  TermParentManager(models.Manager):
    #? might be better if override the queryset, but we don't use on 
    # multiple tids
    # def children(self, tid):
        # '''
        # Ids of child terms
        # return
            # a queryset 'list'
        # '''
        # return self.filter(pid=tid).values_list('tid', flat=True)

    # def parent(self, tid):
        # '''
        # Ids of parent terms
        # return
            # a queryset 'list'
        # '''
        # return self.filter.get(tid=tid).pid 

    # def ancestors(self, term_id):
        # '''
        # Ids of ancestors
        # Collects from parentage. Intended for updates, 
        # slow for access.
        # return
            # [(tid relative_depth)], with the initial term_id
        # '''
        # r = []
        # depth = 0
        # tid = term_id
        # while (tid != TermParent.NO_PARENT):
            # r.append((tid, depth),)
            # depth += 1
            # tid = self.parent(tid)
        # return r
                
    # def descendants(self, term_id):
        # '''
        # Ids of descendants
        # Collects from parentage. Intended for updates, 
        # slow for access.
        # return
            # [(tid relative_depth)], without the initial term_id
        # '''
        # r = []
        # depth = 0
        # children = self.children(term_id)
        # stack = [(term_id, depth) for tid in children]
        # while (stack):
            # d = stack.pop()
            # r.append(d)
            # children = self.children(d[0])
            # stack.extend([(tid, d[1] + 1) for tid in children])
        # return r
                
    # def parent_create(self, term_id, new_parent_id):
        # self.create(pid=new_parent_id, tid=term_id)
        
        # make new ancestory
        # all ancestors have a new descendant
        # ancestor_ids = self.ancestors(new_parent_id)
        # for aid in ancestor_ids:
            # TermAncestory.objects.create(tid=aid, did=term_id)
                    
    # def parent_update(self, term_id, old_parent_id, new_parent_id):
        # #delete old parent link
        # self.filter(tid=term_id).delete()

        # # new 
        # self.create(pid=new_parent_id, tid=term_id)       
        

            
                
class TermParent(models.Model):
    '''
    Parent terms to other terms
    '''
    # Sadly, the autoincrement is dependent on underlying DB 
    # implementation. It would be nice to guarentee zero, but the only
    # way to do this is by an even more awkward method of migration.
    # So -1 sentinel it is, for unparented Terms.
    #- signal to unparent, or as unparented.
    # handy here and there
    UNPARENT = -2
    
    # Sentinel for 'pid' if unparented.
    # Now that would beggar belief, an auto-increment that allows -1...
    NO_PARENT = -1
    
    tid = models.IntegerField(
        "term id",
        db_index=True,
        help_text="Category parented by another category.",
    )
      
    # can be self.NO_PARENT, if at root of tree
    pid = models.IntegerField(
        "parent term id",
        db_index=True,
        blank=True,
        default= NO_PARENT,
        help_text="Category parenting another category.",
    )


    # @classmethod
    # def child_tids(self, term_pk):
        # return cls.objects.filter(pid=term_pk).values_list('tid', flat=True)
        
    # functions needed to run the API. This is not an implementation of
    # the facade, but creates functionality necessary to run it.

        # def subtract(self, term_pk): 


    # @classmethod
    # def parent_tids(self, term_pk):
        # return cls.objects.filter(tid=term_pk).values_list('pid', flat=True)   

    # def parent_update(self, parent_ids, term_id):
        # cls.objects.filter(tid=term_id).delete()
        # #?? do by SQL or ORM
        # _SQLParentUpdate = "INSERT taxonomy_termparent tp"
 
        # cls.save(tid=term_id) 
        
    # def multiple_to_single(self, tree_id):
        # '''
        # Turn a multiparent tree into a single parent tree.
        # This is done by removing duplicate parents. Only the first
        # parent is retained.
        # Though still fully parented, after this operation the tree may 
        # display an odd shape.
        
        # return 
            # count of parent associations removed
        # '''
        # # if 'term' is repeated, it must have multiple parents, so:
        # # get every parent relation in a tree
        # qs = TermParent.objects.all()
              
        
        # # build list of entries reepresenting multiple parents.
        # # No need to look at parent. If there is more than one entry
        # # for any tid, it is removed.
        # #? This is a inverse set() operation. Maybe even by SQL DISTINCT
        # seen = []
        # duplicates = []
        # for e in qs:
            # if e.tid in seen:
                # duplicates.append(e.id)
            # else:
                # seen.append(e.tid)
                  
        # # remove entries containing duplicate term fields
        # TermParent.objects.filter(id__in=duplicates).delete()
        # return len(duplicate_pks)
             
    #def terms_collect(self, element):
    #def clear(self):
    ####

    #objects = TermParentManager()
    
    def __repr__(self):
        return  "TermParent(tid:{0}, pid:{1})".format(
            self.tid,
            self.pid
        ) 
        
    def __str__(self):
        return "TermParent({}-{})".format(
            self.tid, 
            self.pid if self.pid != TermParent.NO_PARENT else 'NO_PARENT', 
        )


#x
class ChoiceIterator:
    def __init__(self, queryset):
        self.queryset = queryset

    def __iter__(self):
        yield (TermParent.NO_PARENT, 'None (root term)')
        #queryset = self.queryset
        # Can't use iterator() when queryset uses prefetch_related()
        #if not queryset._prefetch_related_lookups:
        #    queryset = queryset.iterator()
        for obj in self.queryset:
            yield obj
        
        
#x
class TermManager(models.Manager):
    pass
    # def tree(self, tree_id):
        # '''
        # All the terms in a tree.
        # '''
        # return self.filter(tree_id=tree_id)  
        
    # def taxonomy_ids(self, tree_id):
        # '''
        # All the term ids in a tree.
        # '''
        # return self.filter(tree_id=tree_id).values_list('id', flat=True)
        
    # def initial_choices(self, taxonomy_id):
        # '''
        # Choices for parenting a term on creation
        # '''
        # #? A term can be attached to
        # # - NO_PARENT 
        # # but cannot be attached to
        # # - itself (if 'change' not 'add')
        # # - descendants (makes circular linkage)
        # return ChoiceIterator(self.model.objects.filter(taxonomy_id=taxonomy_id).values_list('id', 'title'))

    # def reparent_choices(self, taxonomy_id, term_id):
        # '''
        # choices for a a term parent update
        # These are limited comared to creation. Updating only allows 
        # attachment to terms that are not descendants, to avoid circular 
        # references
        # '''
        # descendants = self.model.parent_model???.objects.descendants(term_id)
        
        # # add in the seed term_id. Don't want to parent on ourself
        # descendants.append(term_id)
        
        # # get them all. seems easier right now if sloooooow.
        # qs = self.tree_tids(taxonomy_id).values_list('id', 'title')
        # return ChoiceIterator((e for e in qs if (not(e[0] in descendants))))
                    


class Term(models.Model):
    
    taxonomy_id = models.IntegerField(
        "tree id",
        #choices=Taxonomy.tree_choices,
        #default='',
        db_index=True,
        help_text="Id of the tree this category is attached to.",
    )
    
    # Not unique. All terms in same table, different taxonomies.
    title = models.CharField(
        max_length=255,
        blank=True,
        default='',
        db_index=True,
        help_text="Name for the category. Limited to 255 characters.",
    )
      
    # Not unique. Terms may be in different taxonomies. They may
    # be duplicated at different places in a hierarchy e.g. 'sports>news'
    # 'local>news'.
    slug = models.SlugField(
        max_length=64,
        blank=True,
        default='',
        help_text="Short name for use in urls.",
    )
  
    description = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text="Description of the category. Limited to 255 characters.",
    )
      
    weight = models.PositiveSmallIntegerField(
        blank=True,
        default=0,
        db_index=True,
        help_text="Priority for display of several categories Lower value orders first. 0 to 32767.",
    )

    # calculanle, but good to have arround
    # depth = models.IntegerField(
        # "depth",
        # editable= False,
        # help_text="Depth this category is in the tree.",
    # )
    # functions needed to run the API. This is not an implementation of
    # the facade, but creates the functionality necessary to run it.
    # def child_ids(self):
        # return self.parent_model.objects.children(self.id)

    # def parent_ids(self):
        # return self.parent_model.objects.parents(self.id)
        
    # @classmethod
    # def terms(cls, tree_id):
        # '''
        # All the terms in a tree.
        # '''
        # return cls.objects.filter(tree_id=tree_id)  

    # @classmethod
    # def term_ids(cls, tree_id):
        # '''
        # All the term ids in a tree.
        # '''
        # return cls.objects.filter(tree_id=tree_id).values_list('id', flat=True)        
        
    # @classmethod
    # def term_choices(cls, tree_id):
        # #? A term can be attached to
        # # - NO_PARENT 
        # # but cannot be attached to
        # # - itself (if 'change' not 'add')
        # # - descendants (makes circular linkage)
        # return ChoiceIterator(cls.objects.filter(tree_id=tree_id).values_list('id', 'title'))

    # @classmethod
    # def term_choices_update(cls, tree_id, term_id):
        # descendants = cls.parent_model.objects.descendants(term_id)
        
        # # add in the seed term_id. Don't want to parent on ourself
        # descendants.append(term_id)
        
        # # get them all. seems easier right now if sloooooow.
        # qs = cls.objects.filter(tree_id=tree_id).values_list('id', 'title')
        # return ChoiceIterator((e for e in qs if (not(e[0] in descendants))))
                    
    #    def subtract(self, term_pk):
    #def children(self):
    #def terms_collect(self, element):
    
    #def clear(self):
    ####
        
    #def get_absolute_url(self):
    #    return reverse("term-detail", kwargs={"slug": self.slug})
    objects = TermManager()
    #tree_objects = TaxonomyManager(parent_model)

    def __repr__(self):
        return "Term(taxonomy_id:{}, title:{}, slug:{}, weight:{})".format(
            self.taxonomy_id,
            self.title,
            self.slug,
            self.weight,
        )  
          
    def __str__(self):
        return "{}".format(
            self.title if self.title else self.pk, 
        )


## Useful cross-model queries
# put somewhere more structured?


# _SQLTaxonomyTermsAndParents = "SELECT tp.*, tp.pid FROM taxonomy_term t INNER JOIN taxonomy_termparent tp ON t.id = tp.tid WHERE t.tree_id = %s ORDER BY t.weight, t.title"

# def tree_terms_and_parent_ids(tree_id):
    # '''
    # All terms for a tree.
    # return
        # (term, term_parent_id)
    # '''
    # with connection.cursor() as c:
        # c.execute(_SQLTaxonomyTermsAndParents, [tree_id])
        # for e in c.fetchall():
            # yield (e[0], e[0:5],  e[5:]) 
              
# _SQLTIDParentTerms = "SELECT t.* FROM taxonomy_term t INNER JOIN taxonomy_termparent tp ON t.id = tp.pid WHERE tp.tid = %s ORDER BY t.weight, t.title"

# def parent_terms(term_id):
    # '''
    # Parent terms for a given term id.
    # The term pks are ordered by weight and title.

    # return
        # [(parent id, parent terms)].
    # '''      
    # with connection.cursor() as c:
        # c.execute(_SQLTIDParentTerms, [term_id])
        # for e in c.fetchall():
            # yield (e[0], e) 

# _SQLTIDChildTerms = "SELECT t.* FROM taxonomy_term t INNER JOIN taxonomy_termparent tp ON t.id = tp.tid WHERE tp.pid = %s ORDER BY t.weight, t.title"
# #from django.db import connection
# #c = connection.cursor()
# #c.execute(_SQL , [1])

# def child_terms(term_id):
    # '''
    # Child terms for a given term id.
    # The term pks are ordered by weight and title.

    # return
        # [(term_id, parent_id)]
    # '''      
    # with connection.cursor() as c:
        # c.execute(_SQLTIDChildTerms, [term_id])
        # for e in c.fetchall():
            # yield (e[0], e) 


  # # $result = db_query(db_rewrite_sql('SELECT t.tid, t.* FROM {term_data} t INNER JOIN {term_node} r ON r.tid = t.tid WHERE t.vid = %d AND r.vid = %d ORDER BY weight', 't', 'tid'), $vid, $node->vid);
# # Probably filter by tree too, in case placed in two different trees?
# _SQLEIDTerms = "SELECT t.* FROM taxonomy_term t INNER JOIN taxonomy_termelement te ON t.id = te.tid WHERE te.eid = %s ORDER BY t.weight, t.title"

# def element_terms(element_id):
    # with connection.cursor() as c:
        # c.execute(_SQLEIDTerms, [element_id])
        # for e in c.fetchall():
            # yield (e) 




class Taxonomy(models.Model):
    '''
    '''    
    title = models.CharField(
        max_length=255,
        db_index=True,
        blank=True,
        default='',
        help_text="Name for a tree of categories. Limited to 255 characters.",
    )
  
    slug = models.SlugField(
        max_length=64,
        blank=True,
        default='',
        help_text="Short name for use in urls.",
    )
      
    description = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text="Overall description of the tree of categories. Limited to 255 characters.",
    )
      
    # is_single = models.BooleanField(
        # "terms are single_parent",
        # blank=True,
        # default=True,
        # help_text="Single or many parents for a category in the tree (True = one only, False = many).",
    # )
      
    is_unique = models.BooleanField(
        "attached elements are unique",
        blank=True,
        default=True,
        help_text="Sinngle or many parents for a value attached to the tree catagories (True = one only, False = many).",
    )
      
    weight = models.PositiveSmallIntegerField(
        blank=True,
        default=0,
        db_index=True,
        help_text="Priority for display of the categories. Lower value orders first. 0 to 32767.",
    )
        
    #def get_absolute_url(self):
    #    return reverse("tree-detail", kwargs={"slug": self.slug})
        
    def __repr__(self):
        return "Taxonomy(title:{}, slug:{}, is_single:{}, is_unique={}, weight:{})".format(
            self.title,
            self.slug,
            self.is_single,
            self.is_unique,
            self.weight,
        )  
        
    def __str__(self):
        return "{0}".format(
            self.title if self.title else self.pk, 
        )

