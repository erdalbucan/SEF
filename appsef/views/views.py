# from operator import index
# from django.http import FileResponse
# from django.db import models
# from django.utils.dateparse import parse_datetime
# from appsef.utils import günlük_sabit_maliyet_pay_hesapla
# from django.db.models.functions import Cast
# from django.contrib.auth.decorators import login_required, permission_required
# from django.views.decorators.csrf import csrf_protect
# from django.http import HttpResponse
#
# from django.utils import timezone
# import calendar
# from datetime import date
# from django.db.models import Avg, Min, Sum, F, Max, FloatField
# from django.contrib import messages
# from django.core.mail import send_mail
#
# import pandas as pd
# import numpy as np
# import csv
# import io
# import re  # Düzenli ifadeleri kullanmak için gerekli
# from django.core.files.base import ContentFile
#
# from appsef.models import (Uretim, Musteri, Resept, UretimDetay,
#                            Depo, GunlukGider, SabitGider, FormulCSVFile,
#                            Personel, PersonelGunlukCalisma, GunlukGider,
#                            GunlukGelir, UretimIstatistik, Resept_maliyet)
#
# from appsef.forms import (FormulUplCSVForm,
#                           PersonelForm,
#                           PersonelGirisSaatiForm,
#                           PersonelCikisSaatiForm,
#                           UretimIstatistikForm)

from django.shortcuts import render, redirect


#personel listesi html ye gerek olmadigina krar verdim
# def personel_listesi(request):
#     personeller = Personel.objects.all()
#     return render(request, 'personel_listesi.html', {'personeller': personeller})

def home(request):
    return render(request, 'index.html')

def admin(request):
    return render(request, 'admin/')

# #personel mesai baslama zamani girisi
# def Pgiris_saati_ekle(request):
#     if request.method == 'POST':
#         form = PersonelGirisSaatiForm(request.POST)
#         if form.is_valid():
#             personel = form.cleaned_data['personel']
#             tarih = timezone.now().date()  # Tarih bugünün tarihi olarak atanıyor
#             giris_saati = form.cleaned_data['giris_saati']
#
#             # Aynı personel için bugüne ait giriş kaydı var mı?
#             mevcut_kayit = PersonelGunlukCalisma.objects.filter(personel=personel, tarih=tarih).first()
#
#             if mevcut_kayit:
#                 # Eğer çıkış saati varsa ve giriş saati çıkış saatinden sonra ise yeni kayıt oluştur
#                 if mevcut_kayit.cikis_saati and giris_saati > mevcut_kayit.cikis_saati:
#                     # Yeni giriş kaydını oluştur
#                     yeni_kayit = PersonelGunlukCalisma.objects.create(
#                         personel=personel,
#                         tarih=tarih,
#                         giris_saati=giris_saati,
#                         cikis_saati=None  # Çıkış saati yok, daha sonra eklenecek
#                     )
#                     messages.success(request, f'{personel.ad} için yeni giriş kaydedildi: {giris_saati}')
#                     return redirect('Pgiris_saati_ekle')
#                 else:
#                     # Giriş saati çıkış saatinden önce ise hata mesajı göster
#                     messages.error(request, f'{personel.ad} için giriş saati, çıkış saatinden önce olamaz. Çıkış saati: {mevcut_kayit.cikis_saati}')
#             else:
#                 # İlk giriş kaydı oluşturuluyor
#                 calisma = form.save(commit=False)
#                 calisma.tarih = tarih  # Tarihi bugünün tarihi olarak ayarlıyoruz
#                 calisma.cikis_saati = None  # Çıkış saati yok
#                 calisma.save()
#                 messages.success(request, f'{personel.ad} için giriş saati kaydedildi: {giris_saati}')
#                 return redirect('Pgiris_saati_ekle')
#     else:
#         form = PersonelGirisSaatiForm()
#
#     return render(request, 'mesai/Pgiris_saati_ekle.html', {'form': form})
#
# #personel mesai bitirme zamani girisi
# def Pcikis_saati_ekle(request):
#     if request.method == 'POST':
#         form = PersonelCikisSaatiForm(request.POST)
#         if form.is_valid():
#             personel = form.cleaned_data['personel']
#             tarih = timezone.now().date()  # Tarih bugünün tarihi olarak atanıyor
#             cikis_saati = form.cleaned_data['cikis_saati']
#
#             # Aynı personelin bugün için çıkış saati olmayan en son giriş kaydını bulalım
#             mevcut_kayit = PersonelGunlukCalisma.objects.filter(personel=personel, tarih=tarih, cikis_saati__isnull=True).first()
#
#             if mevcut_kayit:
#                 # Çıkış saati giriş saatinden küçükse hata mesajı göster
#                 if cikis_saati <= mevcut_kayit.giris_saati:
#                     messages.error(request, f'{personel.ad} için çıkış saati, giriş saatinden küçük veya eşit olamaz. Giriş saati: {mevcut_kayit.giris_saati}')
#                 else:
#                     # Çıkış saatini kaydediyoruz
#                     mevcut_kayit.cikis_saati = cikis_saati
#                     mevcut_kayit.save()
#
#                     # Giriş ve çıkış saatlerini string formatında alıyoruz
#                     giris_saati_str = mevcut_kayit.giris_saati.strftime('%H:%M')
#                     cikis_saati_str = cikis_saati.strftime('%H:%M')
#
#                     # E-posta gönderme
#                     subject = 'Günlük Çalışma Bilgilendirmesi'
#                     message = f'{personel.ad} {personel.soyad},\n\nBugün {giris_saati_str} dan {cikis_saati_str} a kadar çalıştınız. Teşekkürler.'
#                     recipient_list = [personel.eposta]  # personelin e-posta alanı
#
#                     # E-postayı gönderiyoruz
#                     send_mail(subject, message, 'IK@seffood.fi', recipient_list)
#
#                     # Başarılı mesajı
#                     messages.success(request, f'{personel.ad} {personel.soyad} - Giriş Saati: {giris_saati_str} - Çıkış Saati: {cikis_saati_str} - Kayıt Eklenmiştir.')
#                     return redirect('Pcikis_saati_ekle')
#             else:
#                 # Eğer çıkış yapılacak bir giriş kaydı yoksa
#                 messages.error(request, f'{personel.ad} için çıkış kaydı yapılacak bir giriş bulunamadı.')
#     else:
#         form = PersonelCikisSaatiForm()
#
#     return render(request, 'mesai/Pcikis_saati_ekle.html', {'form': form})
#
# def FormulCsvupload_file(request):
#     if request.method == 'POST':
#         form = FormulUplCSVForm(request.POST, request.FILES)
#         if form.is_valid():
#             if 'file' in request.FILES:
#                 csv_file = request.FILES['file']
#                 decoded_file = csv_file.read().decode('utf-8')
#                 # Burada boş olup olmadığını kontrol edebilirsiniz
#                 if not decoded_file:
#                     raise ValueError("Boş dosya yüklendi")
#             else:
#                 raise ValueError("Dosya yüklenmedi")
#             # # Yüklenen CSV dosyasını al
#             # csv_file = request.FILES['file']
#             # decoded_file = csv_file.read().decode('utf-8')
#
#             # CSV dosyasını işlemek için bir string buffer oluştur
#             io_string = io.StringIO(decoded_file)
#
#             df = pd.read_csv(io_string, sep=';')
#             # sicak yemek ile Domates sosunu ayirmak icin ptesi domates sosu cok uretildiginden sayidan yakala
#             if len(df) >= 107 and df.iloc[107, 3] == 'TOMATO SAUCE':
#                 # Virgülü kaldırıp sayıya çevir
#                 df.iloc[116, 4] = pd.to_numeric(df.iloc[116, 4].replace(",", ""))
#
#             # # Formda seçilen değere göre `basliklar` listesini belirleyelim
#             # selected_name = form.cleaned_data['selected_name']
#             if len(df) >= 76 and df.iloc[76, 1] == 'Kilo':  # HOK
#                 selected_name = df.iloc[76, 1]
#                 df.columns = ['urun', 'Sutun_2', 'Sutun_3', 'Sutun_4']
#
#                 # Büyük toplamları Sütun_4'e taşı, Sütun_1'i boş yap
#                 for t in [16, 30, 42, 52, 60, 70]:
#                     df.at[t, 'Sutun_3'] = df.at[t, 'urun']
#                     df.at[t, 'urun'] = np.nan
#
#                 # Başlık satırlarının altına boş satır ekle
#                 baslikStr = [4, 17, 31, 43, 53, 61]
#                 for row in sorted(baslikStr, reverse=True):
#                     bsl_row = {
#                         'urun': '',  # Boş değer
#                         'Sutun_2': '',
#                         'Sutun_3': '',
#                         'Sutun_4': '',
#                     }
#                     # Yeni satırı ekle
#                     df = pd.concat([df.iloc[:row], pd.DataFrame([bsl_row]), df.iloc[row:]]).reset_index(
#                         drop=True)
#                     df.at[row, 'urun'] = df.at[row + 1, 'urun']
#                     df.at[row + 1, 'urun'] = np.nan
#
#                 # 'acordionKapa' satırlarını ekleme
#                 baslikStr = [18, 33, 46, 57, 66, 77]
#                 for row in sorted(baslikStr, reverse=True):
#                     new_row = {
#                         'urun': 'akordionKapa',
#                         'Sutun_2': np.nan,
#                         'Sutun_3': np.nan,
#                         'Sutun_4': np.nan
#                     }
#                     df = pd.concat([df.iloc[:row], pd.DataFrame([new_row]), df.iloc[row:]]).reset_index(
#                         drop=True)
#
#                 # Tüm boş hücreleri np.nan ile değiştirme
#                 df = df.replace('', np.nan)
#
#                 # Belirli aralıktaki satırları al
#                 df = df.iloc[4:83]
#
#                 # e 202 lerin silinmesi
#
#                 rows_to_delete = [79, 80, 45, 46, 31, 32, 15, 16]
#
#                 # Belirtilen satırları silmek
#                 df = df.drop(rows_to_delete)
#                 # df.loc[rows_to_delete] = None
#
#                 df.rename(columns={"Sutun_4": "Sutun_5", "Sutun_3": "Sutun_4", "Sutun_2": "Sutun_3"},
#                           inplace=True)
#
#                 # Sütun_5'i sayıya çevir
#                 # df['Sutun_5'] = pd.to_numeric(df['Sutun_5'], errors='coerce')
#                 # df['Sutun_5'] = pd.to_numeric(df['Sutun_5'], errors='coerce')
#
#                 df['Sutun_5'] = df['Sutun_5'].str.replace('.', '', regex=False)  # Noktayı kaldır
#                 df['Sutun_5'] = pd.to_numeric(df['Sutun_5'], errors='coerce')  # Sayıya çevir
#
#                 # kac urun uretilecegini hesapla
#                 # 3. satırdaki sutun_5 değerini kontrol et
#                 if df.loc[72, 'Sutun_5'] == 0:
#                     rows_to_delete = [71, 72, 73, 74, 75, 76, 77, 78, 81,
#                                       82]  # 96. satırdan 117. satıra kadar
#                     df = df.drop(rows_to_delete)
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[71, 'Sutun_3'] = int(df.loc[81, 'Sutun_5'] / 1001)
#
#                 if df.loc[62, 'Sutun_5'] == 0:
#                     rows_to_delete = [61, 62, 63, 64, 65, 66, 67, 68, 69,
#                                       70]  # 96. satırdan 117. satıra kadar
#                     df = df.drop(rows_to_delete)
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[61, 'Sutun_3'] = int(df.loc[69, 'Sutun_5'] / 1000)
#
#                 if df.loc[50, 'Sutun_5'] == 0:
#                     rows_to_delete = [49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59,
#                                       60]  # 96. satırdan 117. satıra kadar
#                     df = df.drop(rows_to_delete)
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[49, 'Sutun_3'] = int(df.loc[59, 'Sutun_5'] / 1001)
#
#                 if df.loc[36, 'Sutun_5'] == 0:
#                     rows_to_delete = [35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 47,
#                                       48]  # 96. satırdan 117. satıra kadar
#                     df = df.drop(rows_to_delete)
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[35, 'Sutun_3'] = int(df.loc[47, 'Sutun_5'] / 1001)
#
#                 if df.loc[20, 'Sutun_5'] == 0:
#                     rows_to_delete = [19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 33,
#                                       34]  # 96. satırdan 117. satıra kadar
#                     df = df.drop(rows_to_delete)
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[19, 'Sutun_3'] = int(df.loc[33, 'Sutun_5'] / 1000)
#
#                 if df.loc[5, 'Sutun_5'] == 0:
#                     rows_to_delete = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 17,
#                                       18]  # 96. satırdan 117. satıra kadar
#                     df = df.drop(rows_to_delete)
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[4, 'Sutun_3'] = int(df.loc[17, 'Sutun_5'] / 861)
#
#                 # Düzenlenmiş CSV'yi yaz
#                 df.to_csv('HokFormul.csv', sep=';', index=False, encoding='utf-8')
#
#                 # Formdan gelen `formul_tarihi`'ni al
#                 formul_tarihi = form.cleaned_data.get('formul_tarihi')
#
#                 # Tarih verisini tekrar işlemeye gerek yok, çünkü bu zaten `datetime` objesi
#                 # CSV dosyasını Django modeline kaydet
#                 with open('HokFormul.csv', 'r', encoding='utf-8') as f:
#                     csv_file_instance = FormulCSVFile.objects.create(
#                         name=selected_name,  # Name alanı otomatik oluşturuldu
#                         file=ContentFile(f.read(), 'HokFormul.csv'),
#                         Formul_tarihi=formul_tarihi,  # Formdan gelen tarih bilgisi
#                         Yukleme_tarihi=timezone.now(),  # Fonksiyonu çağırmayı unutmayın
#                     )
#                     csv_file_instance.save()
#
#             elif len(df) >= 151 and df.iloc[151, 1] == 'Kesko Salata':
#                 selected_name = df.iloc[151, 1]
#                 df.columns = ['urun', 'Sutun_3', 'Sutun_4', 'Sutun_5', 'Sutun_6', 'Sutun_7', 'Sutun_8']
#
#
#
#                 # # Küçük toplamları Sütun_4'e taşı, Sütun_2'yi boş yap
#                 # for s in [5, 7, 9, 11, 13, 16, 18, 20, 22, 24, 28, 30, 32, 34, 36, 40, 42, 44, ]:
#                 #     df.at[s, 'Sutun_4'] = df.at[s, 'Sutun_2']
#                 #     df.at[s, 'Sutun_2'] = np.nan
#
#                 # Büyük toplamları Sütun_4'e taşı, Sütun_1'i boş yap
#                 for t in [16, 30, 41, 47, 54, 68, 81, 92, 106, 116, 126, 139, 148]:
#                     df.at[t, 'Sutun_3'] = df.at[t, 'urun']
#                     df.at[t, 'urun'] = np.nan
#
#                 # Sütunları silme (Sutun_2, Sutun_6, Sutun_7, vb.)
#                 df = df.drop(['Sutun_6', 'Sutun_7', 'Sutun_8'], axis=1)
#
#                 # Başlık satırlarının altına boş satır ekle
#                 baslikStr = [4, 17, 31, 42, 48, 55, 69, 82, 93, 107, 117, 127, 140]
#                 for row in sorted(baslikStr, reverse=True):
#                     bsl_row = {
#                         'urun': '',  # Boş değer
#                         'Sutun_3': '',
#                         'Sutun_4': '',
#                     }
#                     # Yeni satırı ekle
#                     df = pd.concat([df.iloc[:row], pd.DataFrame([bsl_row]), df.iloc[row:]]).reset_index(
#                         drop=True)
#                     df.at[row, 'urun'] = df.at[row + 1, 'urun']
#                     df.at[row + 1, 'urun'] = np.nan
#
#                 # 'acordionKapa' satırlarını ekleme
#                 baslikStr = [18, 33, 45, 52, 60, 75, 89, 101, 116, 127, 138, 152, 162]
#                 for row in sorted(baslikStr, reverse=True):
#                     new_row = {
#                         'urun': 'akordionKapa',
#                         'Sutun_3': np.nan,
#                         'Sutun_4': np.nan,
#                     }
#                     df = pd.concat([df.iloc[:row], pd.DataFrame([new_row]), df.iloc[row:]]).reset_index(
#                         drop=True)
#
#                 # Tüm boş hücreleri np.nan ile değiştirme
#                 df = df.replace('', np.nan)
#
#                 # Belirli aralıktaki satırları al
#                 df = df.iloc[4:175]
#
#
#
#                 # e 202 lerin silinmesi
#                 # 13,14,21,22,29,30,34,35,47,48,73,74,80,81,100,101
#                 # rows_to_delete = [13, 14, 21, 22, 29, 30, 34, 35, 47, 48, 73, 74, 80, 81, 100, 101]
#                 rows_to_delete = [171, 172, 160, 161, 145, 146, 133, 134, 121, 122, 104, 105, 92, 93, 77, 78, 61, 62,
#                                   52, 53, 44, 45, 31, 32, 15, 16]
#
#                 # Belirtilen satırları silmek
#                 df = df.drop(rows_to_delete)
#                 # df.loc[rows_to_delete] = None
#
#
#                 # # sutunlarin adini deegiselim
#                 # df.rename(columns={"Sutun_4": "Sutun_5", "Sutun_3": "Sutun_4", "Sutun_2": "Sutun_3"},
#                 #           inplace=True)
#
#                 # Sütun_5'i sayıya çevir
#                 # df['Sutun_5'] = pd.to_numeric(df['Sutun_5'], errors='coerce')
#                 # df['Sutun_5'] = pd.to_numeric(df['Sutun_5'], errors='coerce')
#                 df['Sutun_5'] = df['Sutun_5'].str.replace('.', '').str.replace(',', '.')
#                 df['Sutun_5'] = pd.to_numeric(df['Sutun_5'], errors='coerce')
#
#                 # 173,275.3,164 ,
#                 # 171,172,160,161, 145,146,133,134,121,122,104,105,92,93, 77,78, 61,62, 52,53, 44,45,31,32,15,16,11,12
#                 # kac urun uretilecegini hesapla
#                 # 3. satırdaki sutun_5 değerini kontrol et
#                 if df.loc[165, 'Sutun_5'] == 0:
#                     rows_to_delete = [164, 165, 166, 167, 168, 169, 170, 173, 174]  # 96. satırdan 117. satıra kadar
#                     df = df.drop(rows_to_delete)
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[164, 'Sutun_3'] = int(df.loc[173, 'Sutun_5'] / 275.3)
#
#                 if df.loc[150, 'Sutun_5'] == 0:  # 162,185.3,149,
#                     rows_to_delete = [149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 162,
#                                       163]  # 96. satırdan 117. satıra kadar
#                     df = df.drop(rows_to_delete)
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[149, 'Sutun_3'] = int(df.loc[162, 'Sutun_5'] / 185.3)
#
#                 if df.loc[138, 'Sutun_5'] == 0:  # 147,275.3,137
#                     rows_to_delete = [137, 138, 139, 140, 141, 142, 143, 144, 147,
#                                       148]  # 96. satırdan 117. satıra kadar
#                     df = df.drop(rows_to_delete)
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[137, 'Sutun_3'] = int(df.loc[147, 'Sutun_5'] / 275.3)
#
#                 if df.loc[126, 'Sutun_5'] == 0:  # , 135,275,125
#                     rows_to_delete = [125, 126, 127, 128, 129, 130, 131, 132, 135,
#                                       136]  # 96. satırdan 117. satıra kadar
#                     df = df.drop(rows_to_delete)
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[125, 'Sutun_3'] = int(df.loc[135, 'Sutun_5'] / 275)
#
#                 if df.loc[110, 'Sutun_5'] == 0:  # 123, 275.2,109  ,
#                     rows_to_delete = [109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 123,
#                                       124]  # 96. satırdan 117. satıra kadar
#                     df = df.drop(rows_to_delete)
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[109, 'Sutun_3'] = int(df.loc[123, 'Sutun_5'] / 275)
#
#                 if df.loc[97, 'Sutun_5'] == 0:  # , 107, 275 ,96
#                     rows_to_delete = [96, 97, 98, 99, 100, 101, 102, 103, 106, 107,
#                                       108]  # 96. satırdan 117. satıra kadar
#                     df = df.drop(rows_to_delete)
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[96, 'Sutun_3'] = int(df.loc[107, 'Sutun_5'] / 275)
#
#                 if df.loc[82, 'Sutun_5'] == 0:  # , 94,275.3,81
#                     rows_to_delete = [81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 94,
#                                       95]  # 96. satırdan 117. satıra kadar
#                     df = df.drop(rows_to_delete)
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[81, 'Sutun_3'] = int(df.loc[94, 'Sutun_5'] / 275.3)
#
#                 if df.loc[66, 'Sutun_5'] == 0:  # ,79,275,65
#                     rows_to_delete = [65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 79,
#                                       80]  # 96. satırdan 117. satıra kadar
#                     df = df.drop(rows_to_delete)
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[65, 'Sutun_3'] = int(df.loc[79, 'Sutun_5'] / 275)
#
#                 if df.loc[57, 'Sutun_5'] == 0:  # ,   63,275,56
#                     rows_to_delete = [56, 57, 58, 59, 60, 63, 64, ]  # 96. satırdan 117. satıra kadar
#                     df = df.drop(rows_to_delete)
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[56, 'Sutun_3'] = int(df.loc[63, 'Sutun_5'] / 275)
#
#                 if df.loc[49, 'Sutun_5'] == 0:  # ,54,175.3,48
#                     rows_to_delete = [48, 49, 50, 51, 54, 55]  # 96. satırdan 117. satıra kadar
#                     df = df.drop(rows_to_delete)
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[48, 'Sutun_3'] = int(df.loc[54, 'Sutun_5'] / 175.3)
#
#                 if df.loc[36, 'Sutun_5'] == 0:  # ,46,275,35,
#                     rows_to_delete = [35, 36, 37, 38, 39, 40, 41, 42, 43, 46, 47]  # 96. satırdan 117. satıra kadar
#                     df = df.drop(rows_to_delete)
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[35, 'Sutun_3'] = int(df.loc[46, 'Sutun_5'] / 275)
#
#                 if df.loc[20, 'Sutun_5'] == 0:  # 33,215.5,19,
#                     rows_to_delete = [19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 33,
#                                       34]  # 96. satırdan 117. satıra kadar
#                     df = df.drop(rows_to_delete)
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[19, 'Sutun_3'] = int(df.loc[33, 'Sutun_5'] / 215.5)
#
#                 if df.loc[5, 'Sutun_5'] == 0:  # 17,185.5,4
#                     rows_to_delete = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 17, 18]  # 96. satırdan 117. satıra kadar
#                     df = df.drop(rows_to_delete)
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[4, 'Sutun_3'] = int(df.loc[17, 'Sutun_5'] / 215.5)
#
#                 # # Düzenlenmiş CSV'yi yeniden yaz ve ; ile ayır
#                 # output = io.StringIO()
#                 # trimmed_rows.to_csv(output, sep=';', index=False)
#                 # output.seek(0)
#
#                 # CSV'yi dosya sistemine yaz
#                 df.to_csv('KeskoFormul.csv', sep=';', index=False, encoding='utf-8')
#
#                 # Formul_tarihi = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
#                 # formdan gelen formul_tarihi'ni al
#                 formul_tarihi = form.cleaned_data['formul_tarihi']  # Formdan gelen tarih bilgisi
#
#                 # # Seçilen name'i alıyoruz
#                 # selected_name = form.cleaned_data['selected_name']
#                 # name alanı: uploaded_at + selected_name
#                 # full_name = f"{formul_tarihi} - {selected_name}"
#
#                 # Ardından, dosya sisteminde bu dosyayı Django modeline kaydetmek için:
#                 with open('KeskoFormul.csv', 'r', encoding='utf-8') as f:
#                     csv_file_instance = FormulCSVFile.objects.create(
#                         name=selected_name,  # Name alanı otomatik oluşturuldu
#                         file=ContentFile(f.read(), 'KeskoFormul.csv'),
#                         Formul_tarihi=formul_tarihi,  # Formdan gelen tarih bilgisi
#                         Yukleme_tarihi=timezone.now(),  # Fonksiyonu çağırmayı unutmayın
#                     )
#                     csv_file_instance.save()
#
#             elif len(df) >= 47 and df.iloc[47, 1] == 'Bowl Salad':
#                 selected_name = df.iloc[47, 1]
#                 df.columns = ['urun', 'Sutun_2', 'Sutun_3', 'Sutun_4', 'Sutun_5']
#
#                 # Sütun_5'i sayıya çevir
#                 # df['Sutun_5'] = pd.to_numeric(df['Sutun_5'], errors='coerce')
#
#                 # Küçük toplamları Sütun_4'e taşı, Sütun_2'yi boş yap
#                 for s in [16, 23, 30, 42, ]:
#                     df.at[s, 'Sutun_4'] = df.at[s, 'Sutun_2']
#                     df.at[s, 'Sutun_2'] = np.nan
#
#                 # Büyük toplamları Sütun_4'e taşı, Sütun_1'i boş yap
#                 for t in [17, 24, 31, 43]:
#                     df.at[t, 'Sutun_4'] = df.at[t, 'urun']
#                     df.at[t, 'urun'] = np.nan
#
#                 # Sütunları silme (Sutun_2, Sutun_6, Sutun_7, vb.)
#                 df = df.drop(['Sutun_2', ], axis=1)
#
#                 # Başlık satırlarının altına boş satır ekle
#                 baslikStr = [3, 18, 25, 32]
#                 for row in sorted(baslikStr, reverse=True):
#                     bsl_row = {
#                         'urun': '',  # Boş değer
#                         'Sutun_3': '',
#                         'Sutun_4': '',
#                         'Sutun_5': '',
#                     }
#                     # Yeni satırı ekle
#                     df = pd.concat([df.iloc[:row], pd.DataFrame([bsl_row]), df.iloc[row:]]).reset_index(
#                         drop=True)
#                     df.at[row, 'urun'] = df.at[row + 1, 'urun']
#                     df.at[row + 1, 'urun'] = np.nan
#
#                 # 'acordionKapa' satırlarını ekleme
#                 baslikStr = [19, 27, 35, 48]
#                 for row in sorted(baslikStr, reverse=True):
#                     new_row = {
#                         'urun': 'akordionKapa',
#                         'Sutun_3': np.nan,
#                         'Sutun_4': np.nan,
#                         'Sutun_5': np.nan
#                     }
#                     df = pd.concat([df.iloc[:row], pd.DataFrame([new_row]), df.iloc[row:]]).reset_index(
#                         drop=True)
#
#                 # Tüm boş hücreleri np.nan ile değiştirme
#                 df = df.replace('', np.nan)
#
#                 # Belirli aralıktaki satırları al
#                 df = df.iloc[3:52]
#
#                 # Sütun_5'i sayıya çevir
#                 # df['Sutun_5'] = pd.to_numeric(df['Sutun_5'], errors='coerce')
#                 # df['Sutun_5'] = pd.to_numeric(df['Sutun_5'], errors='coerce')
#
#                 df['Sutun_5'] = df['Sutun_5'].str.replace('.', '', regex=False)  # Noktayı kaldır
#                 df['Sutun_5'] = pd.to_numeric(df['Sutun_5'], errors='coerce')  # Sayıya çevir
#
#                 # e 202 lerin silinmesi
#                 rows_to_delete = [46, 47, 33, 34, 24, 25, 15, 16]
#
#                 # Belirtilen satırları silmek
#                 df = df.drop(rows_to_delete)
#                 # df.loc[rows_to_delete] = None
#
#                 # kac urun uretilecegini hesapla
#                 # 3. satırdaki sutun_5 değerini kontrol et
#                 if df.loc[39, 'Sutun_5'] == 0:
#                     rows_to_delete = [38, 39, 40, 41, 42, 43, 44, 45, 48, 49, 50,
#                                       51]  # 96. satırdan 117. satıra kadar
#                     df = df.drop(rows_to_delete)
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[38, 'Sutun_3'] = int(df.loc[50, 'Sutun_5'] / 275)
#
#                 if df.loc[30, 'Sutun_5'] == 0:
#                     rows_to_delete = [29, 30, 31, 32, 35, 36, 37]  # 96. satırdan 117. satıra kadar
#                     df = df.drop(rows_to_delete)
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[29, 'Sutun_3'] = int(df.loc[36, 'Sutun_5'] / 185)
#
#                 if df.loc[21, 'Sutun_5'] == 0:
#                     rows_to_delete = [20, 21, 22, 23, 26, 27]  # 96. satırdan 117. satıra kadar
#                     df = df.drop(rows_to_delete)
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[20, 'Sutun_3'] = int(df.loc[26, 'Sutun_5'] / 195)
#
#                 if df.loc[4, 'Sutun_5'] == 0:
#                     rows_to_delete = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 17, 18,
#                                       19]  # 96. satırdan 117. satıra kadar
#                     df = df.drop(rows_to_delete)
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[3, 'Sutun_3'] = int(df.loc[18, 'Sutun_5'] / 170)
#
#                 # # Düzenlenmiş CSV'yi yeniden yaz ve ; ile ayır
#                 # output = io.StringIO()
#                 # trimmed_rows.to_csv(output, sep=';', index=False)
#                 # output.seek(0)
#
#                 # CSV'yi dosya sistemine yaz
#                 df.to_csv('BlowFormul.csv', sep=';', index=False, encoding='utf-8')
#                 # Formul_tarihi = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
#                 # formdan gelen formul_tarihi'ni al
#                 formul_tarihi = form.cleaned_data['formul_tarihi']  # Formdan gelen tarih bilgisi
#
#                 # name alanı: uploaded_at + selected_name
#                 # full_name = f"{selected_name}"
#
#                 # Ardından, dosya sisteminde bu dosyayı Django modeline kaydetmek için:
#                 with open('BlowFormul.csv', 'r', encoding='utf-8') as f:
#                     csv_file_instance = FormulCSVFile.objects.create(
#                         name=selected_name,  # Name alanı otomatik oluşturuldu
#                         file=ContentFile(f.read(), 'BlowFormul.csv'),
#                         Formul_tarihi=formul_tarihi,  # Formdan gelen tarih bilgisi
#                         Yukleme_tarihi=timezone.now(),  # Fonksiyonu çağırmayı unutmayın
#                     )
#                     csv_file_instance.save()
#
#             elif len(df) >= 106 and df.iloc[106, 1] == 'Wrap':
#                 selected_name = df.iloc[106, 1]
#                 df.columns = ['urun', 'Sutun_2', 'Sutun_3', 'Sutun_4', 'Sutun_5']
#
#                 # Sütun_5'i sayıya çevir
#                 # df['Sutun_5'] = pd.to_numeric(df['Sutun_5'], errors='coerce')
#
#                 # Küçük toplamları Sütun_4'e taşı, Sütun_2'yi boş yap
#                 for s in [5, 8, 10, 19, 22, 24, 28, 31, 33, 36, 39, 41, 47, 50, 52, 57, 60, 62, 68, 71,
#                           73, 77, 80, 82,
#                           86, 89, 91, 96, 99, 101]:
#                     df.at[s, 'Sutun_4'] = df.at[s, 'Sutun_2']
#                     df.at[s, 'Sutun_2'] = np.nan
#
#                 # Büyük toplamları Sütun_4'e taşı, Sütun_1'i boş yap
#                 # BuyukToplamlar = [11,25,34,42,53,63,74,83,92,102]
#                 BuyukToplamlar = [11, 25, 35, 44, 52, 63, 73, 84, 93, 102]
#                 for t in BuyukToplamlar:
#                     df.at[t, 'Sutun_4'] = df.at[t, 'urun']
#                     df.at[t, 'urun'] = np.nan
#
#                 # Sütunları silme (Sutun_2, Sutun_6, Sutun_7, vb.)
#                 df = df.drop(['Sutun_2', ], axis=1)
#
#                 # Başlık satırlarının altına boş satır ekle
#                 # baslikStr = [3,12,26,35,43,54,64,75,84,93]
#                 baslikStr = [3, 12, 26, 36, 45, 53, 64, 74, 85, 94]
#                 for row in sorted(baslikStr, reverse=True):
#                     bsl_row = {
#                         'urun': '',  # Boş değer
#                         'Sutun_3': '',
#                         'Sutun_4': '',
#                         'Sutun_5': '',
#                     }
#                     # Yeni satırı ekle
#                     df = pd.concat([df.iloc[:row], pd.DataFrame([bsl_row]), df.iloc[row:]]).reset_index(
#                         drop=True)
#                     df.at[row, 'urun'] = df.at[row + 1, 'urun']
#                     df.at[row + 1, 'urun'] = np.nan
#
#                 # 'acordionKapa' satırlarını ekleme
#                 # baslikStr = [13,28,38,47,59,70,82,92,102,113]
#                 baslikStr = [113, 103, 93, 81, 70, 58, 49, 39, 28, 13]
#                 for row in sorted(baslikStr, reverse=True):
#                     new_row = {
#                         'urun': 'akordionKapa',
#                         'Sutun_3': np.nan,
#                         'Sutun_4': np.nan,
#                         'Sutun_5': np.nan
#                     }
#                     df = pd.concat([df.iloc[:row], pd.DataFrame([new_row]), df.iloc[row:]]).reset_index(
#                         drop=True)
#
#                 # Tüm boş hücreleri np.nan ile değiştirme
#                 df = df.replace('', np.nan)
#
#                 # Belirli aralıktaki satırları al
#                 df = df.iloc[3:123]
#
#                 # Sütun_5'i sayıya çevir
#                 # df['Sutun_5'] = pd.to_numeric(df['Sutun_5'], errors='coerce')
#                 # df['Sutun_5'] = pd.to_numeric(df['Sutun_5'], errors='coerce')
#
#                 df['Sutun_5'] = df['Sutun_5'].str.replace('.', '', regex=False)  # Noktayı kaldır
#                 df['Sutun_5'] = pd.to_numeric(df['Sutun_5'], errors='coerce')  # Sayıya çevir
#
#                 # kac urun uretilecegini hesapla
#                 # 3. satırdaki sutun_5 değerini kontrol et
#                 if df.loc[113, 'Sutun_5'] == 0:
#                     rows_to_delete = [111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121,
#                                       122]  # 96. satırdan 117. satıra kadar
#                     df = df.drop(rows_to_delete)
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[112, 'Sutun_3'] = int(df.loc[121, 'Sutun_5'] / 220)
#
#                 if df.loc[102, 'Sutun_5'] == 0:
#                     rows_to_delete = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110]
#                     df = df.drop(rows_to_delete)
#
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[101, 'Sutun_3'] = int(df.loc[110, 'Sutun_5'] / 220)
#
#                 if df.loc[89, 'Sutun_5'] == 0:
#                     rows_to_delete = [89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99]
#                     df = df.drop(rows_to_delete)
#
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[88, 'Sutun_3'] = int(df.loc[99, 'Sutun_5'] / 215)
#
#                 if df.loc[77, 'Sutun_5'] == 0:
#                     rows_to_delete = [76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88]
#                     df = df.drop(rows_to_delete)
#
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[76, 'Sutun_3'] = int(df.loc[86, 'Sutun_5'] / 220)
#
#                 if df.loc[64, 'Sutun_5'] == 0:
#                     rows_to_delete = [64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75]
#                     df = df.drop(rows_to_delete)
#
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[63, 'Sutun_3'] = int(df.loc[74, 'Sutun_5'] / 220)
#
#                 if df.loc[54, 'Sutun_5'] == 0:
#                     rows_to_delete = [51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63]
#                     df = df.drop(rows_to_delete)
#
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[53, 'Sutun_3'] = int(df.loc[61, 'Sutun_5'] / 220)
#
#                 if df.loc[43, 'Sutun_5'] == 0:
#                     rows_to_delete = [41, 42, 43, 44, 45, 46, 47, 48, 49, 50]
#                     df = df.drop(rows_to_delete)
#
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[42, 'Sutun_3'] = int(df.loc[51, 'Sutun_5'] / 220)
#
#                 if df.loc[31, 'Sutun_5'] == 0:
#                     rows_to_delete = [30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40]
#                     df = df.drop(rows_to_delete)
#
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[30, 'Sutun_3'] = int(df.loc[40, 'Sutun_5'] / 205)
#
#                 if df.loc[15, 'Sutun_5'] == 0:
#                     rows_to_delete = [14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
#                     df = df.drop(rows_to_delete)
#
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[14, 'Sutun_3'] = int(df.loc[28, 'Sutun_5'] / 220)
#
#                 if df.loc[4, 'Sutun_5'] == 0:
#                     rows_to_delete = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
#                     df = df.drop(rows_to_delete)
#
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[3, 'Sutun_3'] = int(df.loc[12, 'Sutun_5'] / 215)
#
#                 # # Düzenlenmiş CSV'yi yeniden yaz ve ; ile ayır
#                 # output = io.StringIO()
#                 # trimmed_rows.to_csv(output, sep=';', index=False)
#                 # output.seek(0)
#
#                 # CSV'yi dosya sistemine yaz
#                 df.to_csv('WrapFormul.csv', sep=';', index=False, encoding='utf-8')
#                 # Formul_tarihi = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
#                 # formdan gelen formul_tarihi'ni al
#                 formul_tarihi = form.cleaned_data['formul_tarihi']  # Formdan gelen tarih bilgisi
#
#                 # name alanı: uploaded_at + selected_name
#                 # full_name = f"{selected_name}"
#                 # Ardından, dosya sisteminde bu dosyayı Django modeline kaydetmek için:
#                 with open('WrapFormul.csv', 'r', encoding='utf-8') as f:
#                     csv_file_instance = FormulCSVFile.objects.create(
#                         name=selected_name,  # Name alanı otomatik oluşturuldu
#                         file=ContentFile(f.read(), 'WrapFormul.csv'),
#                         Formul_tarihi=formul_tarihi,  # Formdan gelen tarih bilgisi
#                         Yukleme_tarihi=timezone.now(),  # Fonksiyonu çağırmayı unutmayın
#                     )
#                     csv_file_instance.save()
#
#             elif len(df) >= 50 and df.iloc[50, 1] == 'Sandwich':
#                 selected_name = df.iloc[50, 1]
#                 df.columns = ['urun', 'Sutun_2', 'Sutun_3', 'Sutun_4', 'Sutun_5']
#
#                 # Sütun_5'i sayıya çevir
#                 # df['Sutun_5'] = pd.to_numeric(df['Sutun_5'], errors='coerce')
#
#                 # Küçük toplamları Sütun_4'e taşı, Sütun_2'yi boş yap
#                 for s in [5, 7, 9, 11, 13, 16, 18, 20, 22, 24, 28, 30, 32, 34, 36, 40, 42, 44, ]:
#                     df.at[s, 'Sutun_4'] = df.at[s, 'Sutun_2']
#                     df.at[s, 'Sutun_2'] = np.nan
#
#                 # Büyük toplamları Sütun_4'e taşı, Sütun_1'i boş yap
#                 for t in [14, 25, 37, 45, ]:
#                     df.at[t, 'Sutun_4'] = df.at[t, 'urun']
#                     df.at[t, 'urun'] = np.nan
#
#                 # Sütunları silme (Sutun_2, Sutun_6, Sutun_7, vb.)
#                 df = df.drop(['Sutun_2', ], axis=1)
#
#                 # Başlık satırlarının altına boş satır ekle
#                 baslikStr = [3, 15, 26, 38, ]
#                 for row in sorted(baslikStr, reverse=True):
#                     bsl_row = {
#                         'urun': '',  # Boş değer
#                         'Sutun_3': '',
#                         'Sutun_4': '',
#                         'Sutun_5': '',
#                     }
#                     # Yeni satırı ekle
#                     df = pd.concat([df.iloc[:row], pd.DataFrame([bsl_row]), df.iloc[row:]]).reset_index(
#                         drop=True)
#                     df.at[row, 'urun'] = df.at[row + 1, 'urun']
#                     df.at[row + 1, 'urun'] = np.nan
#
#                 # 'acordionKapa' satırlarını ekleme
#                 baslikStr = [16, 28, 41, 50]
#                 for row in sorted(baslikStr, reverse=True):
#                     new_row = {
#                         'urun': 'akordionKapa',
#                         'Sutun_3': np.nan,
#                         'Sutun_4': np.nan,
#                         'Sutun_5': np.nan
#                     }
#                     df = pd.concat([df.iloc[:row], pd.DataFrame([new_row]), df.iloc[row:]]).reset_index(
#                         drop=True)
#
#                 # Tüm boş hücreleri np.nan ile değiştirme
#                 df = df.replace('', np.nan)
#
#                 # Belirli aralıktaki satırları al
#                 df = df.iloc[3:54]
#
#                 # Sütun_5'i sayıya çevir
#                 # df['Sutun_5'] = pd.to_numeric(df['Sutun_5'], errors='coerce')
#                 # df['Sutun_5'] = pd.to_numeric(df['Sutun_5'], errors='coerce')
#
#                 df['Sutun_5'] = df['Sutun_5'].str.replace('.', '', regex=False)  # Noktayı kaldır
#                 df['Sutun_5'] = pd.to_numeric(df['Sutun_5'], errors='coerce')  # Sayıya çevir
#
#                 # kac urun uretilecegini hesapla
#                 # 52 170 44 , 42,170,30 , 28,170,17 , 15,180,3
#                 # 3. satırdaki sutun_5 değerini kontrol et
#                 if df.loc[45, 'Sutun_5'] == 0:
#                     rows_to_delete = [44, 45, 46, 47, 48, 49, 50, 51, 52,
#                                       53]  # 96. satırdan 117. satıra kadar
#                     df = df.drop(rows_to_delete)
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[44, 'Sutun_3'] = int(df.loc[52, 'Sutun_5'] / 170)
#
#                 if df.loc[31, 'Sutun_5'] == 0:
#                     rows_to_delete = [30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43]
#                     df = df.drop(rows_to_delete)
#
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[30, 'Sutun_3'] = int(df.loc[42, 'Sutun_5'] / 170)
#
#                 if df.loc[18, 'Sutun_5'] == 0:
#                     rows_to_delete = [17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
#                     df = df.drop(rows_to_delete)
#
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[17, 'Sutun_3'] = int(df.loc[28, 'Sutun_5'] / 170)
#
#                 if df.loc[4, 'Sutun_5'] == 0:
#                     rows_to_delete = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
#                     df = df.drop(rows_to_delete)
#
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[3, 'Sutun_3'] = int(df.loc[15, 'Sutun_5'] / 180)
#
#                 # # Düzenlenmiş CSV'yi yeniden yaz ve ; ile ayır
#                 # output = io.StringIO()
#                 # trimmed_rows.to_csv(output, sep=';', index=False)
#                 # output.seek(0)
#
#                 # CSV'yi dosya sistemine yaz
#                 df.to_csv('SandvicFormul.csv', sep=';', index=False, encoding='utf-8')
#                 # Formul_tarihi = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
#                 # formdan gelen formul_tarihi'ni al
#                 formul_tarihi = form.cleaned_data['formul_tarihi']  # Formdan gelen tarih bilgisi
#
#                 # name alanı: uploaded_at + selected_name
#                 # full_name = f"{selected_name}"
#
#                 # Ardından, dosya sisteminde bu dosyayı Django modeline kaydetmek için:
#                 with open('SandvicFormul.csv', 'r', encoding='utf-8') as f:
#                     csv_file_instance = FormulCSVFile.objects.create(
#                         name=selected_name,  # Name alanı otomatik oluşturuldu
#                         file=ContentFile(f.read(), 'SandvicFormul.csv'),
#                         Formul_tarihi=formul_tarihi,  # Formdan gelen tarih bilgisi
#                         Yukleme_tarihi=timezone.now(),  # Fonksiyonu çağırmayı unutmayın
#                     )
#                     csv_file_instance.save()
#
#             elif len(df) >= 8 and df.iloc[7, 0] == 'mozarella wrap':  # DONUK
#                 selected_name = "Donuk"
#                 df.insert(0, 'Boş Sütun', '')
#
#                 df.columns = ['urun', 'Sutun_2', 'Sutun_3', 'Sutun_4']
#
#                 # 'acordionKapa' satırlarını ekleme
#                 baslikStr = [16]
#                 for row in sorted(baslikStr, reverse=True):
#                     new_row = {
#                         'urun': 'akordionKapa',
#                         'Sutun_2': np.nan,
#                         'Sutun_3': np.nan,
#                         'Sutun_4': np.nan
#                     }
#                     df = pd.concat([df.iloc[:row], pd.DataFrame([new_row]), df.iloc[row:]]).reset_index(
#                         drop=True)
#
#                 # 'urun' sütununun 0. satırındaki değeri 'Donuk' olarak değiştir
#                 df.at[0, 'urun'] = 'Donuk'
#
#                 # Tüm boş hücreleri np.nan ile değiştirme
#                 df = df.replace('', np.nan)
#
#                 # Belirli aralıktaki satırları al
#                 df = df.iloc[0:17]
#
#                 # CSV'yi dosya sistemine yaz
#                 df.to_csv('donuk.csv', sep=';', index=False, encoding='utf-8')
#                 # Formul_tarihi = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
#                 # formdan gelen formul_tarihi'ni al
#                 formul_tarihi = form.cleaned_data['formul_tarihi']  # Formdan gelen tarih bilgisi
#
#                 # name alanı: uploaded_at + selected_name
#                 # full_name = f"{formul_tarihi} - {selected_name}"
#                 # full_name = f" Donuk "
#
#                 # Ardından, dosya sisteminde bu dosyayı Django modeline kaydetmek için:
#                 with open('donuk.csv', 'r', encoding='utf-8') as f:
#                     csv_file_instance = FormulCSVFile.objects.create(
#                         name=selected_name,  # Name alanı otomatik oluşturuldu
#                         file=ContentFile(f.read(), 'Donuk.csv'),
#                         Formul_tarihi=formul_tarihi,  # Formdan gelen tarih bilgisi
#                         Yukleme_tarihi=timezone.now(),  # Fonksiyonu çağırmayı unutmayın
#                     )
#                     csv_file_instance.save()
#
#             elif len(df) >= 107 and df.iloc[107, 3] == 'TOMATO SAUCE' and df.iloc[116, 4] >= 4000:  # DOMATES SOS
#                 selected_name = df.iloc[107, 3]
#                 df.columns = ['urun', 'Sutun_1', 'Sutun_2', 'Sutun_3', 'Sutun_4', 'Sutun_5', 'Sutun_6',
#                               'Sutun_7', 'Sutun_8', 'Sutun_9', 'Sutun_10']
#
#                 # 'urun' sütununun 0. satırındaki değeri 'Donuk' olarak değiştir
#                 df.at[118, 'Sutun_3'] = df.at[123, 'Sutun_1']
#                 df.at[118, 'Sutun_4'] = df.at[123, 'Sutun_2']
#                 df.at[107, 'urun'] = df.at[107, 'Sutun_3']
#
#                 # Sütunları silme (Sutun_2, Sutun_6, Sutun_7, vb.)
#                 df = df.drop(['Sutun_1', 'Sutun_2', 'Sutun_7', 'Sutun_8', 'Sutun_9', 'Sutun_10'],
#                              axis=1)
#
#                 # 'acordionKapa' satırlarını ekleme
#                 baslikStr = [119]
#                 for row in sorted(baslikStr, reverse=True):
#                     new_row = {
#                         'urun': 'akordionKapa',
#                         'Sutun_3': np.nan,
#                         'Sutun_4': np.nan,
#                         'Sutun_5': np.nan,
#                         'Sutun_6': np.nan,
#                     }
#                     df = pd.concat([df.iloc[:row], pd.DataFrame([new_row]), df.iloc[row:]]).reset_index(
#                         drop=True)
#
#                 # Tüm boş hücreleri np.nan ile değiştirme
#                 df = df.replace('', np.nan)
#
#                 # Belirli aralıktaki satırları al
#                 df = df.iloc[107:120]
#
#                 # CSV'yi dosya sistemine yaz
#                 df.to_csv('domates.csv', sep=';', index=False, encoding='utf-8')
#                 # Formul_tarihi = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
#                 # formdan gelen formul_tarihi'ni al
#                 formul_tarihi = form.cleaned_data['formul_tarihi']  # Formdan gelen tarih bilgisi
#
#                 # name alanı: uploaded_at + selected_name
#                 # full_name = f"{formul_tarihi} - {selected_name}"
#                 # full_name = f"{selected_name}"
#
#                 # Ardından, dosya sisteminde bu dosyayı Django modeline kaydetmek için:
#                 with open('domates.csv', 'r', encoding='utf-8') as f:
#                     csv_file_instance = FormulCSVFile.objects.create(
#                         name=selected_name,  # Name alanı otomatik oluşturuldu
#                         file=ContentFile(f.read(), 'Domates.csv'),
#                         Formul_tarihi=formul_tarihi,  # Formdan gelen tarih bilgisi
#                         Yukleme_tarihi=timezone.now(),  # Fonksiyonu çağırmayı unutmayın
#                     )
#                     csv_file_instance.save()
#
#             elif len(df) >= 119 and df.iloc[119, 1] == 'Sıcak Yemek':
#                 selected_name = df.iloc[119, 1]
#                 df.columns = ['urun', 'Sutun_2', 'Sutun_3', 'Sutun_4', 'Sutun_5', 'Sutun_6', 'Sutun_7',
#                               'Sutun_8',
#                               'Sutun_9', 'Sutun_10', 'Sutun_11']
#
#                 # Sütun_5'i sayıya çevir
#                 # df['Sutun_5'] = pd.to_numeric(df['Sutun_5'], errors='coerce')
#
#                 # Küçük toplamları Sütun_4'e taşı, Sütun_2'yi boş yap
#                 for s in [13, 17, 21, 25, 29, 34, 37, 47, 52, 55, 73, 80, 96, 100]:
#                     df.at[s, 'Sutun_4'] = df.at[s, 'Sutun_2']
#                     df.at[s, 'Sutun_2'] = np.nan
#
#                 # Büyük toplamları Sütun_4'e taşı, Sütun_1'i boş yap
#                 for t in [14, 22, 30, 38, 53, 74, 81, 101]:
#                     df.at[t, 'Sutun_4'] = df.at[t, 'urun']
#                     df.at[t, 'urun'] = np.nan
#
#                 # Sütunları silme (Sutun_2, Sutun_6, Sutun_7, vb.)
#                 df = df.drop(
#                     ['Sutun_2', 'Sutun_6', 'Sutun_7', 'Sutun_8', 'Sutun_9', 'Sutun_10', 'Sutun_11'],
#                     axis=1)
#
#                 # Başlık satırlarının altına boş satır ekle
#                 baslikStr = [3, 15, 23, 31, 39, 54, 75, 82]
#                 for row in sorted(baslikStr, reverse=True):
#                     bsl_row = {
#                         'urun': '',  # Boş değer
#                         'Sutun_3': '',
#                         'Sutun_4': '',
#                         'Sutun_5': '',
#                     }
#                     # Yeni satırı ekle
#                     df = pd.concat([df.iloc[:row], pd.DataFrame([bsl_row]), df.iloc[row:]]).reset_index(
#                         drop=True)
#                     df.at[row, 'urun'] = df.at[row + 1, 'urun']
#                     df.at[row + 1, 'urun'] = np.nan
#
#                 # 'acordionKapa' satırlarını ekleme
#                 baslikStr = [16, 25, 34, 43, 59, 81, 89, 110]
#                 for row in sorted(baslikStr, reverse=True):
#                     new_row = {
#                         'urun': 'akordionKapa',
#                         'Sutun_3': np.nan,
#                         'Sutun_4': np.nan,
#                         'Sutun_5': np.nan
#                     }
#                     df = pd.concat([df.iloc[:row], pd.DataFrame([new_row]), df.iloc[row:]]).reset_index(
#                         drop=True)
#
#                 # e200 ve e 202 satirlarini temizleyelim
#                 rows_to_delete = [12, 13, 22, 23, 32, 33, 39, 40, 54, 55, 82, 83, 91, 92, 113, 114]
#                 # df.loc[rows_to_delete] = None
#                 df = df.drop(rows_to_delete)
#
#                 # Tüm boş hücreleri np.nan ile değiştirme
#                 df = df.replace('', np.nan)
#
#                 # Belirli aralıktaki satırları al
#                 df = df.iloc[3:102]
#
#                 # Sütun_5'i sayıya çevir
#                 # df['Sutun_5'] = pd.to_numeric(df['Sutun_5'], errors='coerce')
#                 # df['Sutun_5'] = pd.to_numeric(df['Sutun_5'], errors='coerce')
#
#                 df['Sutun_5'] = df['Sutun_5'].str.replace('.', '', regex=False)  # Noktayı kaldır
#                 df['Sutun_5'] = pd.to_numeric(df['Sutun_5'], errors='coerce')  # Sayıya çevir
#
#                 # kac urun uretilecegini hesapla
#                 # 3. satırdaki sutun_5 değerini kontrol et
#                 if df.loc[97, 'Sutun_5'] == 0:
#                     rows_to_delete = [96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109,
#                                       110, 111, 112,
#                                       115, 116, 117]  # 96. satırdan 117. satıra kadar
#                     df = df.drop(rows_to_delete)
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[96, 'Sutun_3'] = int(df.loc[116, 'Sutun_5'] / 300)
#
#                 if df.loc[88, 'Sutun_5'] == 0:
#                     rows_to_delete = [87, 88, 89, 90, 93, 94, 95]
#                     df = df.drop(rows_to_delete)
#
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[87, 'Sutun_3'] = int(df.loc[94, 'Sutun_5'] / 300)
#
#                 if df.loc[65, 'Sutun_5'] == 0:
#                     rows_to_delete = [64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
#                                       80, 81, 84, 85,
#                                       86]
#                     df = df.drop(rows_to_delete)
#
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[64, 'Sutun_3'] = int(df.loc[85, 'Sutun_5'] / 300)
#
#                 if df.loc[48, 'Sutun_5'] == 0:
#                     rows_to_delete = [47, 48, 49, 50, 51, 52, 53, 56, 57, 58, 59, 60, 61, 62, 63]
#                     df = df.drop(rows_to_delete)
#
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[47, 'Sutun_3'] = int(df.loc[62, 'Sutun_5'] / 300)
#
#                 if df.loc[38, 'Sutun_5'] == 0:
#                     rows_to_delete = [37, 38, 41, 42, 43, 44, 45, 46]
#                     df = df.drop(rows_to_delete)
#
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[37, 'Sutun_3'] = int(df.loc[45, 'Sutun_5'] / 300)
#
#                 if df.loc[28, 'Sutun_5'] == 0:
#                     rows_to_delete = [27, 28, 29, 30, 31, 34, 35, 36]
#                     df = df.drop(rows_to_delete)
#
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[27, 'Sutun_3'] = int(df.loc[35, 'Sutun_5'] / 300)
#
#                 if df.loc[18, 'Sutun_5'] == 0:
#                     rows_to_delete = [17, 18, 19, 20, 21, 24, 25, 26]
#                     df = df.drop(rows_to_delete)
#
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[17, 'Sutun_3'] = int(df.loc[25, 'Sutun_5'] / 300)
#
#                 if df.loc[4, 'Sutun_5'] == 0:
#                     rows_to_delete = [3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 15, 16]
#                     df = df.drop(rows_to_delete)
#
#                 else:
#                     # Sayıysa, 140'a böl
#                     # Sonucu 1. satırın sutun_3 değerine yaz
#                     df.loc[3, 'Sutun_3'] = int(df.loc[15, 'Sutun_5'] / 300)
#
#                 # yukarda kac urun uretilecegini hesapladik
#
#                 # # Düzenlenmiş CSV'yi yeniden yaz ve ; ile ayır
#                 # output = io.StringIO()
#                 # trimmed_rows.to_csv(output, sep=';', index=False)
#                 # output.seek(0)
#
#                 # CSV'yi dosya sistemine yaz
#                 df.to_csv('sicakFormul.csv', sep=';', index=False, encoding='utf-8')
#                 # Formul_tarihi = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
#                 # formdan gelen formul_tarihi'ni al
#                 formul_tarihi = form.cleaned_data['formul_tarihi']  # Formdan gelen tarih bilgisi
#
#                 # name alanı: uploaded_at + selected_name
#                 # full_name = f"{selected_name}"
#
#                 # Ardından, dosya sisteminde bu dosyayı Django modeline kaydetmek için:
#                 with open('sicakFormul.csv', 'r', encoding='utf-8') as f:
#                     csv_file_instance = FormulCSVFile.objects.create(
#                         name=selected_name,  # Name alanı otomatik oluşturuldu
#                         file=ContentFile(f.read(), 'sicakFormul.csv'),
#                         Formul_tarihi=formul_tarihi,  # Formdan gelen tarih bilgisi
#                         Yukleme_tarihi=timezone.now(),  # Fonksiyonu çağırmayı unutmayın
#                     )
#                     csv_file_instance.save()
#
#             return redirect('FrmlCsvlist_files')  # Yükledikten sonra dosyaları listele
#
#     else:
#         form = FormulUplCSVForm()
#     return render(request, 'formul_Csv/FrmlCsvupload.html', {'form': form})
#
# # formullerin listelenmesi
# def FormulCsvlist_files(request):
#     # files = FormulCSVFile.objects.all()
#     files = FormulCSVFile.objects.order_by('-Formul_tarihi')[:8]
#     return render(request, 'formul_Csv/FrmlCsvlist_files.html', {'files': files})
#
# # formul detaylarinin gosterimi
# def FormulCsvview_file(request, file_id):
#     csv_file = FormulCSVFile.objects.get(id=file_id)
#
#     try:
#         # ; ile ayrılmış CSV dosyasını oku
#         df = pd.read_csv(csv_file.file.path, encoding='utf-8', on_bad_lines='skip', delimiter=';')
#     except UnicodeDecodeError:
#         # Hatalı satırları atla ve latin1 kodlaması ile dene
#         df = pd.read_csv(csv_file.file.path, encoding='latin1', on_bad_lines='skip', delimiter=';')
#
#     # 'urun' sütununda NaN olup olmadığını kontrol et ve NaN değerleri boş stringe çevir
#     df['urun'] = df['urun'].fillna('')
#
#     # Satırları ve sütun başlıklarını al
#     rows = df.to_dict(orient='records')  # Satırları bir liste olarak alır
#     columns = df.columns  # Sütun başlıklarını al
#
#     return render(request, 'formul_Csv/FrmlCsvView_file.html',
#                   {'rows': rows, 'columns': columns, 'file_name': csv_file.name})
#
#
# @csrf_protect
# @login_required
# @permission_required('raporlari_GOR.rapori_gorebilir', raise_exception=True)
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
# ###########################
#
# def finans_raporu(request):
#     today = date.today()
#     gunluk_gider = GunlukGider.objects.filter(tarih=today).first()
#     gunluk_gelir = GunlukGelir.objects.filter(tarih=today).first()
#
#     context = {
#         'gunluk_gider': gunluk_gider,
#         'gunluk_gelir': gunluk_gelir
#     }
#
#     return render(request, 'rapor/finans_rapor.html', context)
#
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
#
# def uretim_istatistik_girisi(request):
#     if request.method == 'POST':
#         form = UretimIstatistikForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Üretim istatistiği başarıyla kaydedildi.')
#             return redirect('uretim_istatistik_girisi')
#         else:
#             print("Form errors:", form.errors)  # Form hatalarını konsola yazdır
#     else:
#         form = UretimIstatistikForm()
#     return render(request, 'rapor/uretim_istatistik_girisi.html', {'form': form})
#
# @login_required
# def resept_maliyet_list(request):
#     # Resept_maliyet tablosundaki tüm verileri çekiyoruz
#     maliyetler = Resept_maliyet.objects.all().order_by('resept_id')
#     # maliyetler = Resept_maliyet.objects.all()
#     return render(request, 'rapor/resept_maliyet_list.html', {'maliyetler': maliyetler})

