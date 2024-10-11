from django.db import models
from django.urls import reverse

class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    description = models.TextField(max_length=255, blank=True)
    slug = models.SlugField(max_length=100, unique=True)
    cat_image = models.ImageField(upload_to='photos/categories', blank=True, null=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['category_name']

    def get_url(self):
        """Genera la URL para filtrar productos por categoría."""
        return reverse('products_by_category', args=[self.slug])

    def __str__(self):
        return self.category_name
