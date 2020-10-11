from django.db import models
from django.urls import reverse
from django.db import connection
from taxonomy.api import TaxonomyAPI


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



        




class TermBase(models.Model):

    taxonomy_id = models.IntegerField(
        "taxonomy id",
        db_index=True,
        help_text="Id of the tree this category is attached to.",
    )

    # Not unique.
    name = models.CharField(
        max_length=255,
        blank=True,
        default='',
        db_index=True,
        help_text="Name for the category. Limited to 255 characters.",
    )
    
    weight = models.PositiveSmallIntegerField(
        blank=True,
        default=0,
        db_index=True,
        help_text="Priority for display of several categories Lower value orders first. 0 to 32767.",
    )

    def __repr__(self):
        return "Term(taxonomy_id:{}, name:{}, weight:{})".format(
            self.taxonomy_id,
            self.name,
            self.weight,
        )  
          
    def __str__(self):
        return "{}".format(
            self.id, 
        )
        
    class Meta:
        abstract = True
        
        
class Term(TermBase):
    
    # taxonomy_id = models.IntegerField(
        # "tree id",
        # #choices=Taxonomy.tree_choices,
        # #default='',
        # db_index=True,
        # help_text="Id of the tree this category is attached to.",
    # )
    
    # Not unique. All terms in same table, different taxonomies.
    name = models.CharField(
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
      
    # weight = models.PositiveSmallIntegerField(
        # blank=True,
        # default=0,
        # db_index=True,
        # help_text="Priority for display of several categories Lower value orders first. 0 to 32767.",
    # )
        
    #def get_absolute_url(self):
    #    return reverse("term-detail", kwargs={"slug": self.slug})
    @classmethod
    def api(cls, taxonomy_id, term_id):
        return TermAPI(
            cls,
            TermParent, 
            TermElement, 
            taxonomy_id,
            term_id
         )
    #system = models.Manager()

    def __repr__(self):
        return "Term(taxonomy_id:{}, name:{}, slug:{}, weight:{})".format(
            self.taxonomy_id,
            self.name,
            self.slug,
            self.weight,
        )  
          
    def __str__(self):
        return "{}".format(
            self.name if self.name else self.id, 
        )





    
class Taxonomy(models.Model):
    '''
    '''    
    name = models.CharField(
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
      
    weight = models.PositiveSmallIntegerField(
        blank=True,
        default=0,
        db_index=True,
        help_text="Priority for display of the categories. Lower value orders first. 0 to 32767.",
    )

    # @classmethod
    # def get_api(cls, taxonomy_id):
        # return TaxonomyAPI(
            # cls,
            # Term, 
            # TermParent, 
            # TermElement, 
            # #taxonomy_id
         # )

    api = TaxonomyAPI(
            #'Taxonomy',
            Term, 
            TermParent, 
            TermElement
         )        
    #def get_absolute_url(self):
    #    return reverse("tree-detail", kwargs={"slug": self.slug})
        
    def __repr__(self):
        return "Taxonomy(name:{}, slug:{}, weight:{})".format(
            self.name,
            self.slug,
            self.weight,
        )  
        
    def __str__(self):
        return "{}".format(
            self.name if self.name else self.id, 
        )

