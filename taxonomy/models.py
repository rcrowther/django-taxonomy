from django.db import models
from django.core import checks
from taxonomy.api import TaxonomyAPI



class TermBase(models.Model):

    # A name field is required, or it creates some admin difficulties.
    # Not unique. The id is unique.
    name = models.CharField(
        max_length=255,
        blank=False,
        db_index=True,
        help_text="Name for the category. Limited to 255 characters.",
    )
        
    weight = models.PositiveSmallIntegerField(
        blank=True,
        default=0,
        db_index=True,
        help_text="Priority for display of several categories Lower value orders first. 0 to 32767.",
    )

    # Note that API usualls does CRUD actions. Admin calls api. So we
    # leave the model to do it's usual actions, in case users need those
    # for mainenance.
        
    def __repr__(self):
        return "Term(id:{}, name:{}, weight:{})".format(
            self.id,
            self.name,
            self.weight,
        )  
          
    def __str__(self):
        return "{}".format(
            self.name, 
        )

    @classmethod
    def check(cls, **kwargs):
        errors = super().check(**kwargs)
        if not cls._meta.swapped:
            if (cls.api is None):
                errors.append(
                    checks.Error(
                        "'{}' class must have an attribute 'api' declared.".format(
                            cls.__name__,
                        ),
                        id='taxonomy.E001',
                    )
                )
            if (not(isinstance(cls.api, TaxonomyAPI))):
                errors.append(
                    checks.Error(
                        "'{}' attribute 'api' must be a subclass of TaxonomyAPI.".format(
                            cls.__name__,
                        ),
                        id='taxonomy.E002',
                    )
                )
        return errors
        
    class Meta:
        abstract = True

        
# Subclasses are unalatered, but a new one needed for every taxonomy.                
class TermParentBase(models.Model):
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

    class Meta:
        abstract = True


