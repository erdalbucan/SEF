"""
URL configuration for SEF project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from appsef.views.views_personel import Pgiris_saati_ekle, Pcikis_saati_ekle, Personel_MesaiPlan_view
from appsef.views.views_formul import FormulCsvupload_file, FormulCsvlist_files, FormulCsvview_file
from appsef.views.views_rapor import RAPOR_view, resept_maliyet_list, uretim_istatistik_girisi, gunluk_uretim_view, uretim_listesi
# from appsef.views.views_rapor import finans_raporu, gunluk_gider_hesapla
# from appsef.views.views_rapor import gunluk_veriler_al
from appsef.views.views import home
from appsef.views.views_Uretim import uretim_sayi_yukleme_view, hammadde_formul, tarih_list, urun_grup_list, urun_grubu_detaylari_view, siparis_ver


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # Ana sayfa URL yönlendirmesi
    path('rapor/', RAPOR_view, name='rapor'),
    # path('finansraporu/', finans_raporu, name='finans_raporu'),
    # path('gunlukgider/', gunluk_gider_hesapla, name='gunluk_gider_hesapla'),
    path('Pgiris/', Pgiris_saati_ekle, name='Pgiris_saati_ekle'),
    path('Pcikis/', Pcikis_saati_ekle, name='Pcikis_saati_ekle'),
    path('PersonelMesaiPlan/', Personel_MesaiPlan_view, name='personel_mesaiPlanYukle_url'),
    path('resept-maliyet/', resept_maliyet_list, name='resept_maliyet_list'),
    path('uretim-istatistik-girisi/', uretim_istatistik_girisi, name='uretim_istatistik_girisi'),
    path('accounts/', include('django.contrib.auth.urls')),  # Django auth URL'lerini dahil edin
    path('FormulCsvyukle/', FormulCsvupload_file, name='upload_file'),  # CSV yükleme sayfası
    path('FormulCsvfiles/', FormulCsvlist_files, name='FrmlCsvlist_files'),# Yüklenen dosyaların listesi
    path('FormulCsvView/<int:file_id>/', FormulCsvview_file, name='view_file'),# Belirli bir dosyayı görüntüleme
    path('UretimSayiYukle/', uretim_sayi_yukleme_view, name='uretim_sayi_yukleme'),
    path('hammadde_formul/', hammadde_formul, name='hammadde_formul'),
    path('gunluk-uretim/', gunluk_uretim_view, name='gunluk_uretim'),
    path('uretim-listesi/', uretim_listesi, name='uretim_listesi'),
    path('formul-trh/', tarih_list, name='tarih_list'),  # Tarihlerin listesi
    path('urunler/<str:tarih>/', urun_grup_list, name='urun_grup_list'),  # Tarihe ait ürün grupları
    path('detaylar/<str:tarih>/<str:urun_grubu>/', urun_grubu_detaylari_view, name='urun_grubu_detaylari'),  # Ürün grubuna ait detaylar
    path('siparis_ver.html', siparis_ver, name='siparis_ver'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
