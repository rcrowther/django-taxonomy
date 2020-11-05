from django.db import models
from django.core import checks
from django.urls import reverse
from taxonomy.api import NodeTreeAPI
from taxonomy.models import AbstractNode, AbstractNodeParent




class TestCat(AbstractNode):

    # Not unique. Terms may be in different taxonomies. They may
    # be duplicated at different places in a hierarchy e.g. 'sports>news'
    # 'local>news'.
    slug = models.SlugField(
        max_length=64,
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
        return "Category(id:{}, name:{}, slug:{}, weight:{})".format(
            self.id,
            self.name,
            self.slug,
            self.weight,
        ) 



class TestCatParent(AbstractNodeParent):
        pass
                

# Always this format, but a new one needed for every taxonomy.
TestCat.api = NodeTreeAPI(
            TestCat, 
            TestCatParent, 
         ) 
