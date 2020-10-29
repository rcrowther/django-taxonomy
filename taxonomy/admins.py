from django.contrib import admin
from taxonomy.forms import NodeFormPartial



class NodeAdmin(admin.ModelAdmin):
    form = NodeFormPartial
    change_form_template = 'taxonomy/term_change_form.html'
    change_list_template = 'taxonomy/term_change_list.html'

    list_display = ('indented_node_titles',)
    search_fields = ['name']

        
    def indented_node_titles(self, obj):
        depth = obj.api(obj.id).depth()
        if (depth > 0):
            return '\u2007\u2007\u2007\u2007' * (depth - 1) + "\u2007●\u2007\u2007" + obj.name            
        else:
            return  obj.name
            
    indented_node_titles.short_description = 'Name'
    

    def save_model(self, request, obj, form, change):
        # usually the API would be called, but if not, this uses the 
        # API too.
        pid = form.cleaned_data.get('parent')
        obj.api.save(pid, obj)       

    def delete_model(self, request, obj):
        # usually the API would be called, but if not, this uses the 
        # API too.
        obj.api(obj.id).delete()

    def delete_queryset(self, request, queryset):
        # usually the API would be called, but if not, this uses the 
        # API too.
        #? More efficient with dedicated api.delete?
        for term in queryset:
            self.delete_model(request, term)
