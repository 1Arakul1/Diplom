# app: components
# components/models.py
from django.db import models

class Manufacturer(models.Model):
    """Производитель компонентов."""
    name = models.CharField(max_length=255, verbose_name="Название")
    component_type = models.CharField(
        max_length=50,
        choices=[
            ('cpu', 'Процессор'),
            ('gpu', 'Видеокарта'),
            ('motherboard', 'Материнская плата'),
            ('ram', 'Оперативная память'),
            ('storage', 'Накопитель'),
            ('psu', 'Блок питания'),
            ('case', 'Корпус'),
        ],
        verbose_name="Тип компонента",
        blank=True,  # Может быть пустым (для общих производителей)
        null=True,  # Может быть None (для общих производителей)
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Производитель"
        verbose_name_plural = "Производители"

class CPU(models.Model):
    """Процессор."""
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, verbose_name="Производитель")
    model = models.CharField(max_length=255, verbose_name="Модель")
    cores = models.IntegerField(verbose_name="Количество ядер")
    frequency = models.FloatField(verbose_name="Частота (ГГц)")
    tdp = models.IntegerField(verbose_name="TDP (Вт)")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    socket = models.CharField(max_length=50, verbose_name="Сокет")  # Добавлено поле сокета
    image = models.ImageField(upload_to='cpu_images/', verbose_name="Изображение", blank=True, null=True) # Добавлено поле изображения

    def __str__(self):
        return f"{self.manufacturer} {self.model}"

    class Meta:
        verbose_name = "Процессор"
        verbose_name_plural = "Процессоры"

class Motherboard(models.Model):
    """Материнская плата."""
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, verbose_name="Производитель")
    model = models.CharField(max_length=255, verbose_name="Модель")
    form_factor = models.CharField(max_length=50, verbose_name="Форм-фактор")
    socket = models.CharField(max_length=50, verbose_name="Сокет")  # Сокет процессора
    chipset = models.CharField(max_length=50, verbose_name="Чипсет")
    ram_slots = models.IntegerField(verbose_name="Слоты для RAM")
    ram_type = models.CharField(max_length=10, verbose_name="Тип RAM (DDR4, DDR5)")
    max_ram_frequency = models.IntegerField(verbose_name="Максимальная частота RAM")
    expansion_slots = models.TextField(verbose_name="Слоты расширения")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(upload_to='motherboard_images/', verbose_name="Изображение", blank=True, null=True) # Добавлено поле изображения

    def __str__(self):
        return f"{self.manufacturer} {self.model}"

    class Meta:
        verbose_name = "Материнская плата"
        verbose_name_plural = "Материнские платы"

class RAM(models.Model):
    """Оперативная память."""
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, verbose_name="Производитель")
    model = models.CharField(max_length=255, verbose_name="Модель")
    capacity = models.IntegerField(verbose_name="Объем (ГБ)")
    frequency = models.IntegerField(verbose_name="Частота (МГц)")
    type = models.CharField(max_length=10, verbose_name="Тип (DDR4, DDR5)")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(upload_to='ram_images/', verbose_name="Изображение", blank=True, null=True) # Добавлено поле изображения

    def __str__(self):
        return f"{self.manufacturer} {self.model}"

    class Meta:
        verbose_name = "Оперативная память"
        verbose_name_plural = "Оперативная память"

class GPU(models.Model):
    """Видеокарта."""
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, verbose_name="Производитель")
    model = models.CharField(max_length=255, verbose_name="Модель")
    memory = models.IntegerField(verbose_name="Объем памяти (ГБ)")
    frequency = models.FloatField(verbose_name="Частота (ГГц)") #Частота ядра
    tdp = models.IntegerField(verbose_name="TDP (Вт)")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(upload_to='gpu_images/', verbose_name="Изображение", blank=True, null=True) # Добавлено поле изображения

    def __str__(self):
        return f"{self.manufacturer} {self.model}"

    class Meta:
        verbose_name = "Видеокарта"
        verbose_name_plural = "Видеокарты"

class Storage(models.Model):
    """Накопитель (SSD/HDD)."""
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, verbose_name="Производитель")
    model = models.CharField(max_length=255, verbose_name="Модель")
    capacity = models.IntegerField(verbose_name="Объем (ГБ/ТБ)")
    type = models.CharField(max_length=10, verbose_name="Тип (SSD/HDD)")
    interface = models.CharField(max_length=50, verbose_name="Интерфейс")
    read_speed = models.IntegerField(verbose_name="Скорость чтения (МБ/с)")
    write_speed = models.IntegerField(verbose_name="Скорость записи (МБ/с)")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(upload_to='storage_images/', verbose_name="Изображение", blank=True, null=True) # Добавлено поле изображения

    def __str__(self):
        return f"{self.manufacturer} {self.model}"

    class Meta:
        verbose_name = "Накопитель"
        verbose_name_plural = "Накопители"

class PSU(models.Model):
    """Блок питания."""
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, verbose_name="Производитель")
    model = models.CharField(max_length=255, verbose_name="Модель")
    power = models.IntegerField(verbose_name="Мощность (Вт)")
    certification = models.CharField(max_length=50, verbose_name="Сертификация")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(upload_to='psu_images/', verbose_name="Изображение", blank=True, null=True) # Добавлено поле изображения

    def __str__(self):
        return f"{self.manufacturer} {self.model}"

    class Meta:
        verbose_name = "Блок питания"
        verbose_name_plural = "Блоки питания"

class Case(models.Model):
    """Корпус."""
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, verbose_name="Производитель")
    model = models.CharField(max_length=255, verbose_name="Модель")
    form_factor = models.CharField(max_length=50, verbose_name="Форм-фактор")
    dimensions = models.CharField(max_length=50, verbose_name="Размеры")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(upload_to='case_images/', verbose_name="Изображение", blank=True, null=True) # Добавлено поле изображения

    def __str__(self):
        return f"{self.manufacturer} {self.model}"

    class Meta:
        verbose_name = "Корпус"
        verbose_name_plural = "Корпуса"
