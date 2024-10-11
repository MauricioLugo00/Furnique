from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

def _cart_id(request):
    # Obtiene o crea el ID del carrito de la sesión
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    # Obtiene el producto por su ID
    product = Product.objects.get(id=product_id)
    
    current_user = request.user
    
    if current_user.is_authenticated:
        # Lista para almacenar las variaciones del producto seleccionadas por el usuario
        product_variation = []
        
        # Si la solicitud es POST, busca las variaciones del producto en los datos del formulario
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                
                # Intenta obtener la variación del producto por categoría y valor
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass
        
        # Comprueba si el item ya existe en el carrito para este usuario
        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        
        if is_cart_item_exists:
            # Si el item existe, obtén el item del carrito para el usuario
            cart_item = CartItem.objects.filter(product=product, user=current_user)
            
            # Listas para almacenar variaciones existentes e IDs de los items del carrito
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variation.all() # Obtiene las variaciones actuales del item
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
                
            # Si la variación seleccionada ya existe en el carrito, incrementa la cantidad
            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            # Si la variación no existe, crea un nuevo item en el carrito
            else:
                item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                if len(product_variation) > 0:
                    item.variation.clear()  # Limpia variaciones anteriores
                    item.variation.add(*product_variation)  # Añade las nuevas variaciones
                item.save()
        
        else:
            # Si no existe el item en el carrito, crea un nuevo item
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user = current_user,
            )
            if len(product_variation) > 0:
                cart_item.variation.clear()  # Limpia las variaciones anteriores
                cart_item.variation.add(*product_variation)  # Añade las nuevas variaciones
            cart_item.save()
        
        # Redirige al carrito después de agregar el producto
        return redirect('cart')
    
    else:
        # Si el usuario no está autenticado, se maneja el carrito por sesión
        
        product_variation = []

        if request.method == 'POST':
            # Recolecta las variaciones del producto de los datos del formulario
            for item in request.POST:
                key = item
                value = request.POST[key]

                # Intenta obtener la variación correspondiente al producto
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

        # Obtén o crea un carrito basado en el ID de la sesión
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()

        # Comprueba si el item ya existe en el carrito
        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        if is_cart_item_exists:
            # Si el item existe, obtén el item del carrito
            cart_item = CartItem.objects.filter(product=product, cart=cart)

            # Listas para variaciones existentes e IDs del carrito
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variation.all()  # Obtén las variaciones actuales del item
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            # Si las variaciones seleccionadas coinciden, incrementa la cantidad
            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            # Si no coinciden, crea un nuevo item en el carrito
            else:
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                if len(product_variation) > 0:
                    item.variation.clear()  # Limpia las variaciones anteriores
                    item.variation.add(*product_variation)  # Añade las nuevas variaciones
                item.save()

        # Si no existe el item en el carrito, crea un nuevo item
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart,
            )
            if len(product_variation) > 0:
                cart_item.variation.clear()  # Limpia las variaciones anteriores
                cart_item.variation.add(*product_variation)  # Añade las nuevas variaciones
            cart_item.save()

        # Redirige al carrito después de agregar el producto
        return redirect('cart')



def remove_cart(request, product_id, cart_item_id):
    # Obtiene el producto
    product = get_object_or_404(Product, id=product_id)
    
    try:
        if request.user.is_authenticated:
            # Usuario autenticado: obtiene el item del carrito
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            # Usuario no autenticado: obtiene el carrito de la sesión y el item
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        
        if cart_item.quantity > 1:
            # Reduce la cantidad en 1 si hay más de 1
            cart_item.quantity -= 1
            cart_item.save()
        else:
            # Si solo queda 1, elimina el item del carrito
            cart_item.delete()
    except CartItem.DoesNotExist:
        # Maneja el caso donde no se encuentra el item
        pass
    
    return redirect('cart')


def remove_cart_item(request, product_id, cart_item_id):
    # Obtiene el producto
    product = get_object_or_404(Product, id=product_id)
    
    try:
        if request.user.is_authenticated:
            # Usuario autenticado: elimina el item del carrito
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            # Usuario no autenticado: obtiene el carrito de la sesión y elimina el item
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        
        # Elimina el CartItem completamente
        cart_item.delete()
    except CartItem.DoesNotExist:
        # Maneja el caso donde no se encuentra el item
        pass
    
    return redirect('cart')

def cart(request, total=0, quantity=0,cart_items=None):
    tax = 0
    grand_total=0
    
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = round((16/100) * total, 2)
        grand_total = total + tax
            
    except ObjectDoesNotExist:
        pass


    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }

    return render(request, 'store/cart.html', context)

@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = round((16/100) * total, 2)
        grand_total = total + tax

    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }


    return render(request, 'store/checkout.html', context)