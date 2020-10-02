from django.contrib import admin
from taxonomy.models import Taxonomy, Term, TermParent, TermElement
from taxonomy.forms import TermForm #, MultiTermForm
from django import forms
from django.utils.html import format_html
from functools import partial, reduce, update_wrapper
from taxonomy.taxonomy import TaxonomyAPI


from django.core.exceptions import (
    FieldDoesNotExist, FieldError, PermissionDenied, ValidationError,
)
from django.forms.models import (
    BaseInlineFormSet, inlineformset_factory, modelform_defines_fields,
    modelform_factory, modelformset_factory,
)
class TaxonomyAdmin(admin.ModelAdmin):
    fields = ('title', 'slug', 'description', 'is_unique', 'weight')
    list_display = ('title', 'term_list', 'term_add',)
    
    # Construct a URL for adding terms loaded with a taxonomy_id on the GET 
    def term_add(self, obj):
        return format_html('<a href="/admin/taxonomy/term/add?taxonomy_id={}" class="button">Add term</a>',
            obj.pk
        )
    term_add.short_description = 'Add term'

    # Construct a URL for listing terms within a tree (on the GET) 
    def term_list(self, obj):
        return format_html('<a href="/admin/taxonomy/term?taxonomy_id={}" class="button">List terms</a>',
            obj.pk
        )
    term_list.short_description = 'List terms'
        
    def save_model(self, request, obj, form, change):
        # Save the tree. 
        # if multiple changed to single, we need to do some big-scale
        # hackery on TermParent (single to multiple is no more than a 
        # change of attribute) 
        # if ('is_single' in form.changed_data and obj.is_single):
            # # changed to single parenting 
            # Tree.objects.multiple_to_single(obj.id)
            
        # Save the tree object
        obj.save()
        
admin.site.register(Taxonomy, TaxonomyAdmin)

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

csrf_protect_m = method_decorator(csrf_protect)


def indented_term_titles(obj):
    depth = 2
    return "{} \u2023 {}".format(' ' * depth, obj.title)
    
    
    
class TermAdmin(admin.ModelAdmin):
    #fields = ('tree', 'title', 'slug', 'description', 'weight')
    #form = forms.TermForm
    fields = ('taxonomy_id', 'parent', 'title', 'slug', 'description', 'weight')
    #N cant be readonly, stops us pushing a value in.
    #readonly_fields = ('taxonomy_id',)
    #form = forms.ModelForm
    form = TermForm
    #form = MultiTermForm
    change_form_template = 'taxonomy/term_change_form.html'
    change_list_template = 'taxonomy/term_change_list.html'
    #def get_form(self, request, obj=None, change=False, **kwargs):
     #   return TermForm

    list_display = (indented_term_titles,)

    #! save is not always called? Use a post_save signal?
    #! test this i_single save
    #! also need to do is_unique
    def save_model(self, request, obj, form, change):
        print('admin save')
        print(str(form.cleaned_data))
        # Save the term. 
        ## There must be a tree id. The model will error if not.
        obj.save()
        
        # fix the parents
        ## The admin Term form has an additional parent field. 
        pid = form.cleaned_data.get('parent')
        tid = obj.id
        api = TaxonomyAPI(obj.taxonomy_id).term(tid)
        if (not change):
            api.parent_create(pid)
        elif ('parent' in form.changed_data):
            api.parent_update(pid)

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
    # def changeform_view(self, request, object_id=None, taxonomy_id=None, form_url='', extra_context=None):
        # # boosted with taxonomy_id
        # print(str(object_id))
        # with transaction.atomic(using=router.db_for_write(self.model)):
            # return self._changeform_view(request, object_id, form_url, extra_context)

    #def add_view(self, request, taxonomy_id=None, form_url='', extra_context=None):
        # boosted with taxonomy_id
        #request.GET['taxonomy_id'] = taxonomy_id
    #    return self.changeform_view(request, None, form_url, extra_context)

    def _changeform_view(self, request, object_id, form_url, extra_context):
        # add taxonomy_id to context
        r = super()._changeform_view(request, object_id, form_url, extra_context)
        # Personally, I think this is horrible
        # anyway, the response needs to be a form
        if isinstance(r, TermForm):
            # for an update form the id comes through the instance
            # (there's always an instance, but it may be empty)
            taxonomy_id = r.context_data['adminform'].form.instance.taxonomy_id
            if (not taxonomy_id):
                # for a add form the id comes in GET
                taxonomy_id = request.GET['taxonomy_id']
            r.context_data['tree_name'] = Taxonomy.objects.get(id=taxonomy_id).title
        return r

    def changelist_view(self, request, extra_context=None):
        # add taxonomy_id to context
        # Personally, I think this is horrible
        r = super().changelist_view(request, extra_context=None)
        taxonomy_id = request.GET.get('taxonomy_id')
        r.context_data['tree_name'] = Taxonomy.objects.get(id=taxonomy_id).title
        return r
        
    # def get_urls(self):
        # # Thumpingly ugly overload of URLs to carry taxonomy_id on the 'add'
        # # URL.
        # from django.urls import path

        # def wrap(view):
            # def wrapper(*args, **kwargs):
                # return self.admin_site.admin_view(view)(*args, **kwargs)
            # wrapper.model_admin = self
            # return update_wrapper(wrapper, view)

        # r = []
        # info = self.model._meta.app_label, self.model._meta.model_name
        # # #/admin/taxonomy/term/1/change/
        # #tree_relative_change_url = path('<path:object_id>/<int:taxonomy_id>/change/', wrap(self.change_view), name='%s_%s_change' % info)
        # #r.append(tree_relative_change_url)        
        # tree_relative_add_url = path('<int:taxonomy_id>/add/', wrap(self.add_view), name='%s_%s_add' % info)
        # r.append(tree_relative_add_url)        
        # r.extend( super().get_urls())
        
        # #print(str(r))
        # return r
        
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
