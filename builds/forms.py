# builds/forms.py
from django import forms

class AddToCartForm(forms.Form):
    """Форма для добавления товара в корзину."""
    component_type = forms.ChoiceField(
        choices=[
            ('cpu', 'Процессор'),
            ('gpu', 'Видеокарта'),
            ('motherboard', 'Материнская плата'),
            ('ram', 'Оперативная память'),
            ('storage', 'Накопитель'),
            ('psu', 'Блок питания'),
            ('case', 'Корпус'),
            ('cooler', 'Охлаждение'),  # Добавлено
            ('build', 'Сборка'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Тип компонента"
    )
    component_id = forms.IntegerField(widget=forms.HiddenInput())  # ID компонента или сборки
    quantity = forms.IntegerField(min_value=1, initial=1, widget=forms.NumberInput(attrs={'class': 'form-control'}), label="Количество")
    