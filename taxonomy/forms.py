from django import forms
from taxonomy.models import AbstractNodeParent
from taxonomy import NO_PARENT



class NodeFormPartial(forms.ModelForm):
    '''
    Handle a Category and parenting. 
    It's called Partial because, like a ModelForm, it will not 
    instanciate without a Meta declaration. This could be provided 
    for example, by declaration, or through a ModelAdmin.
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
        # 5. Add choices to 'parents'
        # 6. Set a value on 'parents' (via. 'initial') to select values
        instance = kwargs.get('instance')
        if (instance):
            # probably an 'update'
            # setup parent choices
            api = self._meta.model.api(instance.id)
            self.declared_fields['parent'].choices = api.reparent_choices()
            # ...then 'select' current parent
            kwargs['initial']['parent'] = api.id_parent()
        else:
            # An 'add' or base form (used by admin)
            # setup parent choices
            self.declared_fields['parent'].choices = self._meta.model.api.initial_choices()
            # ...then 'select' current parent
            kwargs['initial']['parent'] = NO_PARENT

        super().__init__(*args, **kwargs)
        
