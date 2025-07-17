from django import template
from digitalstore.models import Category, Product, FavoriteProduct

register = template.Library()


@register.simple_tag()
def get_categories():
    return Category.objects.all()


@register.simple_tag()
def get_correct(price):
    return f'{price:_}'.replace('_', ' ')


@register.simple_tag()
def get_same_products(category, model):
    products = Product.objects.filter(category=category, model=model)
    return products


@register.simple_tag(takes_context=True)
def query_params(context, **kwargs):
    query = context['request'].GET.copy()
    for key, value in kwargs.items():
        query[key] = value

    return query.urlencode()


@register.simple_tag()
def get_favorites(user):
    favorites = FavoriteProduct.objects.filter(user=user)
    products = [i.product for i in favorites]
    return products
