"""netology_pd_diplom URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from backend.admin_views import import_products_view

# Настройка заголовков админки
admin.site.site_header = "Администрирование магазина"
admin.site.site_title = "Магазин"
admin.site.index_title = "Панель управления"

urlpatterns = [
    path('admin/import-products/', import_products_view, name='import_products'),
    path('admin/', admin.site.urls),
    path('api/v1/', include('backend.urls', namespace='backend'))
]