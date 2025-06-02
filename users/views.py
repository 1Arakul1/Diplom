# users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model  # Получаем модель User
from django.utils.encoding import force_str  # Удаляем это
from django.utils.http import urlsafe_base64_decode  # Удаляем это
from django.contrib.auth.tokens import default_token_generator  # Удаляем это
from builds.models import Build, CartItem # <--- Добавьте этот импорт
from .utils import send_registration_email  # Импортируем функцию отправки письма
from django.contrib.auth import authenticate, login # Импорт для логина
from .forms import CustomUserCreationForm # Импортируем пользовательскую форму
from .utils import send_registration_email  # Импортируем функцию отправки письма

@login_required
def profile(request):
    """Профиль пользователя."""
    user = request.user
    builds = Build.objects.filter(user=user)
    cart_items = CartItem.objects.filter(user=user)
    context = {
        'user': user,
        'builds': builds,
        'cart_items': cart_items,
    }
    return render(request, 'users/profile.html', context)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            try:
                send_registration_email(user)  # Отправляем письмо с информацией
                username = form.cleaned_data.get('username')
                messages.success(request, f'Аккаунт создан для {username}! Письмо с информацией отправлено на вашу почту.')
                return redirect('users:login')
            except Exception as e:
                messages.error(request, f'Не удалось отправить письмо. Пожалуйста, свяжитесь с администрацией.')
                print(f"Error sending registration email: {e}")
                user.delete()
                return render(request, 'users/register.html', {'form': form})
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

# Удаляем view подтверждения, т.к. оно больше не нужно
#def confirm_email(request, uidb64, token):
#    pass