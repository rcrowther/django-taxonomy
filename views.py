from django.shortcuts import render
from django.views.generic import DetailView
from taxonomy.models import Term
from article.models import Article



class CategoryDetailView(DetailView):
    model = Term
    context_object_name = 'category'
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        #ctx['nav_bar'] = Term.api.tree()
        #ctx['nav_bar'] = [(e[0], '<a href="{}">{}</a>'.format(e[1].slug, e[1].title)) for e in TaxonomyAPI(1).term(1).tree()]
        print('View object')
        print(str(Term.article_set))
        ctx['crumb_terms'] = Term.api(ctx['object'].id).ascendent_path()
        ctx['elements'] = Article.objects.filter(category=ctx['object'])
        return ctx
