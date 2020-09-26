from django.test import TestCase

from taxonomy.models import TermParent



# Tests the class for attributes and checks, not the action.
class TestManagers(TestCase):
    
    def setUp(self):
        self.m = TermParent.objects
        
    def test_parents(self):
        # is subclass?
       # self.assertTrue(models.parent_terms(), )
        tids = self.m.parents(2)
        self.assertEqual(tids[0], 1)
        pass
       

    def test_children(self):
        # is subclass?
       # self.assertTrue(models.child_terms(), )
        tids = self.m.children(1)
        self.assertEqual(tids[0], 2)
        pass 
    
