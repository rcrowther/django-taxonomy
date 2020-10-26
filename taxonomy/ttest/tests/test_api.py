from django.test import TestCase
from taxonomy.api import DepthTid
from ttest.models import Term, TermParent
from . import utils


# Tests the class for attributes and checks, not the action.
# ./manage.py test ttest.tests.test_api
class TestAPIBase(TestCase):
    '''
    Test API cache
    '''
    @classmethod
    def setUpTestData(cls):
        # build unparented taxonomy of eight terms
        utils.build_taxonomy(8)
        
    def setUp(self):
        self.api = Term.api
        
    def test_child_map(self):
        xe = self.api.child_map()
        # children includes a -1 entry for unparented
        self.assertEqual(len(xe), 9)

    def test_parent_map(self):
        xe = self.api.parent_map()
        self.assertEqual(len(xe), 8)  
             
    def test_term_map(self):
        tids = self.api.term_map()
        self.assertEqual(len(tids), 8)

    def test_ftree(self):
        tree = self.api.ftree()
        self.assertEqual(len(tree), 8)

    def test_ftree_type(self):
        tree = self.api.ftree()
        self.assertIs(tree[0].__class__, DepthTid)

    def test_tree_locations(self):
        locs = self.api.tree_locations()
        self.assertEqual(len(locs), 8)       
         
         

class TestAPIMethods(TestCase):
    @classmethod
    def setUpTestData(cls):
        # build parented taxonomy of eight terms
        utils.build_parented_taxonomy(8)
        
    def setUp(self):
        self.api = Term.api
        
    def test_clear(self):
        self.api.clear()
        # hidden vars avoid auto-rebuilds
        self.assertEqual(len(self.api._parents), 0)       
        self.assertEqual(len(self.api._children), 0)       
        self.assertEqual(len(self.api._terms), 0)       
        self.assertIs(self.api._ftree, None)
        self.assertIs(self.api._tree_locations, None)

    def test_depth_id_tree(self):
        tree = self.api.depth_id_tree(max_depth=3)
        self.assertEqual(len(tree), 3)

    def test_tree(self):
        tree = self.api.tree(max_depth=5)
        self.assertEqual(len(tree), 5)
        
    #def save(new_parent_id, obj)

    def test_delete(self):
        self.api.delete()
        self.assertEqual(len(self.api._children), 0)       
                
                
                
class TestAPITermMethods(TestCase):
    # '''
    # Test API cache
    # '''
    @classmethod
    def setUpTestData(cls):
        # build parented taxonomy of eight terms
        utils.build_parented_taxonomy(8)
        
    def setUp(self):
        self.api = Term.api(3)

    def test_term(self):
        t = self.api.term()
        self.assertIs(t.__class__, Term)
        
    def test_depth(self):
        # depth is from 0
        self.assertEqual(self.api.depth(), 2)

    def test_id_parent(self):
        self.assertEqual(self.api.id_parent(), 2)
        
    def test_id_children(self):
        self.assertEqual(len(self.api.id_children()), 1)

    def test_ascendants(self):
        # includes self
        self.assertEqual(len(self.api.ascendants()), 2)

    def test_descendants(self):
        # not includes self
        self.assertEqual(len(self.api.descendants()), 5)

    #! Can not run mutations in this test case
    # def test_delete(self):
        # self.api.delete()
        # self.assertEqual(len(Term.api.term_map()), 2)
    # def initial_choices(self):
    # def reparent_choices(self):
    # def depth_id_tree(self, max_depth=None):
    # def depth_id_ascendant_path(self):


