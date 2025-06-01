# app: builds
from django.db import models
from django.contrib.auth.models import User #Импорт модели User
class Build(models.Model): # Если нужна функция сохранения сборок
    """Сборка компьютера."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь") # Если есть регистрация
    cpu = models.ForeignKey("components.CPU", on_delete=models.CASCADE, verbose_name="Процессор")
    motherboard = models.ForeignKey("components.Motherboard", on_delete=models.CASCADE, verbose_name="Материнская плата")
    ram = models.ForeignKey("components.RAM", on_delete=models.CASCADE, verbose_name="Оперативная память")
    gpu = models.ForeignKey("components.GPU", on_delete=models.CASCADE, verbose_name="Видеокарта")
    storage = models.ForeignKey("components.Storage", on_delete=models.CASCADE, verbose_name="Накопитель")
    psu = models.ForeignKey("components.PSU", on_delete=models.CASCADE, verbose_name="Блок питания")
    case = models.ForeignKey("components.Case", on_delete=models.CASCADE, verbose_name="Корпус")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Общая стоимость")
    # ... другие поля, например дата создания

    def __str__(self):
        return f"Сборка {self.pk}" # Или какое-то более информативное название

    class Meta:
        verbose_name = "Сборка"
        verbose_name_plural = "Сборки"