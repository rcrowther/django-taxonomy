from django.contrib import admin
from taxonomy.models import Term, TermParent
from taxonomy.forms import TermForm #, MultiTermForm
from django import forms
from django.utils.html import format_html
from functools import partial, reduce, update_wrapper
from django.http import HttpResponseRedirect


from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

csrf_protect_m = method_decorator(csrf_protect)



class TermParentAdmin(admin.ModelAdmin):
    fields = ('tid', 'pid')
admin.site.register(TermParent, TermParentAdmin)



def indented_term_titles(obj):
    #depth = TaxonomyAPI(obj.taxonomy_id).term(obj.id).depth()
    depth = obj.api(obj.id).depth()
    if (depth > 0):
        return '\u2007\u2007\u2007\u2007' * (depth - 1) + "\u2007└─\u2007" + obj.name
    else:
        return  obj.name
    
    
from django.views.generic import RedirectView

class TermAdmin(admin.ModelAdmin):
    fields = ('parent', 'name', 'slug', 'description', 'weight')

    #form = forms.ModelForm
    form = TermForm
    #form = MultiTermForm
    change_form_template = 'taxonomy/term_change_form.html'
    change_list_template = 'taxonomy/term_change_list.html'

    list_display = (indented_term_titles,)
    search_fields = ['name']

    # Construct a URL for adding element loaded with a term_id on the GET 
    # def termelement_add(self, obj):
        # return format_html('<a href="/admin/taxonomy/termelement/add?tid={}" class="button">Add element</a>',
            # obj.id
        # )
    # termelement_add.short_description = 'Add element'
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

admin.site.register(Term, TermAdmin)







