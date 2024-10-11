from django.db import models
from category.models import Category
from django.urls import reverse
from accounts.models import Accounts
from django.db.models import Avg, Count


class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    images = models.ImageField(upload_to='photos/products')
    stock = models.PositiveIntegerField()  # Usar PositiveIntegerField para evitar valores negativos
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name

    def average_review(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        return reviews['average'] or 0  # Retorna 0 si no hay reseñas

    def count_reviews(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        return reviews['count'] or 0  # Retorna 0 si no hay reseñas


class VariationManager(models.Manager):
    def colors(self):
        return self.filter(variation_category='color', is_active=True)

    def sizes(self):
        return self.filter(variation_category='talla', is_active=True)


VARIATION_CATEGORY_CHOICES = (
    ('color', 'Color'),
    ('talla', 'Talla'),
)

class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=VARIATION_CATEGORY_CHOICES)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        return f'{self.variation_category}: {self.variation_value}'


class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Accounts, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2)  # Limitar la precisión del rating
    ip = models.GenericIPAddressField(blank=True, null=True)  # Mejor campo para IP
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Review by {self.user.email} on {self.product.product_name}'


class ProductGallery(models.Model):
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='store/products', max_length=255)

    def __str__(self):
        return self.product.product_name
