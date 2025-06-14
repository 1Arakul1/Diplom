# pc_builder/urls.py
from django.contrib import admin
from django.urls import include, path
from . import views  # Убедись, что импортируешь views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('__debug__/', include('debug_toolbar.urls')),
    path('admin/', admin.site.urls),
    path('users/', include('users.urls', namespace='users')), # <<-- Проверьте namespace!
    path('', views.index, name='index'),  # Добавь этот путь
    path('components/', include('components.urls', namespace='components')),  # Раскомментируй и проверь
    path('builds/', include('builds.urls', namespace='builds')),  # Раскомментируй и проверь
    path('games/', include('games.urls', namespace='games')), # <--- Важно!
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)