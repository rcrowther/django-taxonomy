from django.contrib import admin
from taxonomy.models import Term, TermParent, TermElement
from taxonomy.forms import TermForm #, MultiTermForm
from django import forms
from django.utils.html import format_html
from functools import partial, reduce, update_wrapper
from django.http import HttpResponseRedirect


from django.core.exceptions import (
    FieldDoesNotExist, FieldError, PermissionDenied, ValidationError,
)
from django.forms.models import (
    BaseInlineFormSet, inlineformset_factory, modelform_defines_fields,
    modelform_factory, modelformset_factory,
)


from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

csrf_protect_m = method_decorator(csrf_protect)


def indented_term_titles(obj):
    #depth = TaxonomyAPI(obj.taxonomy_id).term(obj.id).depth()
    depth = obj.api(obj.id).depth()
    if (depth > 0):
        return '\u2007\u2007\u2007\u2007' * (depth - 1) + "\u2007└─\u2007" + obj.name
    else:
        return  obj.name
    
    
from django.views.generic import RedirectView

class TermAdmin(admin.ModelAdmin):
    #fields = ('tree', 'name', 'slug', 'description', 'weight')
    #form = forms.TermForm
    fields = ('parent', 'name', 'slug', 'description', 'weight')
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
        obj.api.save(pid, obj)       


    def delete_model(self, request, obj):
        """
        Given a model instance delete it from the database.
        """
        obj.api(obj.id).delete()


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
            r.context_data['tree_name'] = self.model._meta.model_name
        return r

    def changelist_view(self, request, extra_context=None):
        # add taxonomy_id to context
        # Personally, I think this is horrible
        r = super().changelist_view(request, extra_context=None)
        if (not (isinstance(r, HttpResponseRedirect))):
            r.context_data['tree_name'] = self.model._meta.model_name
            print('changelist_view')
            #print(str(r))
            #print(str(r.context_data['available_apps'][2]['models'][3]['add_url']))
            #r.context_data['available_apps'][2]['models'][3]['add_url'] =  '/admin/taxonomy/term/add?taxonomy_id=1'

        return r

# {'site_title': 'Django site admin', 'site_header': 'Django administration', 'site_url': '/', 'has_permission': True, 
# 'available_apps': [
# {'name': 'Article', 'app_label': 'article', 'app_url': '/admin/article/', 'has_module_perms': True, 'models': [{'name': 'Articles', 'object_name': 'Article', 'perms': {'add': True, 'change': True, 'delete': True, 'view': True}, 'admin_url': '/admin/article/article/', 'add_url': '/admin/article/article/add/', 'view_only': False}]}, {'name': 'Authentication and Authorization', 'app_label': 'auth', 'app_url': '/admin/auth/', 'has_module_perms': True, 'models': [{'name': 'Groups', 'object_name': 'Group', 'perms': {'add': True, 'change': True, 'delete': True, 'view': True}, 'admin_url': '/admin/auth/group/', 'add_url': '/admin/auth/group/add/', 'view_only': False}, {'name': 'Users', 'object_name': 'User', 'perms': {'add': True, 'change': True, 'delete': True, 'view': True}, 'admin_url': '/admin/auth/user/', 'add_url': '/admin/auth/user/add/', 'view_only': False}]}, {'name': 'Taxonomy', 'app_label': 'taxonomy', 'app_url': '/admin/taxonomy/', 'has_module_perms': True, 'models': [{'name': 'Taxonomys', 'object_name': 'Taxonomy', 'perms': {'add': True, 'change': True, 'delete': True, 'view': True}, 'admin_url': '/admin/taxonomy/taxonomy/', 'add_url': '/admin/taxonomy/taxonomy/add/', 'view_only': False}, {'name': 'Term elements', 'object_name': 'TermElement', 'perms': {'add': True, 'change': True, 'delete': True, 'view': True}, 'admin_url': '/admin/taxonomy/termelement/', 'add_url': '/admin/taxonomy/termelement/add/', 'view_only': False}, {'name': 'Term parents', 'object_name': 'TermParent', 'perms': {'add': True, 'change': True, 'delete': True, 'view': True}, 'admin_url': '/admin/taxonomy/termparent/', 'add_url': '/admin/taxonomy/termparent/add/', 'view_only': False}, 
# {'name': 'Terms', 'object_name': 'Term', 'perms': {'add': True, 'change': True, 'delete': True, 'view': True}, 
    # 'admin_url': '/admin/taxonomy/term/', 'add_url': '/admin/taxonomy/term/add/', 'view_only': False}]}
# ],
 # 'is_popup': False, 'is_nav_sidebar_enabled': True, 'module_name': 'terms', 'selection_note': '0 of 3 selected', 'selection_note_all': 'All 3 selected', 'title': 'Select term to change', 'to_field': None, 
# 'cl': <django.contrib.admin.views.main.ChangeList object at 0x7f301756e070>, 'media': Media(css={}, js=['admin/js/vendor/jquery/jquery.js', 'admin/js/jquery.init.js', 'admin/js/core.js', 'admin/js/admin/RelatedObjectLookups.js', 'admin/js/actions.js', 'admin/js/urlify.js', 'admin/js/prepopulate.js', 'admin/js/vendor/xregexp/xregexp.js']), 
# 'has_add_permission': True, 'opts': <Options for Term>, 
# 'action_form': <ActionForm bound=False, valid=Unknown, fields=(action;select_across)>, 
# 'actions_on_top': True, 'actions_on_bottom': False, 'actions_selection_counter': True, 'preserved_filters': '_changelist_filters=taxonomy_id%3D1', 'tree_name': 'site'
# }


    # # Thumpingly ugly overload of URLs to guess at ways of unrendering

        
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

