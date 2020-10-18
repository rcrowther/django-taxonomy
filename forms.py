from django import forms
from taxonomy.models import Term, TermParent
from django.utils.datastructures import MultiValueDict
from django.forms.widgets import HiddenInput
from django.forms.models import ModelFormMetaclass
from django.http.request import QueryDict
#from taxonomy.taxonomy import TaxonomyAPI

#N One of these forms handles single parenting, the other 
# multiparenting. much as I would love these two forms to be one, Django
# is defeating me with forms with dynamic fields. By the time we reach 
# init, which is where we would discover is_single status, the entire
# declarative field metaclass machinery has run. So there are two
# seperate forms (with consequential muddle in Admin).

#N These may be small forms, but full of tricks, and so annotated.
#N https://docs.djangoproject.com/en/3.1/topics/forms/modelforms/
#N https://medium.com/@hakibenita/how-to-add-custom-action-buttons-to-django-admin-8d266f5b0d41
class TermForm(forms.ModelForm):
    '''
    Handle single parenting. 
    '''
    #model = Term
    
    #! _errors
    # 1. It may be a modelform, but it has extra field for parent. This 
    # can be done.
    parent = forms.TypedChoiceField(
        # 2. Base default will be swapped
        coerce=lambda val: int(val),
    )
        
    def __init__(self, *args, **kwargs):
        # 3. Ensure 'initial' for purpose of setting parent fields
        if (not 'initial' in kwargs):
            kwargs['initial'] = {}
            
        # 4. dispatch between 'new' and 'change' forms
        # On either branch, followed by,
        # 5. Get the tree id. 
        # 6. Add choices to 'parents'
        # 7. Set a value on 'parents' (via. 'initial') to select values
        instance = kwargs.get('instance')
        if (instance):
            # probably an 'update'
            print('Termform update')
            # setup parent choices
            api = self._meta.model.api(instance.id)
            self.declared_fields['parent'].choices = api.reparent_choices()
            # ...then 'select' current parent
            kwargs['initial']['parent'] = api.id_parent()
        else:
            # An 'add' or base form (used by admin)
            print('Termform add')
            #preserved_filters = request.GET.get('_changelist_filters')
            print(str(kwargs))
            #initial = kwargs.get('initial')

            #self.declared_fields['parents'].choices = self.model.term_choices(taxonomy_id)
            #self.declared_fields['parent'].choices = self.model.objects.initial_choices(taxonomy_id)
            # setup parent choices
            self.declared_fields['parent'].choices = self._meta.model.api.initial_choices()
            # ...then 'select' current parent
            kwargs['initial']['parent'] = TermParent.NO_PARENT

        #print('meta')
        #print(str(self._meta.model))
#['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'error_messages', 'exclude', 'field_classes', 'fields', 'help_texts', 'labels', 'localized_fields', 'model', 'widgets']

        super().__init__(*args, **kwargs)
        
        # 8. The tree widget is hidden. This can be done in admin,
        # but is enforced here
        #self.fields['taxonomy_id'].widget = HiddenInput()
        #widgets = {'name': forms.HiddenInput()}

    class Meta:
        model = Term
        exclude = []

# class MultiTermForm(forms.ModelForm):
    # '''
    # Handle multi parenting. 
    # '''
    # model = Term
    
    # #! _errors
    # # 1. It may be a modelform, but it has extra field for parent. This 
    # # can be done.
    # parents = forms.TypedMultipleChoiceField(
        # coerce=lambda val: int(val),
        # # 2. Base default will be swapped
    # )
    
    
    # def __init__(self, *args, **kwargs):
        # # 3. Ensure 'initial' for purpose of setting parent field 
        # # 'selected'
        # if (not 'initial' in kwargs):
            # kwargs['initial'] = {}
            

        
        # # 4. dispatch between 'new' and 'change' forms
        # # On either branch, followed by,
        # # 5. Get the tree id. 
        # # 6. Add choices to 'parents'
        # # 7. Set a value on 'parents' (via. 'initial') to select values
        # instance = kwargs.get('instance')
        # print(str(kwargs))
        # if (instance):
            # # probably an 'update'
            # taxonomy_id = instance.taxonomy_id
            # #self.declared_fields['parents'].choices = self.model.term_choices_update(taxonomy_id, instance.id)
            # self.declared_fields['parents'].choices = self.model.objects.choices_update(taxonomy_id, instance.id)
            # kwargs['initial']['parents'] = list(instance.parent_ids())
        # else:
            # # An 'add' or base form (used by admin)
            # initial = kwargs.get('initial')
            # if (initial):
                # taxonomy_id = kwargs['initial']['taxonomy_id']
            # #self.declared_fields['parents'].choices = self.model.term_choices(taxonomy_id)
            # self.declared_fields['parents'].choices = self.model.objects.choices(taxonomy_id)
            # kwargs['initial']['parents'] = [TermParent.NO_PARENT]

        # print(str(kwargs))
        # # 8. The tree widget is hidden. This can be done in admin,
        # # but is enforced here
        
        # super().__init__(*args, **kwargs)

    # # class Meta:
        # # model = Author
        # # fields = ('name', 'title', 'birth_date')
        # # widgets = {
            # # 'name': Textarea(attrs={'cols': 80, 'rows': 20}),
        # # }
