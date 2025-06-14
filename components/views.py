#components\views.py
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import CPU, GPU, Motherboard, RAM, Storage, PSU, Case, Manufacturer  # Убедитесь, что импортированы все модели
from django.db.models import Q
from django import forms
from .models import Cooler, CPU, Manufacturer # Импортируйте модель Cooler
from django.core.cache import cache


# --- Forms ---
class ComponentSearchForm(forms.Form): #Базовая форма для поиска (можно сделать для каждого компонента, расширяя этот класс)
    q = forms.CharField(label="Поиск", required=False)


# --- CPU Views ---
def cpu_list(request):
    form = ComponentSearchForm(request.GET)
    query = ''
    cpus_list = CPU.objects.all()

    if form.is_valid():
        query = form.cleaned_data['q']
        if query:
            cpus_list = cpus_list.filter(
                Q(manufacturer__name__icontains=query) | Q(model__icontains=query)
            ).distinct()

    paginator = Paginator(cpus_list, 6)
    page = request.GET.get('page')
    try:
        cpus = paginator.page(page)
    except PageNotAnInteger:
        cpus = paginator.page(1)
    except EmptyPage:
        cpus = paginator.page(paginator.num_pages)

    return render(request, 'components/cpu_list.html', {'cpus': cpus, 'form': form, 'query': query})


def cpu_detail(request, pk):
    cpu = get_object_or_404(CPU, pk=pk)
    return render(request, 'components/cpu_detail.html', {'cpu': cpu})


# --- GPU Views ---
def gpu_list(request):
    form = ComponentSearchForm(request.GET) #Используем ту же базовую форму для поиска
    query = ''
    gpus_list = GPU.objects.all()

    if form.is_valid():
        query = form.cleaned_data['q']
        if query:
            gpus_list = gpus_list.filter(
                Q(manufacturer__name__icontains=query) | Q(model__icontains=query)
            ).distinct()

    paginator = Paginator(gpus_list, 6)
    page = request.GET.get('page')
    try:
        gpus = paginator.page(page)
    except PageNotAnInteger:
        gpus = paginator.page(1)
    except EmptyPage:
        gpus = paginator.page(paginator.num_pages)

    return render(request, 'components/gpu_list.html', {'gpus': gpus, 'form': form, 'query': query})


def gpu_detail(request, pk):
    gpu = get_object_or_404(GPU, pk=pk)
    return render(request, 'components/gpu_detail.html', {'gpu': gpu})


# --- Motherboard Views ---
def motherboard_list(request):
    form = ComponentSearchForm(request.GET)
    query = ''
    motherboards_list = Motherboard.objects.all()

    if form.is_valid():
        query = form.cleaned_data['q']
        if query:
            motherboards_list = motherboards_list.filter(
                Q(manufacturer__name__icontains=query) | Q(model__icontains=query)
            ).distinct()

    paginator = Paginator(motherboards_list, 6)
    page = request.GET.get('page')
    try:
        motherboards = paginator.page(page)
    except PageNotAnInteger:
        motherboards = paginator.page(1)
    except EmptyPage:
        motherboards = paginator.page(paginator.num_pages)

    return render(request, 'components/motherboard_list.html', {'motherboards': motherboards, 'form': form, 'query': query})


def motherboard_detail(request, pk):
    motherboard = get_object_or_404(Motherboard, pk=pk)
    return render(request, 'components/motherboard_detail.html', {'motherboard': motherboard})


# --- RAM Views ---
def ram_list(request):
    form = ComponentSearchForm(request.GET)
    query = ''
    rams_list = RAM.objects.all()

    if form.is_valid():
        query = form.cleaned_data['q']
        if query:
            rams_list = rams_list.filter(
                Q(manufacturer__name__icontains=query) | Q(model__icontains=query)
            ).distinct()

    paginator = Paginator(rams_list, 6)
    page = request.GET.get('page')
    try:
        rams = paginator.page(page)
    except PageNotAnInteger:
        rams = paginator.page(1)
    except EmptyPage:
        rams = paginator.page(paginator.num_pages)

    return render(request, 'components/ram_list.html', {'rams': rams, 'form': form, 'query': query})


def ram_detail(request, pk):
    ram = get_object_or_404(RAM, pk=pk)
    return render(request, 'components/ram_detail.html', {'ram': ram})


# --- Storage Views ---
def storage_list(request):
    form = ComponentSearchForm(request.GET)
    query = ''
    storages_list = Storage.objects.all()

    if form.is_valid():
        query = form.cleaned_data['q']
        if query:
            storages_list = storages_list.filter(
                Q(manufacturer__name__icontains=query) | Q(model__icontains=query)
            ).distinct()

    paginator = Paginator(storages_list, 6)
    page = request.GET.get('page')
    try:
        storages = paginator.page(page)
    except PageNotAnInteger:
        storages = paginator.page(1)
    except EmptyPage:
        storages = paginator.page(paginator.num_pages)

    return render(request, 'components/storage_list.html', {'storages': storages, 'form': form, 'query': query})


def storage_detail(request, pk):
    storage = get_object_or_404(Storage, pk=pk)
    return render(request, 'components/storage_detail.html', {'storage': storage})


# --- PSU Views ---
def psu_list(request):
    form = ComponentSearchForm(request.GET)
    query = ''
    psus_list = PSU.objects.all()

    if form.is_valid():
        query = form.cleaned_data['q']
        if query:
            psus_list = psus_list.filter(
                Q(manufacturer__name__icontains=query) | Q(model__icontains=query)
            ).distinct()

    paginator = Paginator(psus_list, 6)
    page = request.GET.get('page')
    try:
        psus = paginator.page(page)
    except PageNotAnInteger:
        psus = paginator.page(1)
    except EmptyPage:
        psus = paginator.page(paginator.num_pages)

    return render(request, 'components/psu_list.html', {'psus': psus, 'form': form, 'query': query})


def psu_detail(request, pk):
    psu = get_object_or_404(PSU, pk=pk)
    return render(request, 'components/psu_detail.html', {'psu': psu})


# --- Case Views ---
def case_list(request):
    form = ComponentSearchForm(request.GET)
    query = ''
    cases_list = Case.objects.all()

    if form.is_valid():
        query = form.cleaned_data['q']
        if query:
            cases_list = cases_list.filter(
                Q(manufacturer__name__icontains=query) | Q(model__icontains=query)
            ).distinct()

    paginator = Paginator(cases_list, 6)
    page = request.GET.get('page')
    try:
        cases = paginator.page(page)
    except PageNotAnInteger:
        cases = paginator.page(1)
    except EmptyPage:
        cases = paginator.page(paginator.num_pages)

    return render(request, 'components/case_list.html', {'cases': cases, 'form': form, 'query': query})


def case_detail(request, pk):
    case = get_object_or_404(Case, pk=pk)
    return render(request, 'components/case_detail.html', {'case': case})

# --- Cooler Views ---
def cooler_list(request):
    form = ComponentSearchForm(request.GET)
    query = ''
    coolers_list = Cooler.objects.all()  # Получаем все кулеры

    if form.is_valid():
        query = form.cleaned_data['q']
        if query:
            coolers_list = coolers_list.filter(
                Q(manufacturer__name__icontains=query) | Q(model__icontains=query)
            ).distinct()

    # Пагинация (если нужна)
    paginator = Paginator(coolers_list, 6)
    page = request.GET.get('page')
    try:
        coolers = paginator.page(page)
    except PageNotAnInteger:
        coolers = paginator.page(1)
    except EmptyPage:
        coolers = paginator.page(paginator.num_pages)

    return render(request, 'components/cooler_list.html', {'coolers': coolers, 'form': form, 'query': query})

def cooler_detail(request, pk):
    cooler = get_object_or_404(Cooler, pk=pk)
    return render(request, 'components/cooler_detail.html', {'cooler': cooler})