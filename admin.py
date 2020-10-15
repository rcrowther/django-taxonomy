from django.contrib import admin
from taxonomy.models import Taxonomy, Term, TermParent, TermElement
from taxonomy.forms import TermForm #, MultiTermForm
from django import forms
from django.utils.html import format_html
from functools import partial, reduce, update_wrapper
from taxonomy.taxonomy import TaxonomyAPI
from django.http import HttpResponseRedirect


from django.core.exceptions import (
    FieldDoesNotExist, FieldError, PermissionDenied, ValidationError,
)
from django.forms.models import (
    BaseInlineFormSet, inlineformset_factory, modelform_defines_fields,
    modelform_factory, modelformset_factory,
)
class TaxonomyAdmin(admin.ModelAdmin):
    fields = ('name', 'slug', 'description', 'weight')
    list_display = ('name', 'term_list', 'term_add',)
    
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
from taxonomy.taxonomy import TaxonomyAPI

csrf_protect_m = method_decorator(csrf_protect)


def indented_term_titles(obj):
    depth = TaxonomyAPI(obj.taxonomy_id).term(obj.id).depth()
    if (depth > 1):
        return '\u2007\u2007\u2007\u2007' * (depth - 2) + "\u2007└─\u2007" + obj.name
    else:
        return  obj.name
    
    
from django.views.generic import RedirectView

class TermAdmin(admin.ModelAdmin):
    #fields = ('tree', 'name', 'slug', 'description', 'weight')
    #form = forms.TermForm
    fields = ('taxonomy_id', 'parent', 'name', 'slug', 'description', 'weight')
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

# ModelAdmin.get_list_display(request)
# ModelAdmin.get_list_display_links(request, list_display)¶
    #! save is not always called? Use a post_save signal?
    #! test this i_single save
    #! also need to do is_unique
    def save_model(self, request, obj, form, change):
        pid = form.cleaned_data.get('parent')
        tid = obj.id
        if (not change):        
            #TaxonomyAPI.term_save(pid, obj)
            obj.api.term_save(pid, obj)
        elif ('parent' in form.changed_data):
            #TaxonomyAPI(obj.taxonomy_id).term(tid).parent_update(pid)        
            obj.api(obj.taxonomy_id).term(tid).parent_update(pid)        


    def delete_model(self, request, obj):
        """
        Given a model instance delete it from the database.
        """
        obj.api(obj.taxonomy_id).term(obj.id).delete()


    def delete_queryset(self, request, queryset):
        """Given a queryset, delete it from the database."""
        #? More efficient with dedicated api.delete?
        print("Admin queryset delete...")
        for term in queryset:
            self.delete_model(request, term)
            
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

    def get_form(self, request, obj=None, change=False, **kwargs):
        # Must override this, or it returns a generic model form that
        # will try to process in changeview without understanding the
        # adittional data. Thus, fail validation.
        #! maybe reintroduce some Admin tweaks?
        return self.form

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
            r.context_data['tree_name'] = Taxonomy.objects.get(id=taxonomy_id).name
        return r

    def changelist_view(self, request, extra_context=None):
        # add taxonomy_id to context
        # Personally, I think this is horrible
        r = super().changelist_view(request, extra_context=None)
        if (not (isinstance(r, HttpResponseRedirect))):
            taxonomy_id = request.GET.get('taxonomy_id')
            r.context_data['tree_name'] = Taxonomy.objects.get(id=taxonomy_id).name
        return r
        

    # # Thumpingly ugly overload of URLs to guess at ways of unrendering
    # def get_urls(self):
        # from django.urls import path

        # def wrap(view):
            # def wrapper(*args, **kwargs):
                # return self.admin_site.admin_view(view)(*args, **kwargs)
            # wrapper.model_admin = self
            # return update_wrapper(wrapper, view)

        # info = self.model._meta.app_label, self.model._meta.model_name

        # return [
            # path('', wrap(self.changelist_view), name='%s_%s_changelist' % info),
            # path('add/', wrap(self.add_view), name='%s_%s_add' % info),
            # path('autocomplete/', wrap(self.autocomplete_view), name='%s_%s_autocomplete' % info),
            # path('<path:object_id>/history/', wrap(self.history_view), name='%s_%s_history' % info),
            # path('<path:object_id>/delete/', wrap(self.delete_view), name='%s_%s_delete' % info),
            # #path('<path:object_id>/change/', wrap(self.change_view), name='%s_%s_change' % info),
            # #path('<path:object_id>/change/', wrap(self.change_view), name='%s_%s_change' % info),
            # # For backwards compatibility (was the change url before 1.9)
            # #path('<path:object_id>/', wrap(RedirectView.as_view(
            # #    pattern_name='%s:%s_%s_change' % ((self.admin_site.name,) + info)
            # #))),
        # ]
        
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
