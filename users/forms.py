# users/forms.py  (Создайте этот файл, если его нет)
from django import forms
from django.contrib.auth.forms import UserCreationForm, UsernameField  # Импортируйте UsernameField
from django.core.validators import validate_email  # Для валидации email

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(label="Email", required=True, validators=[validate_email])  # Добавляем поле email

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)  # Добавляем email в fields

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Проверка уникальности email (опционально, но рекомендуется)
            from django.contrib.auth import get_user_model  # Импортируем get_user_model
            User = get_user_model()
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("Пользователь с таким адресом электронной почты уже существует.")
        return email