from django.contrib import admin
from taxonomy.models import Tree, Term, TermParent, TermElement
from taxonomy.forms import TermForm, MultiTermForm
from django import forms
from django.utils.html import format_html
from functools import partial, reduce, update_wrapper

from django.core.exceptions import (
    FieldDoesNotExist, FieldError, PermissionDenied, ValidationError,
)
from django.forms.models import (
    BaseInlineFormSet, inlineformset_factory, modelform_defines_fields,
    modelform_factory, modelformset_factory,
)
class TreeAdmin(admin.ModelAdmin):
    fields = ('title', 'slug', 'description', 'is_single', 'is_unique', 'weight')
    list_display = ('title', 'term_list', 'term_add',)
    
    # Construct a URL for adding terms loaded with a tree_id on the GET 
    def term_add(self, obj):
        return format_html('<a href="/admin/taxonomy/term/add?tree_id={}" class="button">Add term</a>',
            obj.pk
        )
    term_add.short_description = 'Add term'

    # Construct a URL for listing terms within a tree (on the GET) 
    def term_list(self, obj):
        return format_html('<a href="/admin/taxonomy/term?tree_id={}" class="button">List terms</a>',
            obj.pk
        )
    term_list.short_description = 'List terms'
        
    def save_model(self, request, obj, form, change):
        # Save the tree. 
        # if multiple changed to single, we need to do some big-scale
        # hackery on TermParent (single to multiple is no more than a 
        # change of attribute) 
        if ('is_single' in form.changed_data and obj.is_single):
            # changed to single parenting 
            Tree.objects.multiple_to_single(obj.id)
            
        # Save the tree object
        obj.save()
        
admin.site.register(Tree, TreeAdmin)

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

csrf_protect_m = method_decorator(csrf_protect)


def indented_term_titles(obj):
    depth = 2
    return "{} \u2023 {}".format(' ' * depth, obj.title)
    
    
    
class TermAdmin(admin.ModelAdmin):
    #fields = ('tree', 'title', 'slug', 'description', 'weight')
    #form = forms.TermForm
    fields = ('tree_id', 'parents', 'title', 'slug', 'description', 'weight')
    #N cant be readonly, stops us pushing a value in.
    #readonly_fields = ('tree_id',)
    #form = forms.ModelForm
    #form = TermForm
    #form = MultiTermForm
    form = None
    change_form_template = 'taxonomy/term_change_form.html'
    change_list_template = 'taxonomy/term_change_list.html'
    #def get_form(self, request, obj=None, change=False, **kwargs):
     #   return TermForm

    list_display = (indented_term_titles,)

            
    def get_form(self, request, obj=None, change=False, **kwargs):
        """
        Return a Form class for use in the admin add view. This is used by
        add_view and change_view.
        """
        if 'fields' in kwargs:
            fields = kwargs.pop('fields')
        else:
            fields = flatten_fieldsets(self.get_fieldsets(request, obj))
        excluded = self.get_exclude(request, obj)
        exclude = [] if excluded is None else list(excluded)
        readonly_fields = self.get_readonly_fields(request, obj)
        exclude.extend(readonly_fields)
        # Exclude all fields if it's a change form and the user doesn't have
        # the change permission.
        if change and hasattr(request, 'user') and not self.has_change_permission(request, obj):
            exclude.extend(fields)
        if excluded is None and hasattr(self.form, '_meta') and self.form._meta.exclude:
            # Take the custom ModelForm's Meta.exclude into account only if the
            # ModelAdmin doesn't define its own.
            exclude.extend(self.form._meta.exclude)
        # if exclude is an empty list we pass None to be consistent with the
        # default on modelform_factory
        exclude = exclude or None

        # Remove declared form fields which are in readonly_fields.
        new_attrs = dict.fromkeys(f for f in readonly_fields if f in self.form.declared_fields)
        ##########
        print('gewt_form')
        print(str(request.GET))
        if (obj):
            tree_id = obj.tree_id
        else:
            #request.GET.get('')
            #tree_id = dict(request.GET.items())['tree_id']
            tree_id = request.GET.get('tree_id')
        print(str(tree_id))

        if Tree.tree_is_single(tree_id):
            form = TermForm
        else:
            form = MultiTermForm
        #form = type(self.form.__name__, (self.form,), new_attrs)
        form = type(form.__name__, (form,), new_attrs)
        ####################

        defaults = {
            'form': form,
            'fields': fields,
            'exclude': exclude,
            'formfield_callback': partial(self.formfield_for_dbfield, request=request),
            **kwargs,
        }

        if defaults['fields'] is None and not modelform_defines_fields(defaults['form']):
            defaults['fields'] = forms.ALL_FIELDS

        try:
            return modelform_factory(self.model, **defaults)
        except FieldError as e:
            raise FieldError(
                '%s. Check fields/fieldsets/exclude attributes of class %s.'
                % (e, self.__class__.__name__)
            )
            
    #! save is not always called? Use a post_save signal?
    #! test this i_single save
    #! also need to do is_unique
    def save_model(self, request, obj, form, change):
        print('admin save')
        print(str(form.cleaned_data))
        # Save the term. 
        #N There must be a tree id. The model will error if not.
        obj.save()
        
        TPModel = TermParent
        # The admin Term form has an additional parent field. 
        # This needs to be pulled so a parenting info can be 
        # constructed.
        pids = form.cleaned_data.get('parents')
        #N The form parent field can return None. While the model field 
        # defines a default, a value of None is an object in existence, 
        # so we need to assert the default NO_PARENT.
        #! very annoying, we get models when we need pids.
        #if (not pids):
        #    pids = [TPModel.NO_PARENT]
        #if (not isinstance(pids, list)):
        #    pids = [int(pids)]
        #else:
        #    pids = [pid.id for pid in pids]
        tid = obj.id
        #print(str(tp))
        #print(str(change))
        
        # only do this if the term is new or has changed parent
        # changes of parent require tree surgery
        # change of tree disallowed.
        if (not change):
            # it's an add action
            #tp = TermParent(tid=tid, pid=pid)
            #tp.save()
            TPModel.objects.parents_create(tid, pids)   
        if ('parents' in form.changed_data):
            # parent was changed.
            TPModel.objects.parents_update(tid, pids)   

    def delete_model(self, request, obj):
        """
        Given a model instance delete it from the database.
        """
        obj.delete()
        #taxonomy.term_delete([obj.id]) 

    def delete_queryset(self, request, queryset):
        """Given a queryset, delete it from the database."""
        queryset.delete()
        #taxonomy.term_delete([t.tid for t in queryset)) 
        
    #def get_object(self, request, object_id, from_field=None):
    #    return super().get_object(request, object_id, from_field)

    # @csrf_protect_m
    # def changeform_view(self, request, object_id=None, tree_id=None, form_url='', extra_context=None):
        # # boosted with tree_id
        # print(str(object_id))
        # with transaction.atomic(using=router.db_for_write(self.model)):
            # return self._changeform_view(request, object_id, form_url, extra_context)

    def add_view(self, request, tree_id=None, form_url='', extra_context=None):
        # boosted with tree_id
        #request.GET['tree_id'] = tree_id
        return self.changeform_view(request, None, form_url, extra_context)

    def _changeform_view(self, request, object_id, form_url, extra_context):
        # add tree_id to context
        # Personally, I think this is horrible
        r = super()._changeform_view(request, object_id, form_url, extra_context)
        tree_id = r.context_data['adminform'].form.instance.tree_id
        r.context_data['tree_name'] = Tree.objects.get(id=tree_id).title
        return r

    def changelist_view(self, request, extra_context=None):
        # add tree_id to context
        # Personally, I think this is horrible
        r = super().changelist_view(request, extra_context=None)
        tree_id = request.GET.get('tree_id')
        r.context_data['tree_name'] = Tree.objects.get(id=tree_id).title
        return r
        
    def get_urls(self):
        # Thumpingly ugly overload of URLs to carry tree_id on the 'add'
        # URL.
        from django.urls import path

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        r = []
        info = self.model._meta.app_label, self.model._meta.model_name
        # #/admin/taxonomy/term/1/change/
        #tree_relative_change_url = path('<path:object_id>/<int:tree_id>/change/', wrap(self.change_view), name='%s_%s_change' % info)
        #r.append(tree_relative_change_url)        
        tree_relative_add_url = path('<int:tree_id>/add/', wrap(self.add_view), name='%s_%s_add' % info)
        r.append(tree_relative_add_url)        
        r.extend( super().get_urls())
        
        #print(str(r))
        return r
        
    #def get_form(self, request, obj=None, change=False, **kwargs):
    #    form = super().get_form(request, obj, change, **kwargs)
    #    return form

admin.site.register(Term, TermAdmin)



class TermParentAdmin(admin.ModelAdmin):
    fields = ('tid', 'pid')
admin.site.register(TermParent, TermParentAdmin)



class TermElementAdmin(admin.ModelAdmin):
    fields = ('tid', 'eid')
admin.site.register(TermElement, TermElementAdmin)
