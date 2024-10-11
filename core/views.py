from django.shortcuts import render
from store.models import Product, ReviewRating

def home(request):
    products = Product.objects.all().filter(is_available=True).order_by('created_date')

    # Inicializa reviews como una lista vacía
    reviews = []

    for product in products:
        # Agrega las reseñas para cada producto a la lista
        product_reviews = ReviewRating.objects.filter(product_id=product.id, status=True)
        reviews.extend(product_reviews)  # Agrega las reseñas a la lista

    context = {
        'products': products,
        'reviews': reviews,
    }

    return render(request, 'home.html', context)
