from django.test import TestCase

from taxonomy.models import Term, Taxonomy
from . import utils


# Tests the class for attributes and checks, not the action.
# ./manage.py test taxonomy.tests.test_api
class TestAPI(TestCase):
    '''
    Test API cache
    '''
    @classmethod
    def setUpTestData(cls):
        utils.build_taxonomy()
        
    def setUp(self):
        self.api = Taxonomy.api
        
    # def test_save_taxonomy(self):
        # obj = Taxonomy(name='taxonomy 1', slug='taxonomy_1', description='taxonomy 1 desc', weight=3)
        # self.api.taxonomy_save(obj)

    # def test_save_term(self):
        # obj = Term(taxonomy_id=1, name='term 1', slug='term_1', description='term 1 desc', weight=3)
        # self.api.term_save(-1, obj)
        
    def test_child_map(self):
        # is subclass?
       # self.assertTrue(models.parent_terms(), )
        xe = self.api.child_map(1)
        # children includes a -1 entry for unparented
        self.assertEqual(len(xe), 9)

    def test_parents(self):
        xe = self.api.parent_map(1)
        self.assertEqual(len(xe), 8)  
             
    def test_term_map(self):
        tids = self.api.term_map(1)
        self.assertEqual(len(tids), 8)

    def test_trees(self):
        # is subclass?
       # self.assertTrue(models.parent_terms(), )
        tree = self.api.tree(1)
        self.assertEqual(len(tree), 8)

    def test_locations(self):
        locs = self.api.tree_locations(1)
        self.assertEqual(len(locs), 8)       
         

    def test_clear(self):
        self.api.clear(1)
        # hidden vars avoid auto-rebuilds
        self.assertEqual(len(self.api._parents), 0)       
        self.assertEqual(len(self.api._children), 0)       
        self.assertEqual(len(self.api._terms), 0)       


# class TestAPI(TestCase):
    # def setUp(self):
        # self.api = Taxonomy.api
        # utils.build_taxonomy()
        
    # def test_children(self):
        # # is subclass?
       # # self.assertTrue(models.child_terms(), )
        # tids = self.api(1).children()
        # self.assertEqual(len(tids), 2)
        # pass 
