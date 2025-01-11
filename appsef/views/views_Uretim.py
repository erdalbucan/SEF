import csv
import io
import numpy as np
import pandas as pd
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from appsef.forms import UretimSayiYuklemeForm,SiparisForm
from appsef.models import Uretim, UretimDetay, Musteri, Resept, bugunku_uretim_resept_hammaddeleri, uretim_urun_grubu_detaylari,Siparis  #Tarih, ReceteGrubu, ReceteFormul
from django.contrib.auth.decorators import login_required



def uretim_sayi_yukleme_view(request):
    if request.method == 'POST':
        form = UretimSayiYuklemeForm(request.POST, request.FILES)
        if form.is_valid():
            if 'csv_file' in request.FILES:  # Formdaki alanın adı 'csv_file' olmalı
                csv_file = request.FILES['csv_file']
                try:
                    decoded_file = csv_file.read().decode('utf-8')
                    if not decoded_file.strip():
                        messages.error(request, "Boş dosya yüklendi, lütfen geçerli bir dosya yükleyin.")
                        return redirect('uretim_sayi_yukleme')

                    io_string = io.StringIO(decoded_file)
                    df = pd.read_csv(io_string, sep=';')

                    # İlk 10 sütunu alıyoruz ve sütun adlarını güncelliyoruz
                    df = df.iloc[:, :10]
                    df.columns = ['Uresept', 'kategori', 'Sutun_3', 'Uismi', 'Sutun_5', 'musteri_adi', 'Sutun_7',
                                  'resept_fiyati', 'BGram', 'miktar']

                    # 'Uresept' sütunu boş olan satırları siliyoruz
                    df = df.dropna(subset=['Uresept'])

                    # İkinci satırı siliyoruz
                    df = df.drop(index=1)

                    # İstenmeyen sütunları siliyoruz
                    df = df.drop(['kategori', 'Sutun_3', 'Sutun_5', 'BGram', 'Sutun_7'], axis=1)

                    # Tüm boş hücreleri NaN ile değiştiriyoruz
                    df = df.replace('', np.nan)

                    # 'resept_fiyati' sütunundaki virgülleri nokta ile değiştiriyoruz ve sayıya çeviriyoruz
                    df['resept_fiyati'] = df['resept_fiyati'].str.replace(',', '.', regex=False)
                    df['resept_fiyati'] = pd.to_numeric(df['resept_fiyati'], errors='coerce')
                    df['resept_fiyati'] = df['resept_fiyati'].round(2)

                    # 'miktar' sütunundaki noktaları kaldırıp sayıya çeviriyoruz
                    df['miktar'] = df['miktar'].str.replace('.', '', regex=False)
                    df['miktar'] = pd.to_numeric(df['miktar'], errors='coerce')
                    # original_numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 78, 18, 19, 20, 21,
                    #                     22, 23, 24, 25, 26, 27,
                    #                     28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
                    #                     48, 49, 50, 51, 52,
                    #                     53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72,
                    #                     73, 74, 75, 76, 77,
                    #                     79, 80, 81, 82, 83, 84, 85, 86]
                    original_numbers = [1,2,3,4,5,6,7,8,9,10,11,12,13,35,
                                        36,37,38,39,68,69,70,71,19,20,21,22,23,76,93,94,95,96,97,98,
                                        99,100,14,15,16,17,18,78,29,30,31,32,33,34,72,73,74,75,24,25,
                                        26,27,28,77,47,48,49,50,79,80,81,82,88,83,84,41,44,45,46,60,61,
                                        62,63,64,65,66,67,85,86,87,51,54,56,58,59,52,53,55,57,89,90,91,92]

                    new_numbers = [1101,1102,1103,1104,1105,1106,1107,1108,
                                    1109,1110,1111,1112,1113,1201,1202,1203,1204,1205,1206,1207,1208,1209,1210,
                                    1301,1302,1303,1304,1305,1306,1401,1402,1403,1404,1405,1406,1407,1408,2101,
                                    2102,2103,2104,2105,2106,2201,2202,2203,2204,2205,2206,2207,2208,2209,2210,
                                    2301,2302,2303,2304,2306,2401,2402,2403,2404,2450,2451,2452,2453,2454,2460,
                                    2461,2501,2502,2503,2504,2505,2506,2601,2602,2603,2604,2605,2606,2607,2608,
                                    2609,2610,2611,2701,2702,2703,2704,2705,3101,3102,3103,3104,4101,4102,4103,4104]

                    # Yeni Uresept sayıları
                    # new_numbers = [1101, 1102, 1103, 1104, 1105, 1106, 1107, 1108, 1109, 1110, 1111, 1112, 1113, 1201,
                    #                1202, 1203, 1204,
                    #                1205, 1206, 1207, 1208, 1209, 1210, 1301, 1302, 1303, 1304, 1305, 1306, 3101, 3102,
                    #                3103, 3104, 2601,
                    #                2602, 2603, 2604, 2605, 2606, 2607, 2608, 2501, 2502, 2503, 2504, 2505, 2506, 2701,
                    #                2702, 2703, 2704,
                    #                2705, 2101, 2102, 2103, 2104, 2105, 2106, 2401, 2402, 2403, 2404, 2201, 2202, 2203,
                    #                2204, 2205, 2206,
                    #                2207, 2208, 2209, 2210, 2301, 2302, 2303, 2304, 2305, 2306,
                    #                2410, 2409, 2408, 2407, 2406, 2405, 2609, 2610]
                    df['Uresept'] = pd.to_numeric(df['Uresept'], errors='coerce')
                    # Mevcut Uresept numaralarını yeni numaralarla değiştirme
                    replace_map = dict(zip(original_numbers, new_numbers))
                    df['Uresept'] = df['Uresept'].replace(replace_map)
                    # 'miktar' sütunundaki NaN değerleri olan satırları silelim
                    df = df.dropna(subset=['miktar'])

                    # Her satırı işleme
                    for index, row in df.iterrows():
                        musteri_adi = row['musteri_adi']
                        # uretim_tarihi = timezone.now()  # Bugünün tarihi
                        uretim_tarihi = form.cleaned_data['uretim_tarihi']# Formdan alınan üretim tarihi
                        uresept_id = row['Uresept']
                        miktar = int(row['miktar'])
                        resept_fiyati = Decimal(row['resept_fiyati'])

                        # Müşteri ve Reçete verilerini bul veya oluştur
                        try:
                            musteri = Musteri.objects.get(musteri_adi=musteri_adi)
                        except Musteri.DoesNotExist:
                            messages.error(request, f"Müşteri bulunamadı: {musteri_adi}")
                            continue

                        try:
                            resept = Resept.objects.get(id=uresept_id)
                        except Resept.DoesNotExist:
                            messages.error(request, f"Reçete bulunamadı: {uresept_id}")
                            continue

                        # Uretim kaydını oluştur veya bul
                        uretim, created = Uretim.objects.get_or_create(
                            musteri=musteri,
                            uretim_tarihi=uretim_tarihi
                        )

                        # UretimDetay kaydını oluştur
                        uretim_detay = UretimDetay(
                            Udetay=uretim,
                            Uresept=resept,
                            miktar=miktar,
                            resept_fiyati=resept_fiyati
                        )

                        # UretimDetay'i kaydedip save işlemini tetikleyelim
                        uretim_detay.save()

                    messages.success(request, "Yükleme dosyasındaki veriler başarıyla kaydedildi.")
                    return redirect('uretim_sayi_yukleme')

                except Exception as e:
                    messages.error(request, f"Dosya işlenirken bir hata oluştu: {str(e)}")
                    return redirect('uretim_sayi_yukleme')

            else:
                messages.error(request, "Dosya yüklenmedi. Lütfen bir CSV dosyası seçin.")
                return redirect('uretim_sayi_yukleme')

    else:
        form = UretimSayiYuklemeForm()

    return render(request, 'Uretim/uretim_sayi_yukle.html', {'form': form})


def hammadde_formul(request):
    resept_gruplari = bugunku_uretim_resept_hammaddeleri()
    return render(request, 'Uretim/hammadde_formul.html', {'resept_gruplari': resept_gruplari})



# def tarih_list(request):
#     """
#     ÜretimDetay tablosundan tüm tarihleri listele.
#     """
#     tarihler = UretimDetay.objects.values_list('tarih', flat=True).distinct()
#     return render(request, 'uretim/tarih_list.html', {'tarihler': tarihler})
# def urun_grup_list(request, uretim_tarihi):
#     """
#     Belirli bir üretim tarihine göre ürün gruplarını (Urn_kategori) listele.
#     """
#     urun_kategorileri = Resept.objects.filter(
#         uretimdetay__tarih=uretim_tarihi
#     ).values('Urn_kategori').distinct()
#     return render(request, 'uretim/urun_grup_list.html', {
#         'uretim_tarihi': uretim_tarihi,
#         'urun_kategorileri': urun_kategorileri,
#     })
#
# def resept_list(request, kategori_id):
#     """
#     Belirli bir kategoriye göre reçeteleri ve reçete formüllerini listele.
#     """
#     reseptler = Resept.objects.filter(Urn_kategori=kategori_id)
#     return render(request, 'uretim/resept_list.html', {'reseptler': reseptler})

def resept_list(request, kategori_id):
    """
    Belirli bir kategoriye göre reçeteleri ve reçete formüllerini listele.
    """
    reseptler = Resept.objects.filter(Urn_kategori=kategori_id)
    # UretimDetay modelinde uretim_tarihi yerine tarih alanını kullanıyoruz
    uretim_tarihi = reseptler.first().uretimdetay_set.first().tarih if reseptler.exists() else None
    return render(request, 'uretim/resept_list.html', {
        'reseptler': reseptler,
        'uretim_tarihi': uretim_tarihi,
    })
def tarih_list(request):
    """
    ÜretimDetay tablosundan benzersiz tarihleri listele.
    """
    tarihler = UretimDetay.objects.values_list('tarih', flat=True).distinct()
    return render(request, 'uretim/tarih_list.html', {'tarihler': tarihler})
def urun_grup_list(request, tarih):
    """
    Belirli bir tarihe göre ürün gruplarını listele.
    """
    urun_gruplari = Resept.objects.filter(uretimdetay__tarih=tarih).values('Urn_kategori').distinct()
    return render(request, 'uretim/urun_grup_list.html', {
        'tarih': tarih,
        'urun_gruplari': urun_gruplari,
    })

def urun_grubu_detaylari_view(request, tarih, urun_grubu):
    """
    Belirli bir tarih ve ürün grubuna ait detayları listele.
    """
    detaylar = uretim_urun_grubu_detaylari(tarih=tarih, urun_grubu=urun_grubu)
    return render(request, 'uretim/urun_grubu_detaylari.html', {'detaylar': detaylar})






@login_required
def siparis_gecmisi(request):
    siparisler = request.user.siparisler.all().order_by('-tarih')
    return render(request, 'Uretim/siparis_gecmisi.html', {'siparisler': siparisler})


@login_required
def siparis_ver(request):
    if request.method == "POST":
        form = SiparisForm(request.POST)
        if form.is_valid():
            urun = form.cleaned_data['urun']
            miktar = form.cleaned_data['miktar']
            Siparis.objects.create(
                kullanici=request.user,
                urun=urun,
                miktar=miktar
            )
            return redirect('siparis_gecmisi')
    else:
        form = SiparisForm()
    return render(request, 'Uretim/siparis_ver.html', {'form': form})

