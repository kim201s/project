from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect

from .forms import LoginForm, RegisterForm, EditProfileForm
from .models import *
from django.views.generic import ListView, DetailView
from .utils import CartForAuthenticatedUser, get_cart_data


# Create your views here.

class ProductList(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'digitalstore/main.html'
    extra_context = {
        'title': 'DIGITALSTORE - Техника на любой вкус',
        'categories': Category.objects.all()
    }



class ProductDetail(DetailView):
    model = Product
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        product = Product.objects.get(slug=self.kwargs['slug'])
        specs = Specifications.objects.filter(product=product)
        related_products = Product.objects.filter(category=product.category).exclude(pk=product.pk)
        context['title'] = product.title
        context['products'] = related_products[::-1]
        context['specifications'] = specs

        return context

class ProductsByCategory(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'digitalstore/category_products.html'
    paginate_by = 2

    def get_queryset(self):
        brand_name = self.request.GET.get('brand')
        color_name = self.request.GET.get('color')
        discount = self.request.GET.get('discount')
        price = self.request.GET.get('price')

        category = Category.objects.get(slug=self.kwargs['slug'])
        products = Product.objects.filter(category=category)

        if brand_name:
            products = products.filter(brand__title=brand_name)
        if color_name:
            products = products.filter(color_name=color_name)
        if discount:
            products = products.filter(discount=discount)
        if price:
            products = products.filter(price=price)
        return products[::-1]

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        category = Category.objects.get(slug=self.kwargs['slug'])
        products = context['products']

        all_products = Product.objects.filter(category=category)

        brands = list(set([i.brand for i in all_products]))
        colors = list(set([i.color_name for i in all_products]))
        discounts = list(set([i.discount for i in all_products if i.discount is not None]))
        prices = list(set([i.get_price for i in all_products]))

        context['title'] = f'DIGITALSTORE - {category.title}'
        context['brands'] = brands
        context['colors'] = colors
        context['discounts'] = discounts
        context['prices'] = prices


        return context

def login_user_view(request):
    if request.user.is_authenticated:
        return redirect('main')
    else:
        if request.method == 'POST':
            form = LoginForm(data=request.POST)
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                return redirect('main')
        else:
            form = LoginForm()

        context = {
            'title': 'Авторизация',
            'form': form
        }
        return render(request, 'digitalstore/login.html', context)



def logout_user_view(request):
    if request.user.is_authenticated:
        logout(request)

    return redirect('main')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('main')
    else:
        if request.method == 'POST':
            form = RegisterForm(data=request.POST)
            if form.is_valid():
                user = form.save()

                customer = Customer.objects.create(user=user)
                customer.save()
                profile = Profile.objects.create(user=user)
                profile.save()

                return redirect('login')
        else:
            form = RegisterForm()
        context = {
            'title': 'Регистрация',
            'form': form
        }
        return render(request, 'digitalstore/registration.html', context)

def save_favorite_product(request, slug):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        product = Product.objects.get(slug=slug)
        user = request.user
        favorite_products = FavoriteProduct.objects.filter(user=user)
        if user:
            if product in [i.product for i in favorite_products]:
                fav_product = FavoriteProduct.objects.get(user=user, product=product)
                fav_product.delete()
            else:
                FavoriteProduct.objects.create(user=user, product=product)

        next_page = request.META.get('HTTP_REFERER', 'main')
        return redirect(next_page)


class FavoriteListView(LoginRequiredMixin, ListView):
    model = FavoriteProduct
    context_object_name = 'products'
    template_name = 'digitalstore/product_list.html'
    login_url = 'login'
    extra_context = {
        'title': 'Избранное'
    }

    def get_queryset(self):
        favorites = FavoriteProduct.objects.filter(user=self.request.user)
        products = [i.product for i in favorites]
        return products


def add_or_delete_product_view(request, slug, action):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        user_cart = CartForAuthenticatedUser(request, slug, action)
        next_page = request.META.get('HTTP_REFERER', 'main')
        return redirect(next_page)


def my_cart_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        order_info = get_cart_data(request)  # Функция даст информацию о корзине
        order_products = order_info['order_products']
        context = {
            'title': 'Ваша корзина',
            'order_total_price': order_info['order_total_price'],
            'order_total_quantity': order_info['order_total_quantity'],
            'order_products': order_products,
            'products': Product.objects.all().order_by('-created_at')
        }

        return render(request, 'digitalstore/my_cart.html', context)


def delete_product(request, pk, order_id):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        order = Order.objects.get(pk=order_id)
        if order.customer.user == request.user:
            order_product = OrderProduct.objects.get(pk=pk, order=order)
            order_product.delete()

        return redirect('my_cart')


def profile_user_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:

        if request.method == 'POST':
            profile_form = EditProfileForm(request.POST, instance=request.user.profile)
            if profile_form.is_valid() and profile_form.is_valid():
                profile_form.save()

            return redirect('profile')

        else:
            profile_form = EditProfileForm(instance=request.user.customer)

        try:
            orders = Order.objects.filter(customer=Customer.objects.get(user=request.user)).order_by('-created_at')
        except:
            orders = None

        context = {
            'title': 'My profile | Malias',
            'profile_form': profile_form,
            'orders': orders[:1],
        }

        return render(request, 'digitalstore/profile.html', context)