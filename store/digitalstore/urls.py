from django.urls import path
from .views import *

urlpatterns = [
    path('', ProductList.as_view(), name='main'),
    path('product/<slug:slug>/', ProductDetail.as_view(), name='product'),
    path('category/<slug:slug>/', ProductsByCategory.as_view(), name='category'),
    path('login/', login_user_view, name='login'),
    path('logout/', logout_user_view, name='logout'),
    path('registration/', register_view, name='registration'),
    path('save_favorite/<slug:slug>/', save_favorite_product, name='save_favorite'),
    path('favorites/', FavoriteListView.as_view(), name='favorite'),
    path('add_or_delete/<slug:slug>/<str:action>/', add_or_delete_product_view, name='add_or_del'),
    path('my_cart/', my_cart_view, name='my_cart'),
    path('profile/', profile_user_view, name='profile'),
]
