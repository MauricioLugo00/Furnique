from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, UserProfileForm, UserForm
from .models import Accounts, UserProfile
from orders.models import Order
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import authenticate, login as auth_login
from carts.views import _cart_id
from carts.models import Cart, CartItem
import requests
import random
from django.views.decorators.csrf import csrf_protect

@csrf_protect
@csrf_protect
def register(request):
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            confirm_password = request.POST.get('confirm_password')

            # Verificar que las contraseñas coinciden
            if password != confirm_password:
                messages.error(request, 'Las contraseñas no coinciden.')
                return redirect('register')

            username = email.split("@")[0]  # Crear nombre de usuario a partir del email

            # Crear el usuario sin activación
            user = Accounts.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
                phone_number=phone_number,
            )

            # Crear el perfil del usuario
            profile = UserProfile(user=user, profile_picture='default/default-user.png')
            profile.save()

            messages.success(request, 'Te has registrado exitosamente. Puedes iniciar sesión ahora.')
            return redirect('/accounts/login/')

    return render(request, 'accounts/register.html', {'form': form})


@csrf_protect
@csrf_protect
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, 'Por favor, completa todos los campos.')
            return redirect('login')

        # Autenticación del usuario usando el email
        user = authenticate(request, username=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exist = CartItem.objects.filter(cart=cart).exists()

                if is_cart_item_exist:
                    product_variation = [list(item.variation.all()) for item in CartItem.objects.filter(cart=cart)]
                    cart_items = CartItem.objects.filter(user=user)
                    ex_var_list = [list(item.variation.all()) for item in cart_items]
                    ids = [item.id for item in cart_items]

                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = ids[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.save()
                        else:
                            for item in CartItem.objects.filter(cart=cart):
                                item.user = user
                                item.save()
            except Cart.DoesNotExist:
                pass

            # Iniciar sesión
            auth_login(request, user)
            messages.success(request, 'Has iniciado sesión exitosamente.')

            # Redirigir a la página anterior o al dashboard
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except (ValueError, KeyError):
                return redirect('dashboard')
        else:
            messages.error(request, 'Los datos son incorrectos.')
            return redirect('login')

    return render(request, 'accounts/login.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'Has salido de sesión')
    return redirect('login')



@login_required(login_url='login')
def dashboard(request):
    orders = Order.objects.filter(user_id=request.user.id, is_ordered=True).order_by('-created_at')
    orders_count = orders.count()
    userprofile = UserProfile.objects.get(user_id=request.user.id)

    context = {
        'orders_count': orders_count,
        'userprofile': userprofile,
    }

    return render(request, 'accounts/dashboard.html', context)


def forgotPassword(request):
    if request.method == 'POST':
        phone_number = request.POST['phone_number']
        if Accounts.objects.filter(phone_number=phone_number).exists():
            user = Accounts.objects.get(phone_number=phone_number)
            
            # Generar un código de verificación
            verification_code = random.randint(1000, 9999)
            
            # Guardar el código en la sesión
            request.session['verification_code'] = verification_code
            request.session['user_id'] = user.id
            
            # Aquí se puede integrar una API de envío de SMS
            # Enviar el código al teléfono registrado (usando una API SMS, o mostrar en pantalla para demo)
            messages.success(request, f'Tu código de verificación es {verification_code}')
            
            return redirect('verify_code')  # Redirige al formulario para ingresar el código
        else:
            messages.error(request, 'No se encontró ninguna cuenta con ese número de teléfono')
            return redirect('forgotPassword')

    return render(request, 'accounts/forgotPassword.html')



def verify_code(request):
    if request.method == 'POST':
        entered_code = request.POST['verification_code']
        stored_code = request.session.get('verification_code')
        
        if str(entered_code) == str(stored_code):
            messages.success(request, 'Código verificado. Ahora puedes cambiar tu contraseña.')
            return redirect('resetPassword')
        else:
            messages.error(request, 'El código ingresado es incorrecto.')
            return redirect('verify_code')
    
    return render(request, 'accounts/verify_code.html')



def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            user_id = request.session.get('user_id')
            user = Accounts.objects.get(pk=user_id)
            user.set_password(password)
            user.save()
            
            # Limpiar la sesión
            del request.session['user_id']
            del request.session['verification_code']
            
            messages.success(request, 'La contraseña se actualizó correctamente')
            return redirect('login')
        else:
            messages.error(request, 'La contraseña de confirmación no concuerda')
            return redirect('resetPassword')
    
    return render(request, 'accounts/resetPassword.html')


def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {'orders': orders}
    return render(request, 'accounts/my_orders.html', context)


@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Su información fue guardada con éxito')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }

    return render(request, 'accounts/edit_profile.html', context)


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Accounts.objects.get(username=request.user.username)

        if new_password == confirm_password:
            if user.check_password(current_password):
                user.set_password(new_password)
                user.save()
                messages.success(request, 'La contraseña se actualizó correctamente')
                return redirect('change_password')
            else:
                messages.error(request, 'Los datos no son válidos, ingresa una contraseña correcta')
        else:
            messages.error(request, 'La contraseña no coincide con la confirmación')

    return render(request, 'accounts/change_password.html')
