from django.test import TestCase
from taxonomy import NO_PARENT
from ttest.models import TestCat, TestCatParent



# Tests the class for attributes and checks, not the action.
# ./manage.py test ttest.tests.test_models
class TestModels(TestCase):
    
    def setUp(self):
        # Create a category for running tests on
        obj = TestCat.objects.create(
            name='Test1',
            weight=5,
            slug="test-1",
            description='test1',
        )
        TestCat.api.save(NO_PARENT, obj)
       
    # Think this is the only basic test?
    def test_parentage(self):
        tp = TestCatParent.objects.get(nid=1)
        self.assertEqual(tp.pid, -1)

