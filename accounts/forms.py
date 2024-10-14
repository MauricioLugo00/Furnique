from django import forms
from .models import Accounts, UserProfile


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Ingrese Contraseña',
    }), help_text='La contraseña debe tener al menos 8 caracteres.')

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirmar Contraseña',
    }), help_text='Confirme la contraseña anterior.')

    class Meta:
        model = Accounts
        fields = ['first_name', 'last_name', 'username', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Ingrese su nombre'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Ingrese sus apellidos'
        self.fields['username'].widget.attrs['placeholder'] = 'Ingrese su nombre de usuario'
        self.fields['email'].widget.attrs['placeholder'] = 'Ingrese su email'

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                'Las contraseñas no coinciden. Por favor, verifique su información.'
            )

        if len(password) < 8:
            raise forms.ValidationError('La contraseña debe tener al menos 8 caracteres.')


class UserForm(forms.ModelForm):
    class Meta:
        model = Accounts
        fields = ('first_name', 'last_name', 'phone_number', 'email')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Accounts.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError('Este email ya está en uso. Elige otro.')
        return email


class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(
        required=False, 
        error_messages={'invalid': 'Solo se permiten archivos de imagen.'}, 
        widget=forms.FileInput()
    )

    class Meta:
        model = UserProfile
        fields = ('address_line_1', 'address_line_2', 'city', 'state', 'country', 'profile_picture')

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)

    def clean_profile_picture(self):
        picture = self.cleaned_data.get('profile_picture')
        if picture:
            if not picture.name.endswith(('.png', '.jpg', '.jpeg')):
                raise forms.ValidationError('Por favor, sube una imagen en formato PNG o JPEG.')
        return picture
