# builds/models.py
from django.db import models
from django.contrib.auth.models import User
from components.models import CPU, GPU, Motherboard, RAM, Storage, PSU, Case, Cooler  # Импортируем Cooler
from django.contrib import admin


class Build(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    cpu = models.ForeignKey(CPU, on_delete=models.SET_NULL, verbose_name="CPU", blank=True, null=True)
    gpu = models.ForeignKey(GPU, on_delete=models.SET_NULL, verbose_name="GPU", blank=True, null=True)
    motherboard = models.ForeignKey(Motherboard, on_delete=models.SET_NULL, verbose_name="Motherboard", blank=True, null=True)
    ram = models.ForeignKey(RAM, on_delete=models.SET_NULL, verbose_name="RAM", blank=True, null=True)
    storage = models.ForeignKey(Storage, on_delete=models.SET_NULL, verbose_name="Storage", blank=True, null=True)
    psu = models.ForeignKey(PSU, on_delete=models.SET_NULL, verbose_name="PSU", blank=True, null=True)
    case = models.ForeignKey(Case, on_delete=models.SET_NULL, verbose_name="Case", blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Общая стоимость", blank=True, null=True)
    cooler = models.ForeignKey(Cooler, on_delete=models.SET_NULL, verbose_name="Охлаждение", blank=True, null=True, related_name='builds')  # Добавляем поле cooler
    # ... (остальные поля)

    def __str__(self):
        return f"Сборка {self.pk} - {self.cpu.model if self.cpu else 'Без CPU'}"

    @admin.display(description='Общая стоимость')  # <---- Добавляем admin.display
    def get_total_price(self):
        """Вычисляет общую стоимость сборки."""
        price = 0
        if self.cpu:
            price += self.cpu.price
        if self.gpu:
            price += self.gpu.price
        if self.motherboard:
            price += self.motherboard.price
        if self.ram:
            price += self.ram.price
        if self.storage:
            price += self.storage.price
        if self.psu:
            price += self.psu.price
        if self.case:
            price += self.case.price
        if self.cooler:
            price += self.cooler.price
        return price

class Meta:
        verbose_name = "Сборка"
        verbose_name_plural = "Сборки"

class CartItem(models.Model):
    """Элемент в корзине."""
    build = models.ForeignKey(Build, null=True, blank=True, on_delete=models.CASCADE)
    item_type = models.CharField(max_length=50)  # например
    quantity = models.PositiveIntegerField(default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    cpu = models.ForeignKey(CPU, on_delete=models.CASCADE, verbose_name="Процессор", blank=True, null=True)
    gpu = models.ForeignKey(GPU, on_delete=models.CASCADE, verbose_name="Видеокарта", blank=True, null=True)
    motherboard = models.ForeignKey(Motherboard, on_delete=models.CASCADE, verbose_name="Материнская плата", blank=True, null=True)
    ram = models.ForeignKey(RAM, on_delete=models.CASCADE, verbose_name="Оперативная память", blank=True, null=True)
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE, verbose_name="Накопитель", blank=True, null=True)
    psu = models.ForeignKey(PSU, on_delete=models.CASCADE, verbose_name="Блок питания", blank=True, null=True)
    case = models.ForeignKey(Case, on_delete=models.CASCADE, verbose_name="Корпус", blank=True, null=True)
    cooler = models.ForeignKey(Cooler, on_delete=models.CASCADE, verbose_name="Охлаждение", blank=True, null=True) # Добавлено поле cooler
    build = models.ForeignKey(Build, on_delete=models.CASCADE, verbose_name="Сборка", blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    def __str__(self):
        if self.build:
            return f"Сборка {self.build.pk} в корзине для {self.user.username}"
        elif self.cpu:
            return f"CPU {self.cpu.manufacturer} {self.cpu.model} для {self.user.username}"
        elif self.gpu:
            return f"GPU {self.gpu.manufacturer} {self.gpu.model} для {self.user.username}"
        elif self.motherboard:
            return f"Motherboard {self.motherboard.manufacturer} {self.motherboard.model} для {self.user.username}"
        elif self.ram:
            return f"RAM {self.ram.manufacturer} {self.ram.model} для {self.user.username}"
        elif self.storage:
            return f"Storage {self.storage.manufacturer} {self.storage.model} для {self.user.username}"
        elif self.psu:
            return f"PSU {self.psu.manufacturer} {self.psu.model} для {self.user.username}"
        elif self.case:
            return f"Case {self.case.manufacturer} {self.case.model} для {self.user.username}"
        elif self.cooler:
            return f"Cooler {self.cooler.manufacturer} {self.cooler.model} для {self.user.username}" # Добавлено отображение cooler
        else:
            return f"Неизвестный товар в корзине для {self.user.username}"

    def get_total_price(self):
        """Вычисляет общую стоимость элемента корзины."""
        price = 0
        if self.build:
            price = self.build.total_price * self.quantity  # Используем total_price сборки и умножаем на quantity
        elif self.cpu:
            price = self.cpu.price
        elif self.gpu:
            price = self.gpu.price
        elif self.motherboard:
            price = self.motherboard.price
        elif self.ram:
            price = self.ram.price
        elif self.storage:
            price = self.storage.price
        elif self.psu:
            price = self.psu.price
        elif self.case:
            price = self.case.price
        elif self.cooler:
            price = self.cooler.price # Добавляем цену кулера
        return price * self.quantity  # умножаем на количество

    class Meta:
        verbose_name = "Элемент корзины"
        verbose_name_plural = "Элементы корзины"