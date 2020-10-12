from taxonomy.models import Taxonomy, Term


def build_taxonomy():
    '''
    Make taxonomy, add 9 terms
    '''
    obj = Taxonomy(
            name='taxonomy 1', 
            slug='taxonomy_1', 
            description='taxonomy desc 1', 
            weight=3
            )
    Taxonomy.api.taxonomy_save(obj)

    x = 1
    while (x <= 8):
        xstr = str(x)
        obj = Term(
            taxonomy_id=1,
            name='term' + xstr, 
            slug='term_' + xstr, 
            description='term desc' + xstr, 
            weight=3
            )
        Taxonomy.api.term_save(-1, obj)
        x  += 1

def build_parented_taxonomy():
    '''
    Make taxonomy, add 9 terms
    '''
    obj = Taxonomy(
            name='taxonomy 1', 
            slug='taxonomy_1', 
            description='taxonomy desc 1', 
            weight=3
            )
    Taxonomy.api.taxonomy_save(obj)

    x = 1
    parent = -1
    while (x <= 8):
        xstr = str(x)
        obj = Term(
            taxonomy_id=1,
            name='term' + xstr, 
            slug='term_' + xstr, 
            description='term desc' + xstr, 
            weight=3
            )
        Taxonomy.api.term_save(parent, obj)
        parent = obj.id
        print('parent')
        print(str(parentb))
        x  += 1
