from decimal import Decimal
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST
from django.db.models import Q, F
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404
from django.contrib import messages
import logging
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from .models import Build, CartItem, Order, OrderItem
from components.models import CPU, GPU, Motherboard, RAM, Storage, PSU, Case, Cooler
from .forms import AddToCartForm, OrderUpdateForm
from django.contrib import messages
from django.db import transaction  # Import transaction
from django.contrib.sessions.models import Session

logger = logging.getLogger(__name__)

class VaryCookieMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Vary'] = 'Cookie'
        logger.info("VaryCookieMiddleware is running!")
        return response


# --- Вспомогательная функция для получения cart_items и total_price (переиспользуемая) ---
def get_cart_context(request):
    """Получает контекст корзины для авторизованных пользователей."""
    cart_items = []
    total_price = Decimal('0.0')
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
        for item in cart_items:
            total_price += item.get_total_price()
    return {'cart_items': cart_items, 'total_price': total_price}


@login_required
def cart_view(request):
    """Просмотр корзины."""
    logger.info(f"User in cart_view: {request.user}")
    print(f"Cart items in cart_view: {CartItem.objects.filter(user=request.user)}")

    # Получаем текущую сессию, блокируя ее для обновления
    try:
        with transaction.atomic():
            session = Session.objects.select_for_update().get(session_key=request.session.session_key)
            cart_items = CartItem.objects.filter(user=request.user)
            total_price = sum(item.get_total_price() for item in cart_items)
            context = {'cart_items': cart_items, 'total_price': total_price}
            response = render(request, 'builds/cart.html', context)  # Сохраняем response
            response['Cache-Control'] = 'private, no-cache, no-store, must-revalidate'  # Добавляем заголовки
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            return response # Возвращаем response
    except Session.DoesNotExist:
        context = {'cart_items': [], 'total_price': 0}
        return render(request, 'builds/cart.html', context)


@login_required
@require_POST
def add_to_cart(request):
    with transaction.atomic():
        logger.info(f"User in add_to_cart: {request.user}")
        """Добавляет товар в корзину пользователя."""
        component_type = request.POST.get('component_type')
        component_id = request.POST.get('component_id')
        quantity = request.POST.get('quantity', '1')

        logger.debug(f"Received data: component_type={component_type}, component_id={component_id}, quantity={quantity}")

        if not component_type or not component_id:
            error_response = {'success': False, 'error': 'Не указан тип или ID товара'}
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse(error_response, status=400)
            else:
                return redirect('builds:cart')

        try:
            quantity = int(quantity)
            if quantity < 1:
                quantity = 1
            component_id = int(component_id)
        except ValueError:
            error_response = {'success': False, 'error': 'Неверное количество'}
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse(error_response, status=400)
            else:
                return redirect('builds:cart')

        component = None

        if component_type == 'build':
            try:
                component = Build.objects.get(pk=component_id)
                cart_item, created = CartItem.objects.get_or_create(
                    user=request.user,
                    build=component,
                    cpu=None, gpu=None, motherboard=None, ram=None, storage=None, psu=None, case=None, cooler=None
                )
            except Build.DoesNotExist:
                error_response = {'success': False, 'error': 'Сборка не найдена'}
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse(error_response, status=404)
                else:
                    return redirect('builds:cart')

        else:
            component_models = {
                'cpu': CPU,
                'gpu': GPU,
                'motherboard': Motherboard,
                'ram': RAM,
                'storage': Storage,
                'psu': PSU,
                'case': Case,
                'cooler': Cooler,
            }

            component_model = component_models.get(component_type)

            if not component_model:
                error_response = {'success': False, 'error': 'Неверный тип товара'}
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse(error_response, status=400)
                else:
                    return redirect('builds:cart')

            try:
                component = component_model.objects.get(pk=component_id)
            except component_model.DoesNotExist:
                error_response = {'success': False, 'error': 'Товар не найден'}
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse(error_response, status=404)
                else:
                    return redirect('builds:cart')

            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                build=None,
                cpu=component if component_type == 'cpu' else None,
                gpu=component if component_type == 'gpu' else None,
                motherboard=component if component_type == 'motherboard' else None,
                ram=component if component_type == 'ram' else None,
                storage=component if component_type == 'storage' else None,
                psu=component if component_type == 'psu' else None,
                case=component if component_type == 'case' else None,
                cooler=component if component_type == 'cooler' else None,
            )
        logger.debug(f"CartItem created: {created}, ID: {cart_item.id}")

        # Обновляем количество
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity

        cart_item.save()

        print(f"CartItem saved: {cart_item.id}, quantity: {cart_item.quantity}, component_type: {component_type}, component_id: {component_id}")
        logger.info(f"CartItem saved: ID={cart_item.id}, quantity={cart_item.quantity}")

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        else:
            return redirect('builds:cart')


@login_required
def remove_from_cart(request, item_id):
    """Удаление товара из корзины."""
    try:
        cart_item = get_object_or_404(CartItem, pk=item_id, user=request.user)
        cart_item.delete()
        messages.success(request, "Товар успешно удален из корзины.")
    except Http404:
        messages.error(request, "Товар не найден в корзине.")
    return redirect('builds:cart')


@login_required
def remove_from_cart(request, item_id):
    """Удаление товара из корзины."""
    try:
        cart_item = get_object_or_404(CartItem, pk=item_id, user=request.user)
        cart_item.delete()
        messages.success(request, "Товар успешно удален из корзины.")
    except Http404:
        messages.error(request, "Товар не найден в корзине.")
    return redirect('builds:cart')

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
        **cart_context,  # Распаковываем cart_context (cart_items, total_price)
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
        # Получаем данные из POST
        cpu_id = request.POST.get('cpu')
        gpu_id = request.POST.get('gpu')
        motherboard_id = request.POST.get('motherboard')
        ram_id = request.POST.get('ram')
        storage_id = request.POST.get('storage')
        psu_id = request.POST.get('psu')
        case_id = request.POST.get('case')
        cooler_id = request.POST.get('cooler')  # Получаем id кулера

        # Получаем объекты компонентов
        try:
            cpu = get_object_or_404(CPU, pk=cpu_id) if cpu_id else None
            gpu = get_object_or_404(GPU, pk=gpu_id) if gpu_id else None
            motherboard = get_object_or_404(Motherboard, pk=motherboard_id) if motherboard_id else None
            ram = get_object_or_404(RAM, pk=ram_id) if ram_id else None
            storage = get_object_or_404(Storage, pk=storage_id) if storage_id else None
            psu = get_object_or_404(PSU, pk=psu_id) if psu_id else None
            case = get_object_or_404(Case, pk=case_id) if case_id else None
            cooler = get_object_or_404(Cooler, pk=cooler_id) if cooler_id else None  # Получаем кулер
        except (ValueError, TypeError, CPU.DoesNotExist, GPU.DoesNotExist, Motherboard.DoesNotExist,
                RAM.DoesNotExist, Storage.DoesNotExist, PSU.DoesNotExist, Case.DoesNotExist, Cooler.DoesNotExist):
            return render(request, 'builds/build_create.html',
                          {'error_message': 'Один из выбранных компонентов не найден.',
                           'cpus': CPU.objects.all(), 'gpus': GPU.objects.all(),
                           'motherboards': Motherboard.objects.all(), 'rams': RAM.objects.all(),
                           'storages': Storage.objects.all(), 'psus': PSU.objects.all(),
                           'cases': Case.objects.all(), 'coolers': Cooler.objects.all()})  # Добавляем coolers в context

        # Проверки совместимости
        error_message = None

        if cpu and motherboard:
            if not cpu.is_compatible_with_motherboard(motherboard):
                error_message = 'Процессор не совместим с материнской платой.'

        if motherboard and ram:
            if not motherboard.is_compatible_with_ram(ram):
                error_message = 'Оперативная память не совместима с материнской платой.'

        if gpu and psu:
            if not psu.is_sufficient_for_gpu(gpu):
                error_message = 'Мощности блока питания недостаточно для видеокарты.'

        if cpu and cooler:
            if not cooler.is_compatible_with_cpu(cpu):
                error_message = 'Кулер не совместим с процессором.'

        if error_message:
            return render(request, 'builds/build_create.html',
                          {'error_message': error_message,
                           'cpus': CPU.objects.all(), 'gpus': GPU.objects.all(),
                           'motherboards': Motherboard.objects.all(), 'rams': RAM.objects.all(),
                           'storages': Storage.objects.all(), 'psus': PSU.objects.all(),
                           'cases': Case.objects.all(), 'coolers': Cooler.objects.all()})


        # Создаем сборку
        total_price = Decimal('0.0')
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
        if cooler:
            total_price += cooler.price  # Добавляем цену кулера

        build = Build(user=request.user, cpu=cpu, gpu=gpu, motherboard=motherboard, ram=ram, storage=storage, psu=psu, case=case, cooler=cooler, total_price=total_price)  # Добавляем cooler в аргументы
        try:
            build.save()
            return redirect('builds:build_detail', pk=build.pk)
        except ValidationError as e:
             return render(request, 'builds/build_create.html',
                          {'error_message': f'Ошибка сохранения сборки: {e}',
                           'cpus': CPU.objects.all(), 'gpus': GPU.objects.all(),
                           'motherboards': Motherboard.objects.all(), 'rams': RAM.objects.all(),
                           'storages': Storage.objects.all(), 'psus': PSU.objects.all(),
                           'cases': Case.objects.all(), 'coolers': Cooler.objects.all()})

    else:
        cpus = CPU.objects.all()
        gpus = GPU.objects.all()
        motherboards = Motherboard.objects.all()
        rams = RAM.objects.all()
        storages = Storage.objects.all()
        psus = PSU.objects.all()
        cases = Case.objects.all()
        coolers = Cooler.objects.all()  # Получаем все кулеры
        context = {'cpus': cpus, 'gpus': gpus, 'motherboards': motherboards, 'rams': rams, 'storages': storages, 'psus': psus, 'cases': cases, 'coolers': coolers}  # Добавляем coolers в context
        return render(request, 'builds/build_create.html', context)


def build_edit(request, pk):
    build = get_object_or_404(Build, pk=pk)

    if request.method == 'POST':
        # Получаем данные из POST
        cpu_id = request.POST.get('cpu')
        gpu_id = request.POST.get('gpu')
        motherboard_id = request.POST.get('motherboard')
        ram_id = request.POST.get('ram')
        storage_id = request.POST.get('storage')
        psu_id = request.POST.get('psu')
        case_id = request.POST.get('case')
        cooler_id = request.POST.get('cooler')

        # Получаем объекты компонентов, обрабатывая ошибки
        try:
            cpu = CPU.objects.get(pk=cpu_id) if cpu_id else None
            gpu = GPU.objects.get(pk=gpu_id) if gpu_id else None
            motherboard = Motherboard.objects.get(pk=motherboard_id) if motherboard_id else None
            ram = RAM.objects.get(pk=ram_id) if ram_id else None
            storage = Storage.objects.get(pk=storage_id) if storage_id else None
            psu = PSU.objects.get(pk=psu_id) if psu_id else None
            case = Case.objects.get(pk=case_id) if case_id else None
            cooler = Cooler.objects.get(pk=cooler_id) if cooler_id else None
        except (CPU.DoesNotExist, GPU.DoesNotExist, Motherboard.DoesNotExist, RAM.DoesNotExist, Storage.DoesNotExist, PSU.DoesNotExist, Case.DoesNotExist, Cooler.DoesNotExist):
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
                'coolers': Cooler.objects.all(), # Добавляем coolers
            })
        error_message = None

        if cpu and motherboard:
            if not cpu.is_compatible_with_motherboard(motherboard):
                error_message = 'Процессор не совместим с материнской платой.'

        if motherboard and ram:
            if not motherboard.is_compatible_with_ram(ram):
                error_message = 'Оперативная память не совместима с материнской платой.'

        if gpu and psu:
            if not psu.is_sufficient_for_gpu(gpu):
                error_message = 'Мощности блока питания недостаточно для видеокарты.'

        if cpu and cooler:
            if not cooler.is_compatible_with_cpu(cpu):
                error_message = 'Кулер не совместим с процессором.'

        if error_message:
            return render(request, 'builds/build_edit.html', {
                'build': build,
                'error_message': error_message,
                'cpus': CPU.objects.all(),
                'gpus': GPU.objects.all(),
                'motherboards': Motherboard.objects.all(),
                'rams': RAM.objects.all(),
                'storages': Storage.objects.all(),
                'psus': PSU.objects.all(),
                'cases': Case.objects.all(),
                'coolers': Cooler.objects.all(),  # Добавляем coolers
            })

        #  Обновление полей build
        build.cpu = cpu
        build.gpu = gpu
        build.motherboard = motherboard
        build.ram = ram
        build.storage = storage
        build.psu = psu
        build.case = case
        build.cooler = cooler # Добавлено обновление кулера

        # Рассчитываем общую стоимость
        total_price = Decimal('0.0')
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
        if psu:
            total_price += build.psu.price
        if case:
            total_price += build.case.price
        if cooler:
            total_price += build.cooler.price  # Добавляем цену кулера
        build.total_price = total_price

        try:
            build.save()
            return redirect('builds:build_detail', pk=build.pk)
        except ValidationError as e:
            return render(request, 'builds/build_edit.html', {
                'build': build,
                'error_message': f'Ошибка сохранения сборки: {e}',
                'cpus': CPU.objects.all(),
                'gpus': GPU.objects.all(),
                'motherboards': Motherboard.objects.all(),
                'rams': RAM.objects.all(),
                'storages': Storage.objects.all(),
                'psus': PSU.objects.all(),
                'cases': Case.objects.all(),
                'coolers': Cooler.objects.all(),  # Добавляем coolers
            })

    else:
        # Отобразите форму с текущими значениями
        cpus = CPU.objects.all()
        gpus = GPU.objects.all()
        motherboards = Motherboard.objects.all()
        rams = RAM.objects.all()
        storages = Storage.objects.all()
        psus = PSU.objects.all()
        cases = Case.objects.all()
        coolers = Cooler.objects.all()

        context = {
            'build': build,
            'cpus': cpus,
            'gpus': gpus,
            'motherboards': motherboards,
            'rams': rams,
            'storages': storages,
            'psus': psus,
            'cases': cases,
            'coolers': coolers,
        }
        return render(request, 'builds/build_edit.html', context)

# Функция для проверки, является ли пользователь сотрудником
def is_employee(user):
    return user.is_staff  # Проверка, является ли пользователь сотрудником (is_staff)

# Форма
class CustomOrderUpdateForm(OrderUpdateForm):
    def __init__(self, *args, **kwargs):
        status_choices = kwargs.pop('status_choices', [])
        super().__init__(*args, **kwargs)
        self.fields['status'].choices = status_choices  # Задаём в конструкторе


# Представление для сотрудников для просмотра и изменения заказов
@login_required
@user_passes_test(is_employee)
def employee_order_list(request):
    query = request.GET.get('q')
    if query:
        orders = Order.objects.filter(
            Q(is_completed=False) & (
                Q(track_number__icontains=query) |
                Q(user__username__icontains=query) |
                Q(email__icontains=query)
            )
        ).order_by('-order_date')
    else:
        orders = Order.objects.filter(is_completed=False).order_by('-order_date')

    # Пагинация
    paginator = Paginator(orders, 10)  # По 10 заказов на страницу
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'builds/employee_order_list.html', {'page_obj': page_obj, 'query': query})



# Представление для обновления статуса заказа
@login_required
@user_passes_test(is_employee)
def employee_order_update(request, order_id):
    order = get_object_or_404(Order, pk=order_id)

    # Определение доступных статусов на основе доставки
    if order.delivery_option == 'courier':  # Должно быть 'courier'
        status_choices = [
            ('pending', 'Заказ на рассмотрении'),
            ('confirmed', 'Заказ подтверждён'),
            ('assembling', 'Заказ собирается'),
            ('delivery_prep', 'Заказ готовится к доставке'),
            ('delivering', 'Заказ будет доставлен вам в течении 3 часов'),
            ('completed', 'Заказ выполнен'),
        ]
    else:  # Самовывоз или другой способ доставки
        status_choices = [
            ('pending', 'Заказ на рассмотрении'),
            ('confirmed', 'Заказ подтверждён'),
            ('delivered', 'Заказ доставлен, заберите его'),
            ('completed', 'Заказ выполнен'),
        ]

    if request.method == 'POST':
        form = CustomOrderUpdateForm(request.POST, instance=order, status_choices=status_choices)
        if form.is_valid():
            form.save()
            messages.success(request, f"Статус заказа #{order.pk} успешно изменен.")
            return redirect('builds:employee_order_list')
    else:
        form = CustomOrderUpdateForm(instance=order, status_choices=status_choices)
    return render(request, 'builds/employee_order_update.html', {'form': form, 'order': order})


@login_required
@user_passes_test(is_employee)
def employee_order_complete(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    order.is_completed = True
    order.status = 'completed'  # Задаем статус "Заказ выполнен"
    order.save()
    messages.success(request, f"Заказ #{order.pk} отмечен как выданный.")
    return redirect('builds:employee_order_list')


@login_required
@user_passes_test(is_employee)
def employee_order_history(request):
    query = request.GET.get('q')
    if query:
        orders = Order.objects.filter(
            Q(is_completed=True) & (
                Q(track_number__icontains=query) |
                Q(user__username__icontains=query) |
                Q(email__icontains=query)
            )
        ).order_by('-order_date')
    else:
        orders = Order.objects.filter(is_completed=True).order_by('-order_date')

    # Пагинация
    paginator = Paginator(orders, 10)  # По 10 заказов на страницу
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'builds/employee_order_history.html', {'page_obj': page_obj, 'query': query})


@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.get_total_price() for item in cart_items)

    if request.method == 'POST':
        # Обработка данных формы оформления заказа
        email = request.POST.get('email')
        delivery_option = request.POST.get('delivery_option')
        payment_method = request.POST.get('payment_method')
        address = request.POST.get('address')

        # Валидация данных (здесь можно добавить более сложную валидацию)
        if not email or not delivery_option or not payment_method:
            messages.error(request, "Пожалуйста, заполните все поля.")
            return render(request, 'builds/checkout.html', {'cart_items': cart_items, 'total_price': total_price})

        # Создание заказа
        order = Order.objects.create(
            user=request.user,
            email=email,
            delivery_option=delivery_option,
            payment_method=payment_method,
            address=address,
            total_amount=total_price,
            order_date=timezone.now()
        )
        # order.save() # Не нужно, т.к. используем Order.objects.create()

        # Создание позиций заказа
        for item in cart_items:
            component_type = None
            component_id = None

            if item.build:
                component_type = 'build'
                component_id = item.build.pk
            elif item.cpu:
                component_type = 'cpu'
                component_id = item.cpu.pk
            elif item.gpu:
                component_type = 'gpu'
                component_id = item.gpu.pk
            elif item.motherboard:
                component_type = 'motherboard'
                component_id = item.motherboard.pk
            elif item.ram:
                component_type = 'ram'
                component_id = item.ram.pk
            elif item.storage:
                component_type = 'storage'
                component_id = item.storage.pk
            elif item.psu:
                component_type = 'psu'
                component_id = item.psu.pk
            elif item.case:
                component_type = 'case'
                component_id = item.case.pk
            elif item.cooler:
                component_type = 'cooler'
                component_id = item.cooler.pk

            OrderItem.objects.create(
                order=order,
                item=str(item),  # Преобразуем товар в строку
                quantity=item.quantity,
                price=item.get_total_price() / item.quantity,
                component_type=component_type,
                component_id=component_id,
            )

        # Очистка корзины после оформления заказа
        cart_items.delete()

        # Отправка уведомления по электронной почте
        subject = 'Ваш заказ оформлен!'
        message = f'Спасибо за ваш заказ! \n\nСумма заказа: {total_price} ₽\nСпособ доставки: {order.delivery_option}\nСпособ оплаты: {order.payment_method}\nАдрес доставки: {order.address}\nВаш трек-номер: {order.track_number}'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]

        try:
            send_mail(subject, message, from_email, recipient_list)
            success = True
        except Exception as e:
            messages.error(request, f"Заказ оформлен, но не удалось отправить уведомление: {e}")
            success = False

        # Перенаправление на страницу подтверждения с параметром в URL
        if success:
            return redirect(reverse('builds:order_confirmation') + f'?success=True&track_number={order.track_number}')
        else:
            return redirect(reverse('builds:order_confirmation') + '?success=False')

    return render(request, 'builds/checkout.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required
def order_confirmation(request):
    success = request.GET.get('success')
    track_number = request.GET.get('track_number')
    if success == 'True':
        messages.success(request, f"Заказ успешно оформлен! Проверьте вашу электронную почту. Ваш трек-номер: {track_number}")
    elif success == 'False':
        messages.error(request, "Заказ оформлен, но не удалось отправить уведомление.")

    return render(request, 'builds/order_confirmation.html', {'track_number': track_number})


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_completed=False).order_by('-order_date')  # Показывать только невыданные заказы
    return render(request, 'builds/my_orders.html', {'orders': orders})


def is_employee(user):
    return user.is_staff


def index(request):
    cpu_list = CPU.objects.all().select_related()
    paginator = Paginator(cpu_list, 6)

    page = request.GET.get('page')
    try:
        cpus = paginator.page(page)
    except PageNotAnInteger:
        cpus = paginator.page(1)
    except EmptyPage:
        cpus = paginator.page(paginator.num_pages)

    context = {'cpus': cpus}

    if request.user.is_authenticated:
        if is_employee(request.user):
            return render(request, 'pc_builder/employee_index.html', context)
        else:
            return render(request, 'pc_builder/index.html', context)
    else:
        return render(request, 'pc_builder/index.html', context)
    

def get_compatible_motherboards(request):
    """
    Возвращает JSON с материнскими платами, совместимыми с выбранным CPU.
    """
    cpu_id = request.GET.get('cpu_id')
    if cpu_id:
        try:
            cpu = CPU.objects.get(pk=cpu_id)
            # Получаем материнские платы с тем же сокетом, что и у CPU
            compatible_motherboards = Motherboard.objects.filter(socket=cpu.socket).values('id', 'name') # .values() для оптимизации
            return JsonResponse(list(compatible_motherboards), safe=False) # Преобразуем QuerySet в список
        except CPU.DoesNotExist:
            return JsonResponse({'error': 'CPU не найден'}, status=404)
    else:
        return JsonResponse({'error': 'Не указан CPU ID'}, status=400)


def get_compatible_rams(request):
    """
    Возвращает JSON с RAM, совместимой с выбранной материнской платой.
    """
    motherboard_id = request.GET.get('motherboard_id')
    if motherboard_id:
        try:
            motherboard = Motherboard.objects.get(pk=motherboard_id)
            # Получаем RAM с тем же типом и поддерживаемой частотой, что и у материнской платы
            compatible_rams = RAM.objects.filter(
                ram_type=motherboard.ram_type,
                memory_clock__lte=motherboard.max_ram_speed
            ).values('id', 'name')
            return JsonResponse(list(compatible_rams), safe=False)
        except Motherboard.DoesNotExist:
            return JsonResponse({'error': 'Motherboard не найдена'}, status=404)
    else:
        return JsonResponse({'error': 'Не указан Motherboard ID'}, status=400)


def get_compatible_cpu(request):
    """
    Возвращает JSON с CPU, совместимыми с выбранной материнской платой.
    """
    motherboard_id = request.GET.get('motherboard_id')
    if motherboard_id:
        try:
            motherboard = Motherboard.objects.get(pk=motherboard_id)
            # Получаем CPU с тем же сокетом, что и у материнской платы
            compatible_cpus = CPU.objects.filter(socket=motherboard.socket).values('id', 'name')
            return JsonResponse(list(compatible_cpus), safe=False)
        except Motherboard.DoesNotExist:
            return JsonResponse({'error': 'Motherboard не найдена'}, status=404)
    else:
        return JsonResponse({'error': 'Не указан Motherboard ID'}, status=400)