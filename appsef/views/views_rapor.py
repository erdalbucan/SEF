from django.shortcuts import render
from django.db.models import Avg, Min, Max, Sum
from datetime import date
import calendar
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render, redirect
from appsef.models import UretimIstatistik, Depo, GunlukGider, GunlukGelir, Resept_maliyet
from appsef.forms import UretimIstatistikForm, GunlukUretimForm, UretimFormSet


def urun_gruplari_detaylarini_al():
    urun_gruplari_detay = UretimIstatistik.objects.values('urun_adi').annotate(
        ortalama_maliyet=Avg('maliyet_uretim'),
        en_dusuk_maliyet=Min('maliyet_uretim')
    )

    urun_gruplari_list = []
    for grup in urun_gruplari_detay:
        en_dusuk_maliyet_tarih = UretimIstatistik.objects.filter(
            urun_adi=grup['urun_adi'],
            maliyet_uretim=grup['en_dusuk_maliyet']
        ).values_list('tarih', flat=True).first()

        if en_dusuk_maliyet_tarih:
            en_dusuk_maliyet_tarih = en_dusuk_maliyet_tarih.strftime("%-d.%-m.%y")

        fark = grup['ortalama_maliyet'] - grup['en_dusuk_maliyet']

        son_uretim = UretimIstatistik.objects.filter(
            urun_adi=grup['urun_adi']
        ).order_by('-tarih').first()
        son_uretim_maliyeti = son_uretim.maliyet_uretim if son_uretim else 0

        urun_gruplari_list.append({
            'urun_adi': grup['urun_adi'],
            'ortalama_maliyet': grup['ortalama_maliyet'],
            'en_dusuk_maliyet': grup['en_dusuk_maliyet'],
            'en_dusuk_maliyet_tarih': en_dusuk_maliyet_tarih,
            'fark': fark,
            'son_uretim_maliyeti': son_uretim_maliyeti
        })

    urun_gruplari_list.sort(key=lambda x: x['en_dusuk_maliyet_tarih'], reverse=True)
    return urun_gruplari_list

def depo_kategorileri_al():
    depolar = Depo.objects.all()
    kategori1_urunleri = []
    kategori2_urunleri = []
    kategori3_urunleri = []
    kategori4_urunleri = []

    toplam_fiyat_kategori1 = 0
    toplam_fiyat_kategori2 = 0
    toplam_fiyat_kategori3 = 0
    toplam_fiyat_kategori4 = 0

    for depo in depolar:
        hammadde_maliyeti = depo.hammadde_maliyet  # Hammadde maliyeti alınır
        if depo.miktar >= depo.kategori1:
            maddi_deger = depo.miktar * hammadde_maliyeti  # Hammadde maliyeti ile çarpılır
            kategori1_urunleri.append({
                'hammadde_adi': depo.hammadde.hammadde_adi,
                'miktar': depo.miktar,
                'maddi_deger': maddi_deger
            })
            toplam_fiyat_kategori1 += maddi_deger
        elif depo.kategori2 <= depo.miktar < depo.kategori1:
            maddi_deger = depo.miktar * hammadde_maliyeti  # Hammadde maliyeti ile çarpılır
            kategori2_urunleri.append({
                'hammadde_adi': depo.hammadde.hammadde_adi,
                'miktar': depo.miktar,
                'maddi_deger': maddi_deger
            })
            toplam_fiyat_kategori2 += maddi_deger
        elif depo.kategori3 <= depo.miktar < depo.kategori2:
            gerekli_miktar = depo.kategori2 - depo.miktar
            maliyet = gerekli_miktar * hammadde_maliyeti  # Eksik miktar için maliyet hesaplanır
            kategori3_urunleri.append({
                'hammadde_adi': depo.hammadde.hammadde_adi,
                'miktar': depo.miktar,
                'gerekli_miktar': gerekli_miktar,
                'gerekli_maliyet': maliyet
            })
            toplam_fiyat_kategori3 += maliyet
        else:
            gerekli_miktar = depo.kategori2 - depo.miktar
            maliyet = gerekli_miktar * hammadde_maliyeti  # Eksik miktar için maliyet hesaplanır
            kategori4_urunleri.append({
                'hammadde_adi': depo.hammadde.hammadde_adi,
                'miktar': depo.miktar,
                'gerekli_miktar': gerekli_miktar,
                'gerekli_maliyet': maliyet
            })
            toplam_fiyat_kategori4 += maliyet

    return (kategori1_urunleri, kategori2_urunleri, kategori3_urunleri, kategori4_urunleri,
            toplam_fiyat_kategori1, toplam_fiyat_kategori2, toplam_fiyat_kategori3, toplam_fiyat_kategori4)



def gunluk_veriler_al():
    son_tarih = UretimIstatistik.objects.aggregate(son_tarih=Max('tarih'))['son_tarih']
    gunluk_uretim_verileri = UretimIstatistik.objects.filter(tarih=son_tarih).values(
        'urun_adi', 'uretim_adedi', 'kac_kisi_calisti', 'toplam_calisma_saati', 'maliyet_uretim'
    )

    today = date.today()
    gunluk_gider = GunlukGider.objects.filter(tarih=today).first()
    print (gunluk_gider)
    gunluk_gelir = GunlukGelir.objects.filter(tarih=today).first()

    gunlukTPLgelir = gunluk_gelir.toplam_gelir if gunluk_gelir else 0

    net_gunluk_gelir = None
    if gunluk_gider and gunluk_gelir:
        net_gunluk_gelir = gunluk_gelir.toplam_gelir - (
            gunluk_gider.hammadde_gideri + gunluk_gider.personel_planlanan + gunluk_gider.personel_ilave + gunluk_gider.sabit_gider_payi
        )
    elif gunluk_gelir:
        net_gunluk_gelir = gunluk_gelir.toplam_gelir
    elif gunluk_gider:
        net_gunluk_gelir = - (
            gunluk_gider.hammadde_gideri + gunluk_gider.personel_planlanan + gunluk_gider.personel_ilave + gunluk_gider.sabit_gider_payi
        )

    return gunluk_uretim_verileri, gunlukTPLgelir, net_gunluk_gelir, gunluk_gider, gunluk_gelir, son_tarih
def aylik_rapor_al():
    today = date.today()
    current_month = today.month
    current_year = today.year
    aylik_giderler = GunlukGider.objects.filter(tarih__year=current_year, tarih__month=current_month)
    toplam_aylik_gider = aylik_giderler.aggregate(
        total=Sum('hammadde_gideri') + Sum('personel_planlanan') + Sum('personel_ilave') + Sum('sabit_gider_payi')
    )['total']
    ay_adi = calendar.month_name[current_month]

    aylik_gelirler = GunlukGelir.objects.filter(tarih__year=current_year, tarih__month=current_month)
    toplam_aylik_gelir = aylik_gelirler.aggregate(total=Sum('toplam_gelir'))['total']

    if toplam_aylik_gelir is None:
        toplam_aylik_gelir = 0
    if toplam_aylik_gider is None:
        toplam_aylik_gider = 0

    aylik_fark = toplam_aylik_gelir - toplam_aylik_gider
    return aylik_giderler, toplam_aylik_gider, toplam_aylik_gelir, aylik_fark, ay_adi

@csrf_protect
@login_required
@permission_required('raporlari_GOR.rapori_gorebilir', raise_exception=True)
def RAPOR_view(request):
    # Ürün grupları detaylarını alıyoruz
    urun_gruplari_list = urun_gruplari_detaylarini_al()

    # Depo kategorilerini alıyoruz
    kategori1_urunleri, kategori2_urunleri, kategori3_urunleri, kategori4_urunleri, toplam_fiyat_kategori1, toplam_fiyat_kategori2, toplam_fiyat_kategori3, toplam_fiyat_kategori4 = depo_kategorileri_al()

    # Günlük verileri alıyoruz
    gunluk_uretim_verileri, gunlukTPLgelir, net_gunluk_gelir, gunluk_gider, gunluk_gelir, son_tarih = gunluk_veriler_al()

    # Aylık raporu alıyoruz
    aylik_giderler, toplam_aylik_gider, toplam_aylik_gelir, aylik_fark, ay_adi = aylik_rapor_al()

    # Verileri şablona gönderiyoruz
    context = {
        'urun_gruplari_detay': urun_gruplari_list,
        'kategori1_urunleri': kategori1_urunleri,
        'kategori2_urunleri': kategori2_urunleri,
        'kategori3_urunleri': kategori3_urunleri,
        'kategori4_urunleri': kategori4_urunleri,
        'toplam_fiyat_kategori1': toplam_fiyat_kategori1,
        'toplam_fiyat_kategori2': toplam_fiyat_kategori2,
        'toplam_fiyat_kategori3': toplam_fiyat_kategori3,
        'toplam_fiyat_kategori4': toplam_fiyat_kategori4,
        'gunluk_uretim_verileri': gunluk_uretim_verileri,
        'son_tarih': son_tarih.strftime("%-d.%-m.%y") if son_tarih else '',
        'gunluk_gider': gunluk_gider,
        'gunluk_gelir': gunluk_gelir,
        'gunluk_TPL_gelir': gunlukTPLgelir,
        'net_gunluk_gelir': net_gunluk_gelir,
        'aylik_giderler': aylik_giderler,
        'toplam_aylik_gider': toplam_aylik_gider,
        'toplam_aylik_gelir': toplam_aylik_gelir,
        'aylik_fark': aylik_fark,
        'ay_adi': ay_adi,
    }

    return render(request, 'rapor.html', context)
# def RAPOR_view(request):
#     urun_gruplari_detay = UretimIstatistik.objects.values('urun_adi').annotate(
#         ortalama_maliyet=Avg('maliyet_uretim'),
#         en_dusuk_maliyet=Min('maliyet_uretim')
#     )
#
#     urun_gruplari_list = []
#     for grup in urun_gruplari_detay:
#         en_dusuk_maliyet_tarih = UretimIstatistik.objects.filter(
#             urun_adi=grup['urun_adi'],
#             maliyet_uretim=grup['en_dusuk_maliyet']
#         ).values_list('tarih', flat=True).first()
#
#         if en_dusuk_maliyet_tarih:
#             en_dusuk_maliyet_tarih = en_dusuk_maliyet_tarih.strftime("%-d.%-m.%y")
#
#         fark = grup['ortalama_maliyet'] - grup['en_dusuk_maliyet']
#
#         son_uretim = UretimIstatistik.objects.filter(
#             urun_adi=grup['urun_adi']
#         ).order_by('-tarih').first()
#         son_uretim_maliyeti = son_uretim.maliyet_uretim if son_uretim else 0
#
#         urun_gruplari_list.append({
#             'urun_adi': grup['urun_adi'],
#             'ortalama_maliyet': grup['ortalama_maliyet'],
#             'en_dusuk_maliyet': grup['en_dusuk_maliyet'],
#             'en_dusuk_maliyet_tarih': en_dusuk_maliyet_tarih,
#             'fark': fark,
#             'son_uretim_maliyeti': son_uretim_maliyeti
#         })
#
#     urun_gruplari_list.sort(key=lambda x: x['en_dusuk_maliyet_tarih'], reverse=True)
#
#     depolar = Depo.objects.all()
#     kategori1_urunleri = []
#     kategori2_urunleri = []
#     kategori3_urunleri = []
#     kategori4_urunleri = []
#
#     toplam_fiyat_kategori1 = 0
#     toplam_fiyat_kategori2 = 0
#     toplam_fiyat_kategori3 = 0
#     toplam_fiyat_kategori4 = 0
#
#     for depo in depolar:
#         son_alis_fiyati = depo.get_son_alis_fiyati()
#         if depo.miktar >= depo.kategori1:
#             maddi_deger = depo.miktar * son_alis_fiyati
#             kategori1_urunleri.append({
#                 'hammadde_adi': depo.hammadde.hammadde_adi,
#                 'miktar': depo.miktar,
#                 'maddi_deger': maddi_deger
#             })
#             toplam_fiyat_kategori1 += maddi_deger
#         elif depo.kategori2 <= depo.miktar < depo.kategori1:
#             maddi_deger = depo.miktar * son_alis_fiyati
#             kategori2_urunleri.append({
#                 'hammadde_adi': depo.hammadde.hammadde_adi,
#                 'miktar': depo.miktar,
#                 'maddi_deger': maddi_deger
#             })
#             toplam_fiyat_kategori2 += maddi_deger
#         elif depo.kategori3 <= depo.miktar < depo.kategori2:
#             gerekli_miktar = depo.kategori2 - depo.miktar
#             maliyet = gerekli_miktar * son_alis_fiyati
#             kategori3_urunleri.append({
#                 'hammadde_adi': depo.hammadde.hammadde_adi,
#                 'miktar': depo.miktar,
#                 'gerekli_miktar': gerekli_miktar,
#                 'gerekli_maliyet': maliyet
#             })
#             toplam_fiyat_kategori3 += maliyet
#         else:
#             gerekli_miktar = depo.kategori2 - depo.miktar
#             maliyet = gerekli_miktar * son_alis_fiyati
#             kategori4_urunleri.append({
#                 'hammadde_adi': depo.hammadde.hammadde_adi,
#                 'miktar': depo.miktar,
#                 'gerekli_miktar': gerekli_miktar,
#                 'gerekli_maliyet': maliyet
#             })
#             toplam_fiyat_kategori4 += maliyet
#
#     # Günlük Üretim Raporu
#     son_tarih = UretimIstatistik.objects.aggregate(son_tarih=Max('tarih'))['son_tarih']
#     gunluk_uretim_verileri = UretimIstatistik.objects.filter(tarih=son_tarih).values(
#         'urun_adi', 'uretim_adedi', 'kac_kisi_calisti', 'toplam_calisma_saati', 'maliyet_uretim'
#     )
#
#     # Günlük Gider ve Gelir Raporu
#     today = date.today()
#     gunluk_gider = GunlukGider.objects.filter(tarih=today).first()
#     gunluk_gelir = GunlukGelir.objects.filter(tarih=today).first()
#
#     # Günlük Gelir Kontrolü
#     gunlukTPLgelir = gunluk_gelir.toplam_gelir if gunluk_gelir else 0
#
#     # Net Günlük Gelir Hesaplama
#     net_gunluk_gelir = None
#     if gunluk_gider and gunluk_gelir:
#         net_gunluk_gelir = gunluk_gelir.toplam_gelir - (
#                 gunluk_gider.hammadde_gideri + gunluk_gider.personel_gideri + gunluk_gider.sabit_gider_payi
#         )
#     elif gunluk_gelir:
#         net_gunluk_gelir = gunluk_gelir.toplam_gelir
#     elif gunluk_gider:
#         net_gunluk_gelir = - (
#                     gunluk_gider.hammadde_gideri + gunluk_gider.personel_gideri + gunluk_gider.sabit_gider_payi)
#
#
#     # Aylık Gider Raporu
#     current_month = today.month
#     current_year = today.year
#     aylik_giderler = GunlukGider.objects.filter(tarih__year=current_year, tarih__month=current_month)
#     toplam_aylik_gider = \
#     aylik_giderler.aggregate(total=Sum('hammadde_gideri') + Sum('personel_gideri') + Sum('sabit_gider_payi'))['total']
#     ay_adi = calendar.month_name[current_month]
#
#     # Aylık Gelir Raporu
#     aylik_gelirler = GunlukGelir.objects.filter(tarih__year=current_year, tarih__month=current_month)
#     toplam_aylik_gelir = aylik_gelirler.aggregate(total=Sum('toplam_gelir'))['total']
#
#     # Aylık Gelir - Gider Farkı
#     if toplam_aylik_gelir is None:
#         toplam_aylik_gelir = 0
#
#     if toplam_aylik_gider is None:
#         toplam_aylik_gider = 0
#     aylik_fark = toplam_aylik_gelir - toplam_aylik_gider
#
#     context = {
#         'urun_gruplari_detay': urun_gruplari_list,
#         'kategori1_urunleri': kategori1_urunleri,
#         'kategori2_urunleri': kategori2_urunleri,
#         'kategori3_urunleri': kategori3_urunleri,
#         'kategori4_urunleri': kategori4_urunleri,
#         'toplam_fiyat_kategori1': toplam_fiyat_kategori1,
#         'toplam_fiyat_kategori2': toplam_fiyat_kategori2,
#         'toplam_fiyat_kategori3': toplam_fiyat_kategori3,
#         'toplam_fiyat_kategori4': toplam_fiyat_kategori4,
#         'gunluk_uretim_verileri': gunluk_uretim_verileri,
#         'son_tarih': son_tarih.strftime("%-d.%-m.%y") if son_tarih else '',
#         'gunluk_gider': gunluk_gider,
#         'gunluk_gelir': gunluk_gelir,
#         'gunluk_TPL_gelir': gunlukTPLgelir,
#         'net_gunluk_gelir': net_gunluk_gelir,
#         'aylik_giderler': aylik_giderler,
#         'toplam_aylik_gider': toplam_aylik_gider,
#         'toplam_aylik_gelir': toplam_aylik_gelir,
#         'aylik_fark': aylik_fark,
#         'ay_adi': ay_adi,
#     }
#
#     return render(request, 'rapor.html', context)
###########################



# def finans_raporu(request):
#     today = date.today()
#     gunluk_gider = GunlukGider.objects.filter(tarih=today).first()
#     print(gunluk_gider)
#     gunluk_gelir = GunlukGelir.objects.filter(tarih=today).first()
#
#     context = {
#         'gunluk_gider': gunluk_gider,
#         'gunluk_gelir': gunluk_gelir
#     }
#
#     return render(request, 'rapor/finans_rapor.html', context)


# def gunluk_gider_hesapla(request):
#     today = date.today()
#     gunluk_gider = GunlukGider.objects.filter(tarih=today).first()
#
#
#     context = {
#         'gunluk_gider': gunluk_gider
#     }
#
#     return render(request, 'rapor/finans_rapor.html', context)

#uretim_istatistik_girisi aktif fakat artik yerine gunluk_uretim_view kullaniliyor
def uretim_istatistik_girisi(request):
    if request.method == 'POST':
        form = UretimIstatistikForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Üretim istatistiği başarıyla kaydedildi.')
            return redirect('uretim_istatistik_girisi')
        else:
            print("Form errors:", form.errors)  # Form hatalarını konsola yazdır
    else:
        form = UretimIstatistikForm()
    return render(request, 'rapor/uretim_istatistik_girisi.html', {'form': form})


#uretim_istatistik_girisi gunluk_uretim_view adiyla daha guncendi
def gunluk_uretim_view(request):
    if request.method == 'POST':
        form = GunlukUretimForm(request.POST)
        form.bolum1_formset = UretimFormSet(request.POST, prefix='bolum1')
        form.bolum2_formset = UretimFormSet(request.POST, prefix='bolum2')
        form.bolum3_formset = UretimFormSet(request.POST, prefix='bolum3')

        if form.is_valid():
            form.save()
            return redirect('uretim_listesi')  # Kendi yönlendirme URL'inizi belirtin.
    else:
        form = GunlukUretimForm()

    return render(request, 'uretim/uretim_form.html', {'form': form})
#urertim istatistik girislerin gosterildigi sayfa
def uretim_listesi(request):
    uretimler = UretimIstatistik.objects.all()
    return render(request, 'uretim/uretim_listesi.html', {'uretimler': uretimler})


@login_required
def resept_maliyet_list(request):
    # Resept_maliyet tablosundaki tüm verileri çekiyoruz
    maliyetler = Resept_maliyet.objects.all().order_by('resept_id')
    # maliyetler = Resept_maliyet.objects.all()
    return render(request, 'rapor/resept_maliyet_list.html', {'maliyetler': maliyetler})
