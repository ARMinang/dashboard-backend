"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path
from pemasaran.views import IuranBulanan, TkBulanan, NppBulanan, IuranPerAr,\
    TkPerAr, NppBulananPerArk

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/iuran/ar/', IuranPerAr.as_view(), name='api-iuran-ar'),
    path('api/tk/ar/', TkPerAr.as_view(), name='api-tk-ar'),
    path('api/npp/ar/', NppBulananPerArk.as_view(), name='api-npp-ar'),
    path('api/iuran/', IuranBulanan.as_view(), name='api-iuran'),
    path('api/tk/', TkBulanan.as_view(), name='api-tk'),
    path('api/npp/', NppBulanan.as_view(), name='api-npp')
]
