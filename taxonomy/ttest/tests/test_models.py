from django.test import TestCase

from ttest.models import Term, TermParent



# Tests the class for attributes and checks, not the action.
# ./manage.py test ttest.tests.test_models
class TestModels(TestCase):
    
    def setUp(self):
        # Create a category for running tests on
        obj = Term.objects.create(
            name='Test1',
            weight=5,
            slug="test-1",
            description='test1',
        )
        Term.api.save(TermParent.NO_PARENT, obj)
       
    # Think this is the only basic test?
    def test_parentage(self):
        tp = TermParent.objects.get(tid=1)
        self.assertEqual(tp.pid, -1)

