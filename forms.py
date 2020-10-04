from django import forms
from taxonomy.models import Term, Taxonomy, TermParent
from django.utils.datastructures import MultiValueDict
from django.forms.widgets import HiddenInput
from django.forms.models import ModelFormMetaclass
from taxonomy.taxonomy import TaxonomyAPI

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
    model = Term
    
    #! _errors
    # 1. It may be a modelform, but it has extra field for parent. This 
    # can be done.
    parent = forms.TypedChoiceField(
        # 2. Base default will be swapped
        coerce=lambda val: int(val),
    )
        
    def __init__(self, *args, **kwargs):
        # 3. Ensure 'initial' for purpose of setting parent field 
        # 'selected'
        if (not 'initial' in kwargs):
            kwargs['initial'] = {}
            
        # 4. dispatch between 'new' and 'change' forms
        # On either branch, followed by,
        # 5. Get the tree id. 
        # 6. Add choices to 'parents'
        # 7. Set a value on 'parents' (via. 'initial') to select values
        instance = kwargs.get('instance')
        #print(str(kwargs))
        if (instance):
            # probably an 'update'
            print('Termform update')
            taxonomy_id = instance.taxonomy_id
            #self.declared_fields['parents'].choices = self.model.term_choices_update(taxonomy_id, instance.id)
            #self.declared_fields['parent'].choices = self.model.objects.reparent_choices(taxonomy_id, instance.id)
            api = TaxonomyAPI(taxonomy_id).term(instance.id)
            self.declared_fields['parent'].choices = api.reparent_choices()
            kwargs['initial']['parent'] = api.parent()
        else:
            # An 'add' or base form (used by admin)
            print('Termform add')
            #initial = kwargs.get('initial')
            #if (initial):
            #    taxonomy_id = kwargs['initial']['taxonomy_id']
            taxonomy_id = kwargs['initial'].get('taxonomy_id', None)
            #self.declared_fields['parents'].choices = self.model.term_choices(taxonomy_id)
            #self.declared_fields['parent'].choices = self.model.objects.initial_choices(taxonomy_id)
            self.declared_fields['parent'].choices = TaxonomyAPI(taxonomy_id).initial_choices()
            kwargs['initial']['parent'] = TermParent.NO_PARENT

        #print(str(kwargs))

        super().__init__(*args, **kwargs)
        
        # 8. The tree widget is hidden. This can be done in admin,
        # but is enforced here
        #self.fields['taxonomy_id'].widget = HiddenInput()
        #widgets = {'name': forms.HiddenInput()}



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
