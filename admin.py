from django.contrib import admin
from taxonomy.models import Term, TermParent
#from taxonomy.forms import TermFormPartial
#from django import forms
#from django.http import HttpResponseRedirect
from taxonomy import admins

class TermParentAdmin(admin.ModelAdmin):
    fields = ('tid', 'pid')
admin.site.register(TermParent, TermParentAdmin)

    
class TermAdmin(admins.TermAdmin):
    fields = ('parent', 'name', 'slug', 'description', 'weight')
    prepopulated_fields = {"slug": ("name",)}
admin.site.register(Term, TermAdmin)
    
# from django.views.generic import RedirectView

# class TermAdmin(admin.ModelAdmin):
    # fields = ('parent', 'name', 'slug', 'description', 'weight')
    # prepopulated_fields = {"slug": ("name",)}

    # #form = forms.ModelForm
    # form = TermForm
    # change_form_template = 'taxonomy/term_change_form.html'
    # change_list_template = 'taxonomy/term_change_list.html'

    # list_display = ('indented_term_titles',)
    # search_fields = ['name']

    # def __init__(self, model, admin_site):
        # super().__init__(model, admin_site)
        # # Want a copy of the form with 
        # #self.form = type(model._meta.object_name + 'Form', (TermForm,), dict())
        # #self.form.Meta.model = self.model
        
    # def indented_term_titles(self, obj):
        # depth = obj.api(obj.id).depth()
        # if (depth > 0):
            # return '\u2007\u2007\u2007\u2007' * (depth - 1) + "\u2007└─\u2007" + obj.name
        # else:
            # return  obj.name
            
    # indented_term_titles.short_description = 'Name'
    

    # def save_model(self, request, obj, form, change):
        # # usually the API would be called, but if not, this uses the 
        # # API too.
        # pid = form.cleaned_data.get('parent')
        # obj.api.save(pid, obj)       

    # def delete_model(self, request, obj):
        # # usually the API would be called, but if not, this uses the 
        # # API too.
        # obj.api(obj.id).delete()

    # def delete_queryset(self, request, queryset):
        # # usually the API would be called, but if not, this uses the 
        # # API too.
        # #? More efficient with dedicated api.delete?
        # print("Admin queryset delete...")
        # for term in queryset:
            # self.delete_model(request, term)

    # #def get_form(self, request, obj=None, change=False, **kwargs):
        # # Must override this, or it returns a generic model form that
        # # will try to process in changeview without understanding the
        # # adittional data. Thus, fail validation.
        # #! maybe reintroduce some Admin tweaks?
   # #     return self.form

# admin.site.register(Term, TermAdmin)
