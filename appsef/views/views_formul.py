# from operator import index
# from django.http import FileResponse
# from django.db import models
# from django.utils.dateparse import parse_datetime
# from appsef.utils import günlük_sabit_maliyet_pay_hesapla
# from django.db.models.functions import Cast
# from django.contrib.auth.decorators import login_required, permission_required
# from django.views.decorators.csrf import csrf_protect
# from django.http import HttpResponse
# import calendar
# from datetime import date
# from django.db.models import Avg, Min, Sum, F, Max, FloatField
# from django.contrib import messages
# from django.core.mail import send_mail
# import csv
# import re  # Düzenli ifadeleri kullanmak için gerekli

from django.utils import timezone
from django.shortcuts import render, redirect
import pandas as pd
import numpy as np
import io
from django.core.files.base import ContentFile
from appsef.forms import FormulUplCSVForm
from appsef.models import FormulCSVFile



def csv_kaydet(df, dosya_adi, formul_tarihi, selected_name):
    df.to_csv(dosya_adi, sep=';', index=False, encoding='utf-8')
    with open(dosya_adi, 'r', encoding='utf-8') as f:
        csv_file_instance = FormulCSVFile.objects.create(
            name=selected_name,
            file=ContentFile(f.read(), dosya_adi),
            Formul_tarihi=formul_tarihi,
            Yukleme_tarihi=timezone.now(),
        )
        csv_file_instance.save()
def SutunSayiCevir(df, sutunAdi):
    """
    DataFrame'deki 'Sutun_5' sütununu sayiya cevirir.

    Args:
        df (pd.DataFrame): Üzerinde işlem yapılacak DataFrame.
        sutunAdi (sutun): sayiya cevirilecek sutun adi.

    Returns:
        pd.DataFrame: Düzenlenmiş DataFrame.
    """
    # Sütun_5'i sayıya çevir
    # df['Sutun_5'] = pd.to_numeric(df['Sutun_5'], errors='coerce')
    # df['Sutun_5'] = pd.to_numeric(df['Sutun_5'], errors='coerce')

    df[sutunAdi] = df[sutunAdi].str.replace('.', '', regex=False)  # Noktayı kaldır
    df[sutunAdi] = pd.to_numeric(df[sutunAdi], errors='coerce')  # Sayıya çevir
    return df
def KucukToplamlar(df, kucukToplamlar):
    """
    DataFrame'deki belirli satırların 'Sutun_4' sütununa 'Sutun_2' sutunundaki verileri tasir.

    Args:
        df (pd.DataFrame): Üzerinde işlem yapılacak DataFrame.
        buyukToplamlar (list): kucukToplamlar satir numaralarının yer aldığı liste.

    Returns:
        pd.DataFrame: Düzenlenmiş DataFrame.
    """
    for s in kucukToplamlar:
        df.at[s, 'Sutun_4'] = df.at[s, 'Sutun_2']
        df.at[s, 'Sutun_2'] = np.nan
    return df
def BuyukToplamlr(df, buyukToplamlar):
    """
    DataFrame'deki belirli satırların 'Sutun_4' sütununa 'urun' sutunundaki verileri tasir.

    Args:
        df (pd.DataFrame): Üzerinde işlem yapılacak DataFrame.
        buyukToplamlar (list): buyukToplamlar satir numaralarının yer aldığı liste.

    Returns:
        pd.DataFrame: Düzenlenmiş DataFrame.
    """
    for t in buyukToplamlar:
        df.at[t, 'Sutun_4'] = df.at[t, 'urun']
        df.at[t, 'urun'] = np.nan
    return df
def BaslikAltinaSatirEkle(df, baslikStr):
    """
    DataFrame'deki belirli satırların altına boş bir satır ekler
    ve ilgili satırların 'urun' sütununu düzenler.

    Args:
        df (pd.DataFrame): Üzerinde işlem yapılacak DataFrame.
        baslikStr (list): Satır numaralarının yer aldığı liste.

    Returns:
        pd.DataFrame: Düzenlenmiş DataFrame.
    """
    for row in sorted(baslikStr, reverse=True):
        bsl_row = {
            'urun': '',  # Boş değer
            'Sutun_3': '',
            'Sutun_4': '',
            'Sutun_5': '',
        }
        # Yeni satırı ekle
        df = pd.concat([df.iloc[:row], pd.DataFrame([bsl_row]), df.iloc[row:]]).reset_index(drop=True)
        df.at[row, 'urun'] = df.at[row + 1, 'urun']
        df.at[row + 1, 'urun'] = np.nan
    return df
def AkordionKapa(df, akordionKapa):
    """
    DataFrame'deki belirli satırların altına boş bir satır ekler
    ve ilgili satırların 'urun' sütununa 'AkordionKapa' yazar.

    Args:
        df (pd.DataFrame): Üzerinde işlem yapılacak DataFrame.
        akordionKapa (list): akordionKapa satir numaralarının yer aldığı liste.

    Returns:
        pd.DataFrame: Düzenlenmiş DataFrame.
    """
    for row in sorted(akordionKapa, reverse=True):
        new_row = {
            'urun': 'akordionKapa',
            'Sutun_3': np.nan,
            'Sutun_4': np.nan,
            'Sutun_5': np.nan
        }
        df = pd.concat([df.iloc[:row], pd.DataFrame([new_row]), df.iloc[row:]]).reset_index(drop=True)
    return df
def KacUrunVar(df, baslik, toplamStri, bolme, silinecekler):
    if df.loc[baslik+1, 'Sutun_5'] == 0:

        df = df.drop(silinecekler)

    else:

        # Sayıysa, 140'a böl

        # Sonucu 1. satırın sutun_3 değerine yaz

        df.loc[baslik, 'Sutun_3'] = int(df.loc[toplamStri, 'Sutun_5'] / bolme)
    return df



def FormulCsvupload_file(request):
    if request.method == 'POST':
        form = FormulUplCSVForm(request.POST, request.FILES)
        if form.is_valid():
            if 'file' in request.FILES:
                csv_file = request.FILES['file']
                decoded_file = csv_file.read().decode('utf-8')
                # Burada boş olup olmadığını kontrol edebilirsiniz
                if not decoded_file:
                    raise ValueError("Boş dosya yüklendi")
            else:
                raise ValueError("Dosya yüklenmedi")
            # # Yüklenen CSV dosyasını al
            # csv_file = request.FILES['file']
            # decoded_file = csv_file.read().decode('utf-8')

            # CSV dosyasını işlemek için bir string buffer oluştur
            io_string = io.StringIO(decoded_file)

            df = pd.read_csv(io_string, sep=';')
            # sicak yemek ile Domates sosunu ayirmak icin ptesi domates sosu cok uretildiginden sayidan yakala
            if len(df) >= 107 and df.iloc[107, 3] == 'TOMATO SAUCE':
                # Virgülü kaldırıp sayıya çevir
                df.iloc[116, 4] = pd.to_numeric(df.iloc[116, 4].replace(",", ""))

            # # Formda seçilen değere göre `basliklar` listesini belirleyelim
            # selected_name = form.cleaned_data['selected_name']
            if len(df) >= 76 and df.iloc[76, 1] == 'Kilo':  # HOK
                df.columns = ['urun', 'Sutun_3', 'Sutun_4', 'Sutun_5']

                selected_name = df.iloc[76, 1]
                # kucukToplamKsk = [13, 17, 21, 25, 29, 34, 37, 47, 52, 55, 73, 80, 96, 100]
                buyukTplmKilo = [16, 30, 42, 52, 60, 70]
                baslikStrKilo = [4, 17, 31, 43, 53, 61]
                acordStrKilo = [18, 33, 46, 57, 66, 77]
                delete_202Kilo = [79, 80, 45, 46, 31, 32, 15, 16]
                urunVerileriKilo = [
                    {
                        'baslik': 71, 'toplamStri': 81, 'bolme': 1001,
                        'silinecekler': [71, 72, 73, 74, 75, 76, 77, 78, 81,82]
                    },
                    {
                        'baslik': 61, 'toplamStri': 69, 'bolme': 1000,
                        'silinecekler': [61, 62, 63, 64, 65, 66, 67, 68, 69, 70]
                    },
                    {
                        'baslik': 49, 'toplamStri': 59, 'bolme': 1001,
                        'silinecekler': [49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60]
                    },
                    {
                        'baslik': 35, 'toplamStri': 47, 'bolme': 1001,
                        'silinecekler': [35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 47,48]
                    },
                    {
                        'baslik': 19, 'toplamStri': 33, 'bolme': 1000,
                        'silinecekler': [19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 33, 34]
                    },
                    {
                        'baslik': 4, 'toplamStri': 17, 'bolme': 861,
                        'silinecekler': [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 17, 18]
                    },

                ]

                # Küçük toplamları Sütun_4'e taşı, Sütun_2'yi boş yap
                # df = KucukToplamlar(df, kucukToplamKsk)

                # Büyük toplamları Sütun_4'e taşı, Sütun_1'i boş yap
                df = BuyukToplamlr(df, buyukTplmKilo)

                # Başlık satırlarının altına boş satır ekle
                df = BaslikAltinaSatirEkle(df, baslikStrKilo)

                # 'acordionKapa' satırlarını ekleme
                df = AkordionKapa(df, acordStrKilo)

                # Belirli aralıktaki satırları al
                df = df.iloc[4:83]

                # e200 ve e 202 satirlarini temizleyelim
                df = df.drop(delete_202Kilo)

                # Sütun_5'i sayıya çevir
                SutunSayiCevir(df, 'Sutun_5')


                # kac urun uretilecegini hesapla
                for urun in urunVerileriKilo:
                    baslik = urun['baslik']
                    toplamStri = urun['toplamStri']
                    bolme = urun['bolme']
                    silinecekler = urun['silinecekler']

                    df = KacUrunVar(df, baslik, toplamStri, bolme, silinecekler)
                # yukarda kac urun uretilecegini hesapladik


                # Formdan gelen `formul_tarihi`'ni al
                formul_tarihi = form.cleaned_data.get('formul_tarihi')
                # CSV'yi dosya sistemine yaz
                csv_kaydet(df, 'Kilo.csv', formul_tarihi, selected_name)

            elif len(df) >= 151 and df.iloc[151, 1] == 'Kesko Salata':
                df.columns = ['urun', 'Sutun_3', 'Sutun_4', 'Sutun_5', 'Sutun_6', 'Sutun_7', 'Sutun_8']
                selected_name = df.iloc[151, 1]
                # kucukToplamKsk = [13, 17, 21, 25, 29, 34, 37, 47, 52, 55, 73, 80, 96, 100]
                buyukTplmKsk = [16, 30, 41, 47, 54, 68, 81, 92, 106, 116, 126, 139, 148]
                baslikStrKsk = [4, 17, 31, 42, 48, 55, 69, 82, 93, 107, 117, 127, 140]
                acordStrKsk = [18, 33, 45, 52, 60, 75, 89, 101, 116, 127, 138, 152, 162]
                delete_202Ksk = [171, 172, 160, 161, 145, 146, 133, 134, 121, 122, 104, 105, 92, 93, 77, 78, 61, 62,
                                  52, 53, 44, 45, 31, 32, 15, 16]
                urunVerileriKsk = [
                    {
                        'baslik': 164, 'toplamStri': 173, 'bolme': 275.3,
                        'silinecekler': [164, 165, 166, 167, 168, 169, 170, 173, 174]
                    },
                    {
                        'baslik': 149, 'toplamStri': 162, 'bolme': 285.3,
                        'silinecekler': [149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 162,163]
                    },
                    {
                        'baslik': 137, 'toplamStri': 147, 'bolme': 275.3,
                        'silinecekler': [137, 138, 139, 140, 141, 142, 143, 144, 147,148]
                    },
                    {
                        'baslik': 125, 'toplamStri': 135, 'bolme': 275,
                        'silinecekler': [125, 126, 127, 128, 129, 130, 131, 132, 135,136]
                    },
                    {
                        'baslik': 109, 'toplamStri': 123, 'bolme': 275,
                        'silinecekler': [109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 123, 124]
                    },
                    {
                        'baslik': 96, 'toplamStri': 107, 'bolme': 275,
                        'silinecekler': [96, 97, 98, 99, 100, 101, 102, 103, 106, 107, 108]
                    },
                    {
                        'baslik': 81, 'toplamStri': 94, 'bolme': 275.3,
                        'silinecekler': [81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 94,95]
                    },
                    {
                        'baslik': 65, 'toplamStri': 79, 'bolme': 275,
                        'silinecekler': [65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 79, 80]
                    },
                    {
                        'baslik': 56, 'toplamStri': 63, 'bolme': 275,
                        'silinecekler': [56, 57, 58, 59, 60, 63, 64, ]
                    },
                    {
                        'baslik': 48, 'toplamStri': 54, 'bolme': 175.3,
                        'silinecekler': [48, 49, 50, 51, 54, 55]
                    },
                    {
                        'baslik': 35, 'toplamStri': 46, 'bolme': 175,
                        'silinecekler': [35, 36, 37, 38, 39, 40, 41, 42, 43, 46, 47]
                    },
                    {
                        'baslik': 19, 'toplamStri': 33, 'bolme': 215.5,
                        'silinecekler': [19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 33, 34]
                    },
                    {
                        'baslik': 4, 'toplamStri': 17, 'bolme': 215.5,
                        'silinecekler': [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 17, 18]
                    },
                ]

                # Küçük toplamları Sütun_4'e taşı, Sütun_2'yi boş yap
                # df = KucukToplamlar(df, kucukToplamKsk)

                # Büyük toplamları Sütun_4'e taşı, Sütun_1'i boş yap
                df = BuyukToplamlr(df, buyukTplmKsk)

                # Başlık satırlarının altına boş satır ekle
                df = BaslikAltinaSatirEkle(df, baslikStrKsk)

                # 'acordionKapa' satırlarını ekleme
                df = AkordionKapa(df, acordStrKsk)

                # Belirli aralıktaki satırları al
                df = df.iloc[4:175]

                # e200 ve e 202 satirlarini temizleyelim
                df = df.drop(delete_202Ksk)


                # Sütun_5'i sayıya çevir
                df['Sutun_5'] = df['Sutun_5'].str.replace('.', '').str.replace(',', '.')
                df['Sutun_5'] = pd.to_numeric(df['Sutun_5'], errors='coerce')

                # Sütunları silme (Sutun_2, Sutun_6, Sutun_7, vb.)
                df = df.drop([ 'Sutun_6','Sutun_7', 'Sutun_8'], axis=1)

                # kac urun uretilecegini hesapla
                for urun in urunVerileriKsk:
                    baslik = urun['baslik']
                    toplamStri = urun['toplamStri']
                    bolme = urun['bolme']
                    silinecekler = urun['silinecekler']

                    df = KacUrunVar(df, baslik, toplamStri, bolme, silinecekler)
                # yukarda kac urun uretilecegini hesapladik


                # Formdan gelen `formul_tarihi`'ni al
                formul_tarihi = form.cleaned_data.get('formul_tarihi')
                # CSV'yi dosya sistemine yaz
                csv_kaydet(df, 'Kesko.csv', formul_tarihi, selected_name)

            elif len(df) >= 47 and df.iloc[47, 1] == 'Bowl Salad':
                df.columns = ['urun', 'Sutun_2', 'Sutun_3', 'Sutun_4', 'Sutun_5']
                selected_name = df.iloc[47, 1]
                kucukToplamB = [16, 23, 30, 42, ]
                buyukTplmB = [17, 24, 31, 43]
                baslikStrB = [3, 18, 25, 32]
                acordStrB = [19, 27, 35, 48]
                delete_202B = [46, 47, 33, 34, 24, 25, 15, 16]
                urunVerileriB = [
                    {
                        'baslik': 38, 'toplamStri': 50, 'bolme': 275,
                        'silinecekler': [38, 39, 40, 41, 42, 43, 44, 45, 48, 49, 50,51]
                    },
                    {
                        'baslik': 29, 'toplamStri': 36, 'bolme': 185,
                        'silinecekler': [29, 30, 31, 32, 35, 36, 37]
                    },
                    {
                        'baslik': 20, 'toplamStri': 26, 'bolme': 195,
                        'silinecekler': [20, 21, 22, 23, 26, 27]
                    },
                    {
                        'baslik': 3, 'toplamStri': 18, 'bolme': 170,
                        'silinecekler': [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 17, 18,19]
                    },

                ]

                # Küçük toplamları Sütun_4'e taşı, Sütun_2'yi boş yap
                df = KucukToplamlar(df, kucukToplamB)

                # Büyük toplamları Sütun_4'e taşı, Sütun_1'i boş yap
                df = BuyukToplamlr(df, buyukTplmB)

                # Sütunları silme (Sutun_2, Sutun_6, Sutun_7, vb.)
                df = df.drop(['Sutun_2', ], axis=1)

                # Başlık satırlarının altına boş satır ekle
                df = BaslikAltinaSatirEkle(df, baslikStrB)

                # 'acordionKapa' satırlarını ekleme
                df = AkordionKapa(df, acordStrB)

                # Belirli aralıktaki satırları al
                df = df.iloc[3:52]

                # e200 ve e 202 satirlarini temizleyelim
                df = df.drop(delete_202B)

                # Sütun_5'i sayıya çevir
                SutunSayiCevir(df, 'Sutun_5')

                # kac urun uretilecegini hesapla
                for urun in urunVerileriB:
                    baslik = urun['baslik']
                    toplamStri = urun['toplamStri']
                    bolme = urun['bolme']
                    silinecekler = urun['silinecekler']

                    df = KacUrunVar(df, baslik, toplamStri, bolme, silinecekler)
                # yukarda kac urun uretilecegini hesapladik

                # Formdan gelen `formul_tarihi`'ni al
                formul_tarihi = form.cleaned_data.get('formul_tarihi')
                # CSV'yi dosya sistemine yaz
                csv_kaydet(df, 'Bowl.csv', formul_tarihi, selected_name)

            elif len(df) >= 106 and df.iloc[106, 1] == 'Wrap':
                df.columns = ['urun', 'Sutun_2', 'Sutun_3', 'Sutun_4', 'Sutun_5']
                selected_name = df.iloc[106, 1]
                kucukToplamW = [5, 8, 10, 19, 22, 24, 28, 31, 33, 36, 39, 41, 47, 50, 52, 57, 60, 62, 68, 71,73, 77, 80, 82,86, 89, 91, 96, 99, 101]
                buyukTplmW = [11, 25, 35, 44, 52, 63, 73, 84, 93, 102]
                baslikStrW = [3, 12, 26, 36, 45, 53, 64, 74, 85, 94]
                acordStrW = [113, 103, 93, 81, 70, 58, 49, 39, 28, 13]
                urunVerileriW = [
                    {
                        'baslik': 112, 'toplamStri': 121, 'bolme': 220,
                        'silinecekler': [111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121,
                                      122]
                    },
                    {
                        'baslik': 101, 'toplamStri': 110, 'bolme': 220,
                        'silinecekler':[100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110]
                    },
                    {
                        'baslik': 88, 'toplamStri': 99, 'bolme': 215,
                        'silinecekler': [89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99]
                    },
                    {
                        'baslik': 76, 'toplamStri': 86, 'bolme': 220,
                        'silinecekler': [76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88]
                    },
                    {
                        'baslik': 63, 'toplamStri': 74, 'bolme': 220,
                        'silinecekler': [64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75]
                    },
                    {
                        'baslik': 53, 'toplamStri': 61, 'bolme': 220,
                        'silinecekler': [51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63]
                    },
                    {
                        'baslik': 42, 'toplamStri': 51, 'bolme': 220,
                        'silinecekler': [41, 42, 43, 44, 45, 46, 47, 48, 49, 50]
                    },
                    {
                        'baslik': 30, 'toplamStri': 40, 'bolme': 205,
                        'silinecekler': [30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40]
                    },
                    {
                        'baslik': 14, 'toplamStri': 28, 'bolme': 220,
                        'silinecekler': [14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
                    },
                    {
                        'baslik': 3, 'toplamStri': 12, 'bolme': 215,
                        'silinecekler': [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
                    },
                ]

                # Küçük toplamları Sütun_4'e taşı, Sütun_2'yi boş yap
                df = KucukToplamlar(df, kucukToplamW)

                # Büyük toplamları Sütun_4'e taşı, Sütun_1'i boş yap
                df = BuyukToplamlr(df, buyukTplmW)

                # Sütunları silme (Sutun_2, Sutun_6, Sutun_7, vb.)
                df = df.drop(['Sutun_2', ], axis=1)

                # Başlık satırlarının altına boş satır ekle
                df = BaslikAltinaSatirEkle(df, baslikStrW)

                # 'acordionKapa' satırlarını ekleme
                df = AkordionKapa(df, acordStrW)

                # Belirli aralıktaki satırları al
                df = df.iloc[3:123]

                # Sütun_5'i sayıya çevir
                SutunSayiCevir(df, 'Sutun_5')

                # kac urun uretilecegini hesapla
                for urun in urunVerileriW:
                    baslik = urun['baslik']
                    toplamStri = urun['toplamStri']
                    bolme = urun['bolme']
                    silinecekler = urun['silinecekler']

                    df = KacUrunVar(df, baslik, toplamStri, bolme, silinecekler)
                # yukarda kac urun uretilecegini hesapladik

                # Formdan gelen `formul_tarihi`'ni al
                formul_tarihi = form.cleaned_data.get('formul_tarihi')
                # CSV'yi dosya sistemine yaz
                csv_kaydet(df, 'Wrap.csv', formul_tarihi, selected_name)

            elif len(df) >= 50 and df.iloc[50, 1] == 'Sandwich':
                df.columns = ['urun', 'Sutun_2', 'Sutun_3', 'Sutun_4', 'Sutun_5']

                selected_name = df.iloc[50, 1]
                kucukToplamSnd = [5, 7, 9, 11, 13, 16, 18, 20, 22, 24, 28, 30, 32, 34, 36, 40, 42, 44, ]
                buyukTplmSnd = [14, 25, 37, 45, ]
                baslikStrSnd = [3, 15, 26, 38, ]
                acordStrSnd = [16, 28, 41, 50]
                urunVerileriSnd = [
                    {
                        'baslik': 44, 'toplamStri': 52, 'bolme': 170,
                        'silinecekler': [44, 45, 46, 47, 48, 49, 50, 51, 52, 53]
                    },
                    {
                        'baslik': 30, 'toplamStri': 42, 'bolme': 170,
                        'silinecekler': [30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43]
                    },
                    {
                        'baslik': 17, 'toplamStri': 28, 'bolme': 170,
                        'silinecekler': [17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
                    },
                    {
                        'baslik': 3, 'toplamStri': 15, 'bolme': 180,
                        'silinecekler': [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
                    },
                    {
                        'baslik': 37, 'toplamStri': 45, 'bolme': 300,
                        'silinecekler': [37, 38, 41, 42, 43, 44, 45, 46]
                    },
                    {
                        'baslik': 27, 'toplamStri': 35, 'bolme': 300,
                        'silinecekler': [27, 28, 29, 30, 31, 34, 35, 36]
                    },
                    {
                        'baslik': 17, 'toplamStri': 25, 'bolme': 300,
                        'silinecekler': [17, 18, 19, 20, 21, 24, 25, 26]
                    },
                    {
                        'baslik': 3, 'toplamStri': 15, 'bolme': 300,
                        'silinecekler': [3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 15, 16]
                    },
                ]

                # Küçük toplamları Sütun_4'e taşı, Sütun_2'yi boş yap
                df = KucukToplamlar(df, kucukToplamSnd)

                # Büyük toplamları Sütun_4'e taşı, Sütun_1'i boş yap
                df = BuyukToplamlr(df, buyukTplmSnd)

                # Sütunları silme (Sutun_2, Sutun_6, Sutun_7, vb.)
                df = df.drop(['Sutun_2', ], axis=1)

                # Başlık satırlarının altına boş satır ekle
                df = BaslikAltinaSatirEkle(df, baslikStrSnd)

                # 'acordionKapa' satırlarını ekleme
                df = AkordionKapa(df, acordStrSnd)

                # Belirli aralıktaki satırları al
                df = df.iloc[3:54]

                # Sütun_5'i sayıya çevir
                SutunSayiCevir(df, 'Sutun_5')

                # kac urun uretilecegini hesapla
                for urun in urunVerileriSnd:
                    baslik = urun['baslik']
                    toplamStri = urun['toplamStri']
                    bolme = urun['bolme']
                    silinecekler = urun['silinecekler']

                    df = KacUrunVar(df, baslik, toplamStri, bolme, silinecekler)

                # Formdan gelen `formul_tarihi`'ni al
                formul_tarihi = form.cleaned_data.get('formul_tarihi')
                # CSV'yi dosya sistemine yaz
                csv_kaydet(df, 'Sandwich.csv', formul_tarihi, selected_name)

            elif len(df) >= 8 and df.iloc[7, 0] == 'mozarella wrap':  # DONUK
                selected_name = "Donuk"
                df.insert(0, 'Boş Sütun', '')

                df.columns = ['urun', 'Sutun_2', 'Sutun_3', 'Sutun_4']

                # 'acordionKapa' satırlarını ekleme
                baslikStr = [16]
                for row in sorted(baslikStr, reverse=True):
                    new_row = {
                        'urun': 'akordionKapa',
                        'Sutun_2': np.nan,
                        'Sutun_3': np.nan,
                        'Sutun_4': np.nan
                    }
                    df = pd.concat([df.iloc[:row], pd.DataFrame([new_row]), df.iloc[row:]]).reset_index(
                        drop=True)

                # 'urun' sütununun 0. satırındaki değeri 'Donuk' olarak değiştir
                df.at[0, 'urun'] = 'Donuk'

                # Tüm boş hücreleri np.nan ile değiştirme
                df = df.replace('', np.nan)

                # Belirli aralıktaki satırları al
                df = df.iloc[0:17]

                # Formdan gelen `formul_tarihi`'ni al
                formul_tarihi = form.cleaned_data.get('formul_tarihi')
                # CSV'yi dosya sistemine yaz
                csv_kaydet(df, 'Donuk.csv', formul_tarihi, selected_name)

            elif len(df) >= 107 and df.iloc[107, 3] == 'TOMATO SAUCE' and df.iloc[116, 4] >= 4000:  # DOMATES SOS
                selected_name = df.iloc[107, 3]
                df.columns = ['urun', 'Sutun_1', 'Sutun_2', 'Sutun_3', 'Sutun_4', 'Sutun_5', 'Sutun_6',
                              'Sutun_7', 'Sutun_8', 'Sutun_9', 'Sutun_10']

                # 'urun' sütununun 0. satırındaki değeri 'Donuk' olarak değiştir
                df.at[118, 'Sutun_3'] = df.at[123, 'Sutun_1']
                df.at[118, 'Sutun_4'] = df.at[123, 'Sutun_2']
                df.at[107, 'urun'] = df.at[107, 'Sutun_3']

                # Sütunları silme (Sutun_2, Sutun_6, Sutun_7, vb.)
                df = df.drop(['Sutun_1', 'Sutun_2', 'Sutun_7', 'Sutun_8', 'Sutun_9', 'Sutun_10'],
                             axis=1)

                # 'acordionKapa' satırlarını ekleme
                baslikStr = [119]
                for row in sorted(baslikStr, reverse=True):
                    new_row = {
                        'urun': 'akordionKapa',
                        'Sutun_3': np.nan,
                        'Sutun_4': np.nan,
                        'Sutun_5': np.nan,
                        'Sutun_6': np.nan,
                    }
                    df = pd.concat([df.iloc[:row], pd.DataFrame([new_row]), df.iloc[row:]]).reset_index(
                        drop=True)

                # Tüm boş hücreleri np.nan ile değiştirme
                df = df.replace('', np.nan)

                # Belirli aralıktaki satırları al
                df = df.iloc[107:120]

                # Formdan gelen `formul_tarihi`'ni al
                formul_tarihi = form.cleaned_data.get('formul_tarihi')
                # CSV'yi dosya sistemine yaz
                csv_kaydet(df, 'DomatesSos.csv', formul_tarihi, selected_name)

            elif len(df) >= 119 and df.iloc[119, 1] == 'Sıcak Yemek':
                df.columns = ['urun', 'Sutun_2', 'Sutun_3', 'Sutun_4', 'Sutun_5', 'Sutun_6', 'Sutun_7', 'Sutun_8',
                              'Sutun_9', 'Sutun_10', 'Sutun_11']

                selected_name = df.iloc[119, 1]
                kucukToplamS = [13, 17, 21, 25, 29, 34, 37, 47, 52, 55, 73, 80, 96, 100]
                buyukTplmS = [14, 22, 30, 38, 53, 74, 81, 101]
                baslikStrS = [3, 15, 23, 31, 39, 54, 75, 82]
                acordStrS = [16, 25, 34, 43, 59, 81, 89, 110]
                delete_202 = [12, 13, 22, 23, 32, 33, 39, 40, 54, 55, 82, 83, 91, 92, 113, 114]
                urunVerileriSicak = [
                    {
                        'baslik': 96, 'toplamStri': 116, 'bolme': 300,
                        'silinecekler': [96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111,
                                         112, 115, 116, 117]
                    },
                    {
                        'baslik': 87, 'toplamStri': 94, 'bolme': 300,
                        'silinecekler': [87, 88, 89, 90, 93, 94, 95]
                    },
                    {
                        'baslik': 64, 'toplamStri': 85, 'bolme': 300,
                        'silinecekler': [64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 84, 85,
                                         86]
                    },
                    {
                        'baslik': 47, 'toplamStri': 62, 'bolme': 300,
                        'silinecekler': [47, 48, 49, 50, 51, 52, 53, 56, 57, 58, 59, 60, 61, 62, 63]
                    },
                    {
                        'baslik': 37, 'toplamStri': 45, 'bolme': 300,
                        'silinecekler': [37, 38, 41, 42, 43, 44, 45, 46]
                    },
                    {
                        'baslik': 27, 'toplamStri': 35, 'bolme': 300,
                        'silinecekler': [27, 28, 29, 30, 31, 34, 35, 36]
                    },
                    {
                        'baslik': 17, 'toplamStri': 25, 'bolme': 300,
                        'silinecekler': [17, 18, 19, 20, 21, 24, 25, 26]
                    },
                    {
                        'baslik': 3, 'toplamStri': 15, 'bolme': 300,
                        'silinecekler': [3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 15, 16]
                    },
                ]

                # Küçük toplamları Sütun_4'e taşı, Sütun_2'yi boş yap
                df = KucukToplamlar(df,kucukToplamS)

                # Büyük toplamları Sütun_4'e taşı, Sütun_1'i boş yap
                df = BuyukToplamlr(df, buyukTplmS)

                # Başlık satırlarının altına boş satır ekle
                df = BaslikAltinaSatirEkle(df, baslikStrS)

                # 'acordionKapa' satırlarını ekleme
                df = AkordionKapa(df, acordStrS)


                # e200 ve e 202 satirlarini temizleyelim
                df = df.drop(delete_202)

                # Belirli aralıktaki satırları al
                df = df.iloc[3:102]



                # Sütun_5'i sayıya çevir
                SutunSayiCevir(df, 'Sutun_5')

                # Sütunları silme (Sutun_2, Sutun_6, Sutun_7, vb.)
                df = df.drop(['Sutun_2', 'Sutun_6', 'Sutun_7', 'Sutun_8', 'Sutun_9', 'Sutun_10', 'Sutun_11'],axis=1)

                # kac urun uretilecegini hesapla
                for urun in urunVerileriSicak:
                    baslik = urun['baslik']
                    toplamStri = urun['toplamStri']
                    bolme = urun['bolme']
                    silinecekler = urun['silinecekler']

                    df = KacUrunVar(df, baslik, toplamStri, bolme, silinecekler)
                # yukarda kac urun uretilecegini hesapladik

                # Formdan gelen `formul_tarihi`'ni al
                formul_tarihi = form.cleaned_data.get('formul_tarihi')
                # CSV'yi dosya sistemine yaz
                csv_kaydet(df, 'SicakYemek.csv', formul_tarihi, selected_name)

            return redirect('FrmlCsvlist_files')  # Yükledikten sonra dosyaları listele

    else:
        form = FormulUplCSVForm()
    return render(request, 'formul_Csv/FrmlCsvupload.html', {'form': form})

# formullerin listelenmesi
def FormulCsvlist_files(request):
    # files = FormulCSVFile.objects.all()
    files = FormulCSVFile.objects.order_by('-Formul_tarihi')[:8]
    return render(request, 'formul_Csv/FrmlCsvlist_files.html', {'files': files})

# formul detaylarinin gosterimi
def FormulCsvview_file(request, file_id):
    csv_file = FormulCSVFile.objects.get(id=file_id)

    try:
        # ; ile ayrılmış CSV dosyasını oku
        df = pd.read_csv(csv_file.file.path, encoding='utf-8', on_bad_lines='skip', delimiter=';')
    except UnicodeDecodeError:
        # Hatalı satırları atla ve latin1 kodlaması ile dene
        df = pd.read_csv(csv_file.file.path, encoding='latin1', on_bad_lines='skip', delimiter=';')

    # 'urun' sütununda NaN olup olmadığını kontrol et ve NaN değerleri boş stringe çevir
    df['urun'] = df['urun'].fillna('')

    # Satırları ve sütun başlıklarını al
    rows = df.to_dict(orient='records')  # Satırları bir liste olarak alır
    columns = df.columns  # Sütun başlıklarını al

    return render(request, 'formul_Csv/FrmlCsvView_file.html',
                  {'rows': rows, 'columns': columns, 'file_name': csv_file.name})
