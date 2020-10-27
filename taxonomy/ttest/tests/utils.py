from ttest.models import Cat, CatParent


def build_taxonomy(count):
    '''
    Make count Terms, unparented
    '''
    x = 1
    while (x <= count):
        xstr = str(x)
        obj = Cat(
            name='term' + xstr, 
            slug='term-' + xstr, 
            description='desc' + xstr, 
            weight=3
            )
        Cat.api.save(CatParent.NO_PARENT, obj)
        x += 1

def build_parented_taxonomy(count):
    '''
    Make count Terms, parented in chain
    '''
    x = 1
    parent = CatParent.NO_PARENT
    while (x <= count):
        xstr = str(x)
        obj = Cat(
            name='term' + xstr, 
            slug='term-' + xstr, 
            description='desc' + xstr, 
            weight=3
            )
        Cat.api.save(parent, obj)
        parent = obj.id
        x += 1
