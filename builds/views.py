# builds/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import Build
from components.models import CPU, GPU, Motherboard, RAM, Storage, PSU, Case
from django.contrib.auth.decorators import login_required #Импортируем декоратор

@login_required # Добавляем декоратор
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

        cpu = get_object_or_404(CPU, pk=cpu_id)
        gpu = get_object_or_404(GPU, pk=gpu_id)
        motherboard = get_object_or_404(Motherboard, pk=motherboard_id)
        ram = get_object_or_404(RAM, pk=ram_id)
        storage = get_object_or_404(Storage, pk=storage_id)
        psu = get_object_or_404(PSU, pk=psu_id)
        case = get_object_or_404(Case, pk=case_id)

        # Рассчитываем общую стоимость (примерно)
        total_price = cpu.price + gpu.price + motherboard.price + ram.price + storage.price + psu.price + case.price

        build = Build(
            user=request.user,  # Присваиваем текущего пользователя
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

def build_list(request):
    builds = Build.objects.all()  # Получаем все сборки
    return render(request, 'builds/build_list.html', {'builds': builds})

def build_detail(request, pk):
    build = get_object_or_404(Build, pk=pk)  # Получаем сборку или возвращаем 404
    return render(request, 'builds/build_detail.html', {'build': build})

