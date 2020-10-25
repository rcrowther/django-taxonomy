from django.contrib import admin
from taxonomy.models import Term, TermParent
from taxonomy import admins

class TermParentAdmin(admin.ModelAdmin):
    fields = ('tid', 'pid')
admin.site.register(TermParent, TermParentAdmin)

    
class TermAdmin(admins.TermAdmin):
    fields = ('parent', 'name', 'slug', 'description', 'weight')
    prepopulated_fields = {"slug": ("name",)}
admin.site.register(Term, TermAdmin)
