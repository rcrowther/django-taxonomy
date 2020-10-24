from django import forms
from taxonomy.models import TermParentBase
#from django.utils.datastructures import MultiValueDict
#from django.forms.widgets import HiddenInput
#from django.forms.models import ModelFormMetaclass
#from django.http.request import QueryDict
#from taxonomy.taxonomy import TaxonomyAPI


#N These may be small forms, but full of tricks, and so annotated.
#N https://docs.djangoproject.com/en/3.1/topics/forms/modelforms/
#N https://medium.com/@hakibenita/how-to-add-custom-action-buttons-to-django-admin-8d266f5b0d41
class TermFormPartial(forms.ModelForm):
    '''
    Handle single parenting. 
    '''    
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
            print(str(kwargs))
            # setup parent choices
            self.declared_fields['parent'].choices = self._meta.model.api.initial_choices()
            # ...then 'select' current parent
            kwargs['initial']['parent'] = TermParentBase.NO_PARENT

        super().__init__(*args, **kwargs)
        
        
    #class Meta:
        #model = Term
        #exclude = []
    #    pass

        
