from django.db import models
from django.urls import reverse
from django.db import connection
from taxonomy.api import TaxonomyAPI
from django.db.models import signals



class TermBase(models.Model):
    
    weight = models.PositiveSmallIntegerField(
        blank=True,
        default=0,
        db_index=True,
        help_text="Priority for display of several categories Lower value orders first. 0 to 32767.",
    )

    def delete(self, using=None, keep_parents=False):
        # api usually does this. Should the method be called manually, 
        # api does it.
        self.api(self.id).delete()

        
    def __repr__(self):
        return "Term(id:{}, name:{}, weight:{})".format(
            self.id,
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
      
        
    def get_absolute_url(self):
        return reverse("category_detail", kwargs={"slug": self.slug})

    api = None

    def __repr__(self):
        return "Term(id:{}, name:{}, slug:{}, weight:{})".format(
            self.id,
            self.name,
            self.slug,
            self.weight,
        )  
          
    def __str__(self):
        return "{}".format(
            self.name if self.name else self.id, 
        )


                
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

        
        
Term.api = TaxonomyAPI(
            Term, 
            TermParent, 
         ) 
