from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import *
from .forms import CategoryForm

# Register your models here.


# admin.site.register(Category)
# admin.site.register(Product)
admin.site.register(Brand)
admin.site.register(ProductModel)
admin.site.register(Specifications)
admin.site.register(FavoriteProduct)

admin.site.register(Customer)
admin.site.register(Profile)
admin.site.register(Order)
admin.site.register(OrderProduct)
admin.site.register(ShippingAddress)
admin.site.register(Region)
admin.site.register(City)



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'category_icon')
    list_display_links = ('pk', 'title')
    prepopulated_fields = {'slug': ('title',)}
    form = CategoryForm

    def category_icon(self, obj):
        if obj.icon:
            try:
                return mark_safe(f'<img src="{obj.icon.url}">')
            except:
                return 'No icon'
        else:
            return 'No icon'

    category_icon.short_description = 'Иконка'


class SpecificationsInline(admin.TabularInline):
    model = Specifications
    fk_name = 'product'
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'price', 'quantity', 'discount', 'category', 'product_image')
    list_display_links = ('pk', 'title')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [SpecificationsInline]
    list_editable = ('price', 'quantity', 'discount')
    list_filter = ('category', 'discount', 'brand')

    def product_image(self, obj):
        if obj.image:
            try:
                return mark_safe(f'<img src="{obj.image.url}" width="70">')
            except:
                return 'No image'
        else:
            return 'No image'

    product_image.short_description = 'Фото товара'
