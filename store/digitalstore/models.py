from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название категории')
    icon = models.ImageField(upload_to='icons/', verbose_name='Иконка категории', null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, verbose_name='Слаг категории ')

    def get_absolute_url(self):
        return reverse('category', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def get_icon(self):
        if self.icon:
            return self.icon.url
        else:
            return '-'


class Product(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название продукта')
    price = models.FloatField(verbose_name='Цена товара')
    image = models.ImageField(upload_to='products', verbose_name='Фото товара')
    color_name = models.CharField(max_length=50, verbose_name='Название цвета')
    color_code = models.CharField(max_length=7, verbose_name='Код цвета')
    slug = models.SlugField(unique=True, null=True, verbose_name='Слаг товара')
    discount = models.IntegerField(verbose_name='Скидка', null=True, blank=True)
    warranty = models.CharField(max_length=150, verbose_name='Гаррантия')
    quantity = models.IntegerField(default=0, verbose_name='Количество товара')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products", verbose_name='Категория')
    model = models.ForeignKey('ProductModel', on_delete=models.CASCADE, verbose_name='Модель товара', null=True,
                              blank=True)
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE, verbose_name='Бренд', null=True, blank=True)

    def get_absolute_url(self):
        return reverse('product', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def get_price(self):
        if self.discount:
            desc = self.price * self.discount / 100
            new_price = self.price - desc
            return new_price
        else:
            return self.price


class ProductModel(models.Model):
    title = models.CharField(max_length=150, verbose_name='Модель')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Модель'
        verbose_name_plural = 'Модели'


class Brand(models.Model):
    title = models.CharField(max_length=150, verbose_name='Бренд')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'


class Specifications(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Продукт')
    title = models.CharField(max_length=255, verbose_name='Название характеристики')
    value = models.CharField(max_length=255, verbose_name='Значение')

    def __str__(self):
        return f"{self.title}: {self.value}"

    class Meta:
        verbose_name = 'Характеристика'
        verbose_name_plural = 'Характеристики'


class FavoriteProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    def __str__(self):
        return f'Товар {self.product.title} пользователя {self.user.username}'

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, verbose_name='Пользователь')
    region = models.CharField(max_length=150, verbose_name='Регион', null=True, blank=True)
    city = models.CharField(max_length=150, verbose_name='Город', null=True, blank=True)
    street = models.CharField(max_length=150, verbose_name='Улица', null=True, blank=True)
    home = models.CharField(max_length=150, verbose_name='Дом №', null=True, blank=True)
    flat = models.CharField(max_length=150, verbose_name='Квартира №', null=True, blank=True)

    def __str__(self):
        return f'Покупатель {self.user.first_name} {self.user.last_name}'

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, verbose_name='Пользователь')
    first_name = models.CharField(max_length=150, verbose_name='Имя', null=True, blank=True)
    last_name = models.CharField(max_length=150, verbose_name='Фамилия', null=True, blank=True)
    phone = models.CharField(max_length=150, verbose_name='Номер телефона', null=True, blank=True)
    email = models.CharField(max_length=150, verbose_name='Эл.почта', null=True, blank=True)

    def __str__(self):
        return f'Профиль пользователя {self.user.username}'

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='Покупатель')
    is_completed = models.BooleanField(default=False, verbose_name='Статус заказа')
    payment = models.BooleanField(default=False, verbose_name='Статус оплаты')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата начала заказа')
    shipping = models.BooleanField(default=True, verbose_name='Доставка')

    def __str__(self):
        return f'Заказ покупателя {self.customer.user.first_name} по №{self.pk}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    # РЕализовать метод для получения суммы заказа
    @property
    def get_order_total_price(self):
        order_products = self.orderproduct_set.all()  # Получим товары заказа все
        total_price = sum([i.get_total_price for i in order_products])  # [2000, 5000]
        return total_price

    @property
    def get_order_total_quantity(self):
        order_products = self.orderproduct_set.all()
        total_quantity = sum([i.quantity for i in order_products])  # [2, 1]
        return total_quantity


class OrderProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.IntegerField(default=0, verbose_name='В количестве')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Заказ')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    @property
    def get_total_price(self):
        return self.quantity * self.product.get_price()

    def old_price(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f'Товар {self.product.title} для заказа № {self.order.pk}'

    class Meta:
        verbose_name = 'Товар в заказ'
        verbose_name_plural = 'Товары заказов'


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='Покупаетля')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Заказ')
    phone = models.CharField(max_length=50, verbose_name='Номер телефона получаетля')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата оформления доставки')
    comment = models.TextField(verbose_name='Комментарйи к заказу', null=True, blank=True, max_length=200)
    street = models.CharField(max_length=150, verbose_name='Улица')
    home = models.CharField(max_length=150, verbose_name='Дом №')
    flat = models.CharField(max_length=150, verbose_name='Квартира №', null=True, blank=True)
    region = models.ForeignKey('Region', on_delete=models.CASCADE, verbose_name='Регион доставки')
    city = models.ForeignKey('City', on_delete=models.CASCADE, verbose_name='Город доставки')

    def __str__(self):
        return f'Доставка на имя {self.customer.user.first_name} по заказу №:{self.order.pk}'

    class Meta:
        verbose_name = 'Адрес доставки'
        verbose_name_plural = 'Адреса доставок'


class Region(models.Model):
    name = models.CharField(max_length=200, verbose_name='Область')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Область'
        verbose_name_plural = 'Области'


class City(models.Model):
    name = models.CharField(max_length=200, verbose_name='Город')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name='Область города',
                               related_name='cities')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'
