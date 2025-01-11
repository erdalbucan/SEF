from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal
import pandas as pd
import io
from datetime import datetime,timedelta
from django.core.mail import send_mail
from appsef.forms import PersonelGirisSaatiForm, PersonelCikisSaatiForm, PersonelMesaiPlanForm
from appsef.models import PersonelGunlukCalisma,Personel,GunlukGider

#personel mesai baslama zamani girisi
def Pgiris_saati_ekle(request):
    if request.method == 'POST':
        form = PersonelGirisSaatiForm(request.POST)
        if form.is_valid():
            personel = form.cleaned_data['personel']
            tarih = timezone.now().date()  # Tarih bugünün tarihi olarak atanıyor
            giris_saati = form.cleaned_data['giris_saati']

            # Aynı personel için bugüne ait giriş kaydı var mı?
            mevcut_kayit = PersonelGunlukCalisma.objects.filter(personel=personel, tarih=tarih).first()

            if mevcut_kayit:
                # Eğer çıkış saati varsa ve giriş saati çıkış saatinden sonra ise yeni kayıt oluştur
                if mevcut_kayit.cikis_saati and giris_saati > mevcut_kayit.cikis_saati:
                    # Yeni giriş kaydını oluştur
                    yeni_kayit = PersonelGunlukCalisma.objects.create(
                        personel=personel,
                        tarih=tarih,
                        giris_saati=giris_saati,
                        cikis_saati=None  # Çıkış saati yok, daha sonra eklenecek
                    )
                    messages.success(request, f'{personel.ad} için yeni giriş kaydedildi: {giris_saati}')
                    return redirect('Pgiris_saati_ekle')
                else:
                    # Giriş saati çıkış saatinden önce ise hata mesajı göster
                    messages.error(request, f'{personel.ad} için giriş saati, çıkış saatinden önce olamaz. Çıkış saati: {mevcut_kayit.cikis_saati}')
            else:
                # İlk giriş kaydı oluşturuluyor
                calisma = form.save(commit=False)
                calisma.tarih = tarih  # Tarihi bugünün tarihi olarak ayarlıyoruz
                calisma.cikis_saati = None  # Çıkış saati yok
                calisma.save()
                messages.success(request, f'{personel.ad} için giriş saati kaydedildi: {giris_saati}')
                return redirect('Pgiris_saati_ekle')
    else:
        form = PersonelGirisSaatiForm()

    return render(request, 'mesai/Pgiris_saati_ekle.html', {'form': form})
#personel mesai bitirme zamani girisi
def Pcikis_saati_ekle(request):
    if request.method == 'POST':
        form = PersonelCikisSaatiForm(request.POST)
        if form.is_valid():
            personel = form.cleaned_data['personel']
            tarih = timezone.now().date()  # Tarih bugünün tarihi olarak atanıyor
            cikis_saati = form.cleaned_data['cikis_saati']

            # Aynı personelin bugün için çıkış saati olmayan en son giriş kaydını bulalım
            mevcut_kayit = PersonelGunlukCalisma.objects.filter(personel=personel, tarih=tarih, cikis_saati__isnull=True).first()

            if mevcut_kayit:
                # Çıkış saati giriş saatinden küçükse hata mesajı göster
                if cikis_saati <= mevcut_kayit.giris_saati:
                    messages.error(request, f'{personel.ad} için çıkış saati, giriş saatinden küçük veya eşit olamaz. Giriş saati: {mevcut_kayit.giris_saati}')
                else:
                    # Çıkış saatini kaydediyoruz
                    mevcut_kayit.cikis_saati = cikis_saati
                    mevcut_kayit.save()

                    # Giriş ve çıkış saatlerini string formatında alıyoruz
                    giris_saati_str = mevcut_kayit.giris_saati.strftime('%H:%M')
                    cikis_saati_str = cikis_saati.strftime('%H:%M')

                    # E-posta gönderme
                    subject = 'Günlük Çalışma Bilgilendirmesi'
                    message = f'{personel.ad} {personel.soyad},\n\nBugün {giris_saati_str} dan {cikis_saati_str} a kadar çalıştınız. Teşekkürler.'
                    recipient_list = [personel.eposta]  # personelin e-posta alanı

                    # E-postayı gönderiyoruz
                    send_mail(subject, message, 'IK@seffood.fi', recipient_list)

                    # Başarılı mesajı
                    messages.success(request, f'{personel.ad} {personel.soyad} - Giriş Saati: {giris_saati_str} - Çıkış Saati: {cikis_saati_str} - Kayıt Eklenmiştir.')
                    return redirect('Pcikis_saati_ekle')
            else:
                # Eğer çıkış yapılacak bir giriş kaydı yoksa
                messages.error(request, f'{personel.ad} için çıkış kaydı yapılacak bir giriş bulunamadı.')
    else:
        form = PersonelCikisSaatiForm()

    return render(request, 'mesai/Pcikis_saati_ekle.html', {'form': form})



## alttaki fonksyonlar haftaalik mesaiyi otomayik girmek icin
# Pazartesi için veri temizleme fonksiyonu
def pazartesi_Mesai_plan(df):

    # print(f"Sütunlar: {df.columns}")  # Mevcut sütun adlarını konsola yazdırıyoruz

    df.columns = ['PersonelID', 'Sutun1', 'TarihPtsi', 'GirisPtsi', 'CikisPtsi', 'TarihSli', 'GirisSli', 'CikisSali',
                  'TarihCrs', 'GirisCrs', 'CikisCrs', 'TarihPrs', 'GirisPrs', 'CikisPrs', 'TarihCuma', 'GirisCuma',
                  'CikisCuma']

    # Giriş saatlerinin yerlerini tarihlerle değiştiriyoruz
    df.at[2, 'GirisPtsi'] = df.at[1, 'TarihPtsi']
    df_pazartesi = df[['PersonelID', 'TarihPtsi', 'GirisPtsi', 'CikisPtsi']]
    df_pazartesi.columns = ['PersonelID', 'Tarih', 'GirisSaati', 'CikisSaati']

    df = df.drop(index=[0, 1])

    pazartesi_verileri = []
    for index, row in df.iterrows():
        if pd.notna(row['GirisPtsi']) and pd.notna(row['PersonelID']):
            personel_id = row['PersonelID']
            giris_saati = row['GirisPtsi']
            cikis_saati = row['CikisPtsi']
            tarih = df.loc[2, 'GirisPtsi']  # Tarih 2. satırda belirtiliyor

            pazartesi_verileri.append({
                'PersonelID': personel_id,
                'Tarih': tarih,
                'GirisSaati': giris_saati,
                'CikisSaati': cikis_saati
            })

    df_pazartesi = pd.DataFrame(pazartesi_verileri)
    return df_pazartesi
# Salı için veri temizleme fonksiyonu
def sali_Mesai_plan(df):

    # print(f"Sütunlar: {df.columns}")  # Mevcut sütun adlarını konsola yazdırıyoruz

    df.columns = ['PersonelID', 'Sutun1', 'TarihPtsi', 'GirisPtsi', 'CikisPtsi', 'TarihSli', 'GirisSli', 'CikisSali',
                  'TarihCrs', 'GirisCrs', 'CikisCrs', 'TarihPrs', 'GirisPrs', 'CikisPrs', 'TarihCuma', 'GirisCuma',
                  'CikisCuma']

    # Giriş saatlerinin yerlerini tarihlerle değiştiriyoruz
    df.at[2, 'GirisSli'] = df.at[1, 'TarihSli']
    df_sali = df[['PersonelID', 'TarihSli', 'GirisSli', 'CikisSali']]
    df_sali.columns = ['PersonelID', 'Tarih', 'GirisSaati', 'CikisSaati']

    df = df.drop(index=[0, 1])

    sali_verileri = []
    for index, row in df.iterrows():
        if pd.notna(row['GirisSli']) and pd.notna(row['PersonelID']):
            personel_id = row['PersonelID']
            giris_saati = row['GirisSli']
            cikis_saati = row['CikisSali']
            tarih = df.loc[2, 'GirisSli']  # Tarih 2. satırda belirtiliyor

            sali_verileri.append({
                'PersonelID': personel_id,
                'Tarih': tarih,
                'GirisSaati': giris_saati,
                'CikisSaati': cikis_saati
            })

    df_sali = pd.DataFrame(sali_verileri)
    return df_sali
# Çarşamba için veri temizleme fonksiyonu
def carsamba_Mesai_plan(df):

    # print(f"Sütunlar: {df.columns}")  # Mevcut sütun adlarını konsola yazdırıyoruz

    df.columns = ['PersonelID', 'Sutun1', 'TarihPtsi', 'GirisPtsi', 'CikisPtsi', 'TarihSli', 'GirisSli', 'CikisSali',
                  'TarihCrs', 'GirisCrs', 'CikisCrs', 'TarihPrs', 'GirisPrs', 'CikisPrs', 'TarihCuma', 'GirisCuma',
                  'CikisCuma']

    # Giriş saatlerinin yerlerini tarihlerle değiştiriyoruz
    df.at[2, 'GirisCrs'] = df.at[1, 'TarihCrs']
    df_carsamba = df[['PersonelID', 'TarihCrs', 'GirisCrs', 'CikisCrs']]
    df_carsamba.columns = ['PersonelID', 'Tarih', 'GirisSaati', 'CikisSaati']

    df = df.drop(index=[0, 1])

    carsamba_verileri = []
    for index, row in df.iterrows():
        if pd.notna(row['GirisCrs']) and pd.notna(row['PersonelID']):
            personel_id = row['PersonelID']
            giris_saati = row['GirisCrs']
            cikis_saati = row['CikisCrs']
            tarih = df.loc[2, 'GirisCrs']  # Tarih 2. satırda belirtiliyor

            carsamba_verileri.append({
                'PersonelID': personel_id,
                'Tarih': tarih,
                'GirisSaati': giris_saati,
                'CikisSaati': cikis_saati
            })

    df_carsamba = pd.DataFrame(carsamba_verileri)
    return df_carsamba
# Perşembe için veri temizleme fonksiyonu
def persembe_Mesai_plan(df):

    # print(f"Sütunlar: {df.columns}")  # Mevcut sütun adlarını konsola yazdırıyoruz

    df.columns = ['PersonelID', 'Sutun1', 'TarihPtsi', 'GirisPtsi', 'CikisPtsi', 'TarihSli', 'GirisSli', 'CikisSali',
                  'TarihCrs', 'GirisCrs', 'CikisCrs', 'TarihPrs', 'GirisPrs', 'CikisPrs', 'TarihCuma', 'GirisCuma',
                  'CikisCuma']

    # Giriş saatlerinin yerlerini tarihlerle değiştiriyoruz
    df.at[2, 'GirisPrs'] = df.at[1, 'TarihPrs']
    df_persembe = df[['PersonelID', 'TarihPrs', 'GirisPrs', 'CikisPrs']]
    df_persembe.columns = ['PersonelID', 'Tarih', 'GirisSaati', 'CikisSaati']

    df = df.drop(index=[0, 1])

    persembe_verileri = []
    for index, row in df.iterrows():
        if pd.notna(row['GirisPrs']) and pd.notna(row['PersonelID']):
            personel_id = row['PersonelID']
            giris_saati = row['GirisPrs']
            cikis_saati = row['CikisPrs']
            tarih = df.loc[2, 'GirisPrs']  # Tarih 2. satırda belirtiliyor

            persembe_verileri.append({
                'PersonelID': personel_id,
                'Tarih': tarih,
                'GirisSaati': giris_saati,
                'CikisSaati': cikis_saati
            })

    df_persembe = pd.DataFrame(persembe_verileri)
    return df_persembe
# Cuma için veri temizleme fonksiyonu
def cuma_Mesai_plan(df):

    # print(f"Sütunlar: {df.columns}")  # Mevcut sütun adlarını konsola yazdırıyoruz

    df.columns = ['PersonelID', 'Sutun1', 'TarihPtsi', 'GirisPtsi', 'CikisPtsi', 'TarihSli', 'GirisSli', 'CikisSali',
                  'TarihCrs', 'GirisCrs', 'CikisCrs', 'TarihPrs', 'GirisPrs', 'CikisPrs', 'TarihCuma', 'GirisCuma',
                  'CikisCuma']

    # Giriş saatlerinin yerlerini tarihlerle değiştiriyoruz
    df.at[2, 'GirisCuma'] = df.at[1, 'TarihCuma']
    df_Cuma = df[['PersonelID', 'TarihCuma', 'GirisCuma', 'CikisCuma']]
    df_Cuma.columns = ['PersonelID', 'Tarih', 'GirisSaati', 'CikisSaati']

    df = df.drop(index=[0, 1])

    Cuma_verileri = []
    for index, row in df.iterrows():
        if pd.notna(row['GirisCuma']) and pd.notna(row['PersonelID']):
            personel_id = row['PersonelID']
            giris_saati = row['GirisCuma']
            cikis_saati = row['CikisCuma']
            tarih = df.loc[2, 'GirisCuma']  # Tarih 2. satırda belirtiliyor

            Cuma_verileri.append({
                'PersonelID': personel_id,
                'Tarih': tarih,
                'GirisSaati': giris_saati,
                'CikisSaati': cikis_saati
            })

    df_Cuma = pd.DataFrame(Cuma_verileri)
    return df_Cuma

# def Mesai_plan_kaydet(df):
#     for index, row in df.iterrows():
#         try:
#             personel = Personel.objects.get(id=int(row['PersonelID']))  # Personel ID'yi kullanarak personeli bul
#
#             # tarih = pd.to_datetime(row['Tarih']).date()
#             tarih = pd.to_datetime(row['Tarih'], format='%d.%m.%Y', dayfirst=True).date()
#             # Giriş saati için format kontrolü
#             try:
#                 giris_saati = pd.to_datetime(row['GirisSaati'], format='%H:%M').time()  # Sadece saat ve dakika
#             except ValueError:
#                 giris_saati = pd.to_datetime(row['GirisSaati'], format='%H:%M:%S').time()  # Saat, dakika ve saniye
#
#             # Çıkış saati için format kontrolü
#             if pd.notna(row['CikisSaati']):
#                 try:
#                     cikis_saati = pd.to_datetime(row['CikisSaati'], format='%H:%M').time()
#                 except ValueError:
#                     cikis_saati = pd.to_datetime(row['CikisSaati'], format='%H:%M:%S').time()
#             else:
#                 cikis_saati = None
#
#             # Veritabanına kaydetme
#             PersonelGunlukCalisma.objects.create(
#                 personel=personel,
#                 tarih=tarih,
#                 giris_saati=giris_saati,
#                 cikis_saati=cikis_saati
#             )
#         except Personel.DoesNotExist:
#             print(f"Personel ID {row['PersonelID']} bulunamadı.")
#             continue
#         except Exception as e:
#             print(f"Veritabanına kayıt sırasında hata oluştu: {str(e)}")
def Mesai_plan_kaydet(df):
    for index, row in df.iterrows():
        try:
            personel = Personel.objects.get(id=int(row['PersonelID']))  # Personel ID'yi kullanarak personeli bul
            tarih = pd.to_datetime(row['Tarih'], format='%d.%m.%Y', dayfirst=True).date()  # Tarihi al

            # Giriş ve çıkış saatlerini işle
            try:
                giris_saati = pd.to_datetime(row['GirisSaati'], format='%H:%M').time()
            except ValueError:
                giris_saati = pd.to_datetime(row['GirisSaati'], format='%H:%M:%S').time()

            if pd.notna(row['CikisSaati']):
                try:
                    cikis_saati = pd.to_datetime(row['CikisSaati'], format='%H:%M').time()
                except ValueError:
                    cikis_saati = pd.to_datetime(row['CikisSaati'], format='%H:%M:%S').time()
            else:
                cikis_saati = None

            # Personelin günlük çalışma kaydını oluştur
            PersonelGunlukCalisma.objects.create(
                personel=personel,
                tarih=tarih,
                giris_saati=giris_saati,
                cikis_saati=cikis_saati
            )

            # Çalışma süresini saat cinsinden hesapla
            giris_datetime = datetime.combine(tarih, giris_saati)
            cikis_datetime = datetime.combine(tarih, cikis_saati) if cikis_saati else giris_datetime + timedelta(hours=8)
            calisma_suresi_saat = Decimal((cikis_datetime - giris_datetime).total_seconds() / 3600)  # Float'ı Decimal'e dönüştürüyoruz

            # Personel saat ücretini Decimal'e dönüştürerek hesaplama yapıyoruz
            personel_maliyeti = calisma_suresi_saat * personel.saat_ucreti  # Burada her iki değer Decimal olmalı

            # Günlük gider tablosundaki ilgili tarihin personel_planlanan alanını güncelle
            gunluk_gider, created = GunlukGider.objects.get_or_create(tarih=tarih)
            gunluk_gider.personel_planlanan += personel_maliyeti
            gunluk_gider.save()

        except Personel.DoesNotExist:
            print(f"Personel ID {row['PersonelID']} bulunamadı.")
            continue
        except Exception as e:
            print(f"Veritabanına kayıt sırasında hata oluştu: {str(e)}")


def Personel_MesaiPlan_view(request):
    if request.method == 'POST':
        # print("POST isteği alındı")  # POST isteği kontrolü
        form = PersonelMesaiPlanForm(request.POST, request.FILES)
        if form.is_valid():
            # print("Form geçerli")  # Formun geçerli olup olmadığını kontrol edin
            csv_file = request.FILES['csv_file']
            try:
                decoded_file = csv_file.read().decode('utf-8')
                # print("CSV dosyası başarıyla okundu")  # CSV dosyasının okunduğunu kontrol edin
                io_string = io.StringIO(decoded_file)
                df = pd.read_csv(io_string, sep=';')

                # Pazartesi verilerini temizleyip kaydet
                df_pazartesi = pazartesi_Mesai_plan(df)
                # print("Pazartesi verileri temizlendi")  # Temizleme adımını kontrol edin
                Mesai_plan_kaydet(df_pazartesi)

                # Diğer günler için de benzer şekilde işleme ve kaydetme
                df_sali = sali_Mesai_plan(df)
                Mesai_plan_kaydet(df_sali)

                df_carsamba = carsamba_Mesai_plan(df)
                Mesai_plan_kaydet(df_carsamba)

                df_persembe = persembe_Mesai_plan(df)
                Mesai_plan_kaydet(df_persembe)

                df_cuma = cuma_Mesai_plan(df)
                Mesai_plan_kaydet(df_cuma)

                messages.success(request, "CSV dosyası başarıyla yüklendi ve veriler kaydedildi.")
                return redirect(reverse('home'))  # 'home' adında bir URL'ye yönlendiriliyor
            except Exception as e:
                print(f"Hata oluştu: {str(e)}")  # Hata kontrolü
                messages.error(request, f"Dosya işlenirken bir hata oluştu: {str(e)}")
                return redirect('personel_mesaiPlanYukle_url')
    else:
        form = PersonelMesaiPlanForm()

    return render(request, 'mesai/PersonelMesaiPlanYukle.html', {'form': form})