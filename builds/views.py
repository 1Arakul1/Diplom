# builds/views.py
# builds/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Build, CartItem
from components.models import CPU, GPU, Motherboard, RAM, Storage, PSU, Case
from .forms import AddToCartForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages  # Import messages
from django.http import JsonResponse  # Импортируем JsonResponse
from components.forms import CPUForm, GPUForm, MotherboardForm, RAMForm, StorageForm, PSUForm, CaseForm # Импортируем формы компонентов

# --- Вспомогательная функция для получения cart_items и total_price (переиспользуемая) ---
def get_cart_context(request):
    """Получает контекст корзины для авторизованных пользователей."""
    cart_items = []
    total_price = 0
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
        for item in cart_items:
            total_price += item.get_total_price()
    return {'cart_items': cart_items, 'total_price': total_price}

@login_required
def cart_view(request):
    """Просмотр корзины."""
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.get_total_price() for item in cart_items)
    return render(request, 'builds/cart.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required
def add_to_cart(request):
    """Добавление товара в корзину."""
    if request.method == 'POST':
        print("POST data:", request.POST)
        print("Is form bound?", AddToCartForm(request.POST).is_bound)
        form = AddToCartForm(request.POST)
        if form.is_valid():
            print("Form is valid")
            component_type = form.cleaned_data['component_type']
            component_id = form.cleaned_data['component_id']
            quantity = form.cleaned_data['quantity']

            print(f"Component Type: {component_type}, ID: {component_id}, Quantity: {quantity}")

            component_mapping = {
                'cpu': CPU,
                'gpu': GPU,
                'motherboard': Motherboard,
                'ram': RAM,
                'storage': Storage,
                'psu': PSU,
                'case': Case,
                'build': Build,
            }

            if component_type not in component_mapping:
                return JsonResponse({'status': 'error', 'message': 'Неверный тип компонента.'})

            model = component_mapping[component_type]

            try:
                component = get_object_or_404(model, pk=component_id)
            except (ValueError, TypeError):
                return JsonResponse({'status': 'error', 'message': 'Неверный ID компонента.'})

            # Получаем или создаем CartItem.  Используем фильтрацию по типу и ID компонента.
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                **{component_type: component},
                defaults={'quantity': 0}
            )
            print(f"Cart item created/updated: {cart_item.__dict__}")

            # Если элемент уже существует (не created), увеличиваем quantity
            if not created:
                cart_item.quantity += quantity
            else: # Если создан - устанавливаем quantity
                 cart_item.quantity = quantity

            cart_item.save()
            print(f"Cart item created/updated: {cart_item.__dict__}")
            return redirect('builds:cart')

        else:
            print("Form is not valid")
            print(form.errors)
            return JsonResponse({'status': 'error', 'message': 'Ошибка валидации формы.'})

    else:
        return JsonResponse({'status': 'error', 'message': 'Неверный метод запроса.'})

@login_required
def remove_from_cart(request, item_id):
    """Удаление товара из корзины."""
    cart_item = get_object_or_404(CartItem, pk=item_id, user=request.user)
    cart_item.delete()
    return redirect('builds:cart') # Перенаправляем на корзину

# -----------------  Остальной код views.py ----------------------
def build_list(request):
    builds_list = Build.objects.all().order_by('id')
    paginator = Paginator(builds_list, 6)
    page = request.GET.get('page')

    try:
        builds = paginator.page(page)
    except PageNotAnInteger:
        builds = paginator.page(1)
    except EmptyPage:
        builds = paginator.page(paginator.num_pages)

    # --- Получаем контекст корзины ---
    cart_context = get_cart_context(request)
    # --- Добавляем в контекст шаблона ---
    context = {
        'builds': builds,
        **cart_context, # Распаковываем cart_context (cart_items, total_price)
    }
    return render(request, 'builds/build_list.html', context)

def build_detail(request, pk):
    build = get_object_or_404(Build, pk=pk)
    cart_context = get_cart_context(request)  # добавляем корзину в контекст
    context = {
        'build': build,
        **cart_context  # Распаковываем cart_context (cart_items, total_price)
    }
    return render(request, 'builds/build_detail.html', context)

def build_create(request):
    if request.method == 'POST':
        # Обработка формы создания сборки
        cpu_id = request.POST.get('cpu')
        gpu_id = request.POST.get('gpu')
        motherboard_id = request.POST.get('motherboard')
        ram_id = request.POST.get('ram')
        storage_id = request.POST.get('storage')
        psu_id = request.POST.get('psu')
        case_id = request.POST.get('case')

        # Получаем компоненты, обрабатывая ошибки
        try:
            cpu = get_object_or_404(CPU, pk=cpu_id)
            gpu = get_object_or_404(GPU, pk=gpu_id)
            motherboard = get_object_or_404(Motherboard, pk=motherboard_id)
            ram = get_object_or_404(RAM, pk=ram_id)
            storage = get_object_or_404(Storage, pk=storage_id)
            psu = get_object_or_404(PSU, pk=psu_id)
            case = get_object_or_404(Case, pk=case_id)
        except (ValueError, TypeError):
            return render(request, 'builds/build_create.html',
                          {'error_message': 'Неверный формат ID компонента.',
                           'cpus': CPU.objects.all(), 'gpus': GPU.objects.all(),
                           'motherboards': Motherboard.objects.all(), 'rams': RAM.objects.all(),
                           'storages': Storage.objects.all(), 'psus': PSU.objects.all(),
                           'cases': Case.objects.all()})

        # Рассчитываем общую стоимость
        total_price = 0
        if cpu:
            total_price += cpu.price
        if gpu:
            total_price += gpu.price
        if motherboard:
            total_price += motherboard.price
        if ram:
            total_price += ram.price
        if storage:
            total_price += storage.price
        if psu:
            total_price += psu.price
        if case:
            total_price += case.price

        build = Build(
            user=request.user,
            cpu=cpu,
            gpu=gpu,
            motherboard=motherboard,
            ram=ram,
            storage=storage,
            psu=psu,
            case=case,
            total_price=total_price
        )
        build.save()
        return redirect('builds:build_detail', pk=build.pk)

    else:
        cpus = CPU.objects.all()
        gpus = GPU.objects.all()
        motherboards = Motherboard.objects.all()
        rams = RAM.objects.all()
        storages = Storage.objects.all()
        psus = PSU.objects.all()
        cases = Case.objects.all()
        context = {'cpus': cpus, 'gpus': gpus, 'motherboards': motherboards, 'rams': rams, 'storages': storages, 'psus': psus, 'cases': cases}
        return render(request, 'builds/build_create.html', context)

def build_edit(request, pk):
    build = get_object_or_404(Build, pk=pk)

    if request.method == 'POST':
        # Обработка формы редактирования
        # Получите данные из POST, создайте формы для каждого компонента и валидируйте их.
        # Сохраните изменения в сборке.
        cpu_id = request.POST.get('cpu')
        gpu_id = request.POST.get('gpu')
        motherboard_id = request.POST.get('motherboard')
        ram_id = request.POST.get('ram')
        storage_id = request.POST.get('storage')
        psu_id = request.POST.get('psu')
        case_id = request.POST.get('case')

        # Получаем компоненты, обрабатывая ошибки
        try:
            cpu = CPU.objects.get(pk=cpu_id) if cpu_id else None
            gpu = GPU.objects.get(pk=gpu_id) if gpu_id else None
            motherboard = Motherboard.objects.get(pk=motherboard_id) if motherboard_id else None
            ram = RAM.objects.get(pk=ram_id) if ram_id else None
            storage = Storage.objects.get(pk=storage_id) if storage_id else None
            psu = PSU.objects.get(pk=psu_id) if psu_id else None
            case = Case.objects.get(pk=case_id) if case_id else None
        except (CPU.DoesNotExist, GPU.DoesNotExist, Motherboard.DoesNotExist, RAM.DoesNotExist, Storage.DoesNotExist, PSU.DoesNotExist, Case.DoesNotExist):
            # Обработка ошибок, если компонент не найден.
            return render(request, 'builds/build_edit.html', {
                'build': build,
                'error_message': 'Один из выбранных компонентов не найден.',
                'cpus': CPU.objects.all(),
                'gpus': GPU.objects.all(),
                'motherboards': Motherboard.objects.all(),
                'rams': RAM.objects.all(),
                'storages': Storage.objects.all(),
                'psus': PSU.objects.all(),
                'cases': Case.objects.all(),
            })

        #  Обновление полей build
        build.cpu = cpu
        build.gpu = gpu
        build.motherboard = motherboard
        build.ram = ram
        build.storage = storage
        build.psu = psu
        build.case = case

        # Рассчитываем общую стоимость
        total_price = 0
        if build.cpu:
            total_price += build.cpu.price
        if build.gpu:
            total_price += build.gpu.price
        if build.motherboard:
            total_price += build.motherboard.price
        if build.ram:
            total_price += build.ram.price
        if build.storage:
            total_price += build.storage.price
        if build.psu:
            total_price += build.psu.price
        if build.case:
            total_price += build.case.price
        build.total_price = total_price

        build.save()
        return redirect('builds:build_detail', pk=build.pk)
    else:
        # Отобразите форму с текущими значениями
        cpus = CPU.objects.all()
        gpus = GPU.objects.all()
        motherboards = Motherboard.objects.all()
        rams = RAM.objects.all()
        storages = Storage.objects.all()
        psus = PSU.objects.all()
        cases = Case.objects.all()

        context = {
            'build': build,
            'cpus': cpus,
            'gpus': gpus,
            'motherboards': motherboards,
            'rams': rams,
            'storages': storages,
            'psus': psus,
            'cases': cases,
        }
        return render(request, 'builds/build_edit.html', context)
@login_required
def checkout(request):
    """Оформление заказа."""
    # Здесь будет логика оформления заказа.
    #  Например:
    #  1. Получить товары из корзины.
    #  2. Рассчитать общую стоимость.
    #  3. Создать заказ в базе данных.
    #  4. Обработать оплату (если необходимо).
    #  5. Очистить корзину.
    #  6. Перенаправить пользователя на страницу подтверждения заказа.

    return render(request, 'builds/checkout.html', {})  # Замените на ваш шаблон
