# components/admin.py

from django.contrib import admin
from .models import Manufacturer, CPU, Motherboard, RAM, GPU, Storage, PSU, Case
from .forms import CPUForm, GPUForm, MotherboardForm, RAMForm, StorageForm, PSUForm, CaseForm #Импортируйте другие формы

@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'component_type')  # Поля, которые будут отображаться в списке
    search_fields = ('name',)  # Поля, по которым можно искать
    list_filter = ('component_type',)

@admin.register(CPU)
class CPUAdmin(admin.ModelAdmin):
    list_display = ('manufacturer', 'model', 'cores', 'frequency', 'price', 'image')  # Добавлено 'image'
    list_filter = ('manufacturer',)  # Фильтры
    search_fields = ('model', 'manufacturer__name')  # Поля, по которым можно искать
    ordering = ('manufacturer', 'model')  # Сортировка
    form = CPUForm

@admin.register(GPU)
class GPUAdmin(admin.ModelAdmin):
    list_display = ('manufacturer', 'model', 'memory', 'frequency', 'tdp', 'price', 'image') # Добавлено 'image'
    list_filter = ('manufacturer',)
    search_fields = ('model', 'manufacturer__name')
    ordering = ('manufacturer', 'model')
    form = GPUForm

@admin.register(Motherboard)
class MotherboardAdmin(admin.ModelAdmin):
    list_display = ('manufacturer', 'model', 'form_factor', 'socket', 'chipset', 'price', 'image') # Добавлено 'image'
    list_filter = ('manufacturer', 'form_factor', 'socket', 'chipset')
    search_fields = ('model', 'manufacturer__name', 'socket', 'chipset')
    ordering = ('manufacturer', 'model')
    form = MotherboardForm

@admin.register(RAM)
class RAMAdmin(admin.ModelAdmin):
    list_display = ('manufacturer', 'model', 'capacity', 'frequency', 'type', 'price', 'image') # Добавлено 'image'
    list_filter = ('manufacturer', 'type')
    search_fields = ('model', 'manufacturer__name', 'type')
    ordering = ('manufacturer', 'model')
    form = RAMForm

@admin.register(Storage)
class StorageAdmin(admin.ModelAdmin):
    list_display = ('manufacturer', 'model', 'capacity', 'type', 'interface', 'price', 'image') # Добавлено 'image'
    list_filter = ('manufacturer', 'type', 'interface')
    search_fields = ('model', 'manufacturer__name', 'type', 'interface')
    ordering = ('manufacturer', 'model')
    form = StorageForm

@admin.register(PSU)
class PSUAdmin(admin.ModelAdmin):
    list_display = ('manufacturer', 'model', 'power', 'certification', 'price', 'image') # Добавлено 'image'
    list_filter = ('manufacturer', 'certification')
    search_fields = ('model', 'manufacturer__name', 'certification')
    ordering = ('manufacturer', 'model')
    form = PSUForm

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('manufacturer', 'model', 'form_factor', 'dimensions', 'price', 'image') # Добавлено 'image'
    list_filter = ('manufacturer', 'form_factor')
    search_fields = ('model', 'manufacturer__name', 'form_factor')
    ordering = ('manufacturer', 'model')
    form = CaseForm