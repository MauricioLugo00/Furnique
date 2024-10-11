from django.shortcuts import render
from store.models import Product, ReviewRating

def home(request):
    products = Product.objects.all().filter(is_available=True).order_by('created_date')
    
    reviews = {}  # Inicializa reviews como un diccionario

    for product in products:
        reviews[product.id] = ReviewRating.objects.filter(product_id=product.id, status=True)

    context = {
        'products': products,
        'reviews': reviews,  # Envía el diccionario de reseñas al contexto
    }

    return render(request, 'home.html', context)
