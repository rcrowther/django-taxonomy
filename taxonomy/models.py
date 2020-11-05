from django.db import models
from django.core import checks
from taxonomy.api import NodeTreeAPI
from taxonomy import NO_PARENT


class AbstractNode(models.Model):

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
        return "Node(id:{}, name:{}, weight:{})".format(
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
            if (not(isinstance(cls.api, NodeTreeAPI))):
                errors.append(
                    checks.Error(
                        "'{}' attribute 'api' must be a subclass of NodeTreeAPI.".format(
                            cls.__name__,
                        ),
                        id='taxonomy.E002',
                    )
                )
        return errors
        
    class Meta:
        abstract = True

        
        
# Subclasses are unalatered, but a new one needed for every taxonomy.                
class AbstractNodeParent(models.Model):
    '''
    Parent terms to other terms
    '''
    # Sentinel for 'pid' if unparented.
    # Now that would beggar belief, an auto-increment that allows -1...
    #NO_PARENT = -1
    
    nid = models.IntegerField(
        "term id",
        db_index=True,
        help_text="Category parented by another category.",
    )
      
    # can be self.NO_PARENT, if at root of tree
    pid = models.IntegerField(
        "parent term id",
        db_index=True,
        blank=True,
        default=NO_PARENT,
        help_text="Category parenting another category.",
    )
    
    def __repr__(self):
        return  "NodeParent(nid:{0}, pid:{1})".format(
            self.nid,
            self.pid
        ) 
        
    def __str__(self):
        return "NodeParent({}-{})".format(
            self.nid, 
            self.pid if self.pid != NO_PARENT else 'NO_PARENT', 
        )

    class Meta:
        abstract = True


