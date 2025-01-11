from django.db import models
from django.utils import timezone
from datetime import datetime, date, timedelta
from decimal import Decimal
import calendar
from datetime import date  # datetime modülünden 'date' fonksiyonunu içe aktarıyoruz
from decimal import Decimal
from django.utils.timezone import now
from django.db.models import DecimalField, F, Sum, Count
from django.db.models.functions import Coalesce
from django.db.models import Sum, F, DecimalField
from django.db.models.functions import Coalesce
from datetime import date

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    telefon = models.CharField(max_length=15, blank=True, null=True)
    adres = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username




class FormulCSVFile(models.Model): #13.09 09:30
    name = models.CharField(max_length=100)  # CSV dosyasının adı
    file = models.FileField(upload_to='csv_files/')  # CSV dosyasının yolu
    Yukleme_tarihi = models.DateTimeField(default=timezone.now)  # Varsayılan tarih bugünün tarihi, manuel değiştirilebilir
    Formul_tarihi = models.DateTimeField(default=timezone.now)  # Varsayılan tarih bugünün tarihi, manuel değiştirilebilir

    def __str__(self):
        return self.name
class SabitGider(models.Model):
    GIDER_TIPI_CHOICES = [
        ('kira', 'Kira'),
        ('kominal', 'Kominal'),
        ('reklam', 'Reklam'),
        ('transport', 'Transport'),
        ('bakim', 'Bakım/Onarım'),
        # Diğer sabit gider türleri eklenebilir
    ]
    gider_tipi = models.CharField(max_length=20, choices=GIDER_TIPI_CHOICES)
    tutar = models.DecimalField(max_digits=10, decimal_places=2)
    tarih = models.DateField(default=timezone.now)  # Giderin eklenme tarihi

    def __str__(self):
        return f"{self.gider_tipi} - {self.tutar} - {self.tarih}"
class GunlukGider(models.Model):
    tarih = models.DateField(default=timezone.now)
    hammadde_gideri = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    personel_planlanan = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    personel_ilave = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sabit_gider_payi = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def toplam_gider(self):
        return self.hammadde_gideri + self.personel_planlanan + self.personel_ilave + self.sabit_gider_payi
    def __str__(self):
        return f"{self.tarih} - Toplam Gider: {self.toplam_gider()}"

class GunlukGelir(models.Model):
    tarih = models.DateField(default=timezone.now)
    toplam_gelir = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.tarih} - {self.toplam_gelir} Eur"

class Personel(models.Model):
    ad = models.CharField(max_length=100)
    soyad = models.CharField(max_length=100)
    pozisyon = models.CharField(max_length=100)
    saat_ucreti = models.DecimalField(max_digits=10, decimal_places=2)
    baslangic_tarihi = models.DateField()
    departman = models.CharField(max_length=100)
    telefon = models.CharField(max_length=15, blank=True, null=True)
    eposta = models.EmailField(blank=True, null=True)
    dogum_tarihi = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.ad} {self.soyad}"


class PersonelGunlukCalisma(models.Model):
    personel = models.ForeignKey(Personel, on_delete=models.CASCADE)
    tarih = models.DateField(default=timezone.now)
    giris_saati = models.TimeField()
    cikis_saati = models.TimeField(null=True, blank=True)  # null ve blank olarak ayarlandı

    def calisma_saatleri(self):
        giris = datetime.combine(self.tarih, self.giris_saati)

        # Çıkış saati boşsa mevcut zamanı kullan
        if self.cikis_saati is not None:
            cikis = datetime.combine(self.tarih, self.cikis_saati)
        else:
            cikis = datetime.now()  # Çıkış saati yoksa, şu anki zamanı kullan

        calisma_suresi = cikis - giris
        return calisma_suresi.total_seconds() / 3600  # Çalışma süresi saat olarak döndürülüyor

    def gunluk_maliyet(self):
        calisma_saatleri = Decimal(self.calisma_saatleri())  # Decimal türüne dönüştürme
        return calisma_saatleri * self.personel.saat_ucreti

    def __str__(self):
        return f"{self.personel.ad} - {self.tarih}"

class Tedarikci_SRK(models.Model):
    tedarikciAdi = models.CharField(max_length=255)
    adres = models.TextField()
    telefonNumarasi = models.CharField(max_length=20)
    email = models.EmailField()
    vergiNumarasi = models.CharField(max_length=50)
    website = models.URLField(blank=True, null=True)
    iletisimKisi = models.CharField(max_length=255)
    urunlerHizmetler = models.TextField()
    bankaHesapBilgileri = models.TextField()
    anlasmaTarihi = models.DateField()
    durum = models.CharField(max_length=50, choices=[('active', 'Active'), ('inactive', 'Inactive')])
    ekNotlar = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.tedarikciAdi
    class Meta:
        verbose_name = "Tedarikci"
        verbose_name_plural = "Tedarikci"

class Hammadde(models.Model):
    hammadde_kategori = models.CharField(max_length=100, choices=[
        ('bakliyat', 'Bakliyat'), ('buzdolabı', 'Buzdolabı'), ('meyve_sebze', 'Meyve_Sebze'),
        ('ambalajli_urunler', 'Ambalajli_Urunler'), ('ambalaj_urtm', 'Ambalaj_Urtm'),
        ('baharat', 'Baharat'), ('donuk', 'Donuk'), ('katki_maddesi', 'Katki_Maddesi'),
        ('kuruyemis', 'Kuruyemis'), ('uretim', 'Uretim'), ('genel', 'Genel'), ('etiket', 'Etiket')
    ])
    hammadde_adi = models.CharField(max_length=100)
    birim = models.CharField(max_length=50, choices=[('kg', 'Kilogram'), ('Ad', 'Adet')])
    diger_notlar = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.hammadde_adi
    class Meta:
        ordering = ['hammadde_adi']
        verbose_name = "Hammadde"
        verbose_name_plural = "Hammadde"

class SatinAlma(models.Model):
    tedarikci = models.ForeignKey(Tedarikci_SRK, on_delete=models.CASCADE)
    giris_tarihi = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.tedarikci.tedarikciAdi} - {self.giris_tarihi}"

    def update_total_cost(self):
        toplam_maliyet = sum(item.toplam_maliyet for item in self.satinalmalist_set.all())
        # Önceki maliyet kaydını sil (eğer varsa)
        Muhasebe.objects.filter(islem_turu="Satın Alma", miktar__lt=0).delete()
        # Yeni maliyet kaydını ekle
        Muhasebe.objects.create(islem_turu="Satın Alma", miktar=-toplam_maliyet)

class SatinAlmaList(models.Model):
    satin_alma = models.ForeignKey(SatinAlma, on_delete=models.CASCADE, related_name='satinalmalist_set')
    hammadde = models.ForeignKey(Hammadde, on_delete=models.CASCADE)
    miktar = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    fiyat = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    toplam_maliyet = models.DecimalField(max_digits=10, decimal_places=2, blank=True)

    def save(self, *args, **kwargs):
        self.toplam_maliyet = self.miktar * self.fiyat
        super(SatinAlmaList, self).save(*args, **kwargs)
        self.update_depo()
        self.satin_alma.update_total_cost()
        self.guncelle_resept_maliyetleri()
        if self.fiyat and self.miktar and self.hammadde.hammadde_adi:
            SatinAlinanlar.objects.create(
                satin_alma_tarihi=self.satin_alma.giris_tarihi,
                hammadde_adi=self.hammadde.hammadde_adi,
                miktar=self.miktar,
                fiyat=self.fiyat,
                tedarikci=self.satin_alma.tedarikci.tedarikciAdi
            )

    def guncelle_resept_maliyetleri(self):
        # Hangi reçeteler bu hammaddeleri içeriyor, onları bul
        ilgili_reseptler = Resept_icerigi.objects.filter(hhmmadde=self.hammadde).values_list('resept', flat=True)

        # Her ilgili reçetenin maliyetini güncelle
        for resept_id in ilgili_reseptler:
            hesapla_resept_maliyeti(resept_id)

    def update_depo(self):
        try:
            depo_kaydi = Depo.objects.get(hammadde=self.hammadde)
            #depodaki urunun maliyeti ile satinalinan urunun maliyetinin agirlikli malyetini yeni maliyet olarak ekle
            depo_kaydi.hammadde_maliyet = ((depo_kaydi.hammadde_maliyet * depo_kaydi.miktar) + (
                        self.fiyat * self.miktar)) / (depo_kaydi.miktar + self.miktar)

            depo_kaydi.miktar += self.miktar

            depo_kaydi.save()
        except Depo.DoesNotExist:
            Depo.objects.create(hammadde=self.hammadde, miktar=self.miktar, hammadde_maliyet=self.fiyat)

class SatinAlinanlar(models.Model):
    satin_alma_tarihi = models.DateField()
    hammadde_adi = models.CharField(max_length=100)
    miktar = models.DecimalField(max_digits=10, decimal_places=2)
    fiyat = models.DecimalField(max_digits=10, decimal_places=2)
    tedarikci = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.satin_alma_tarihi} - {self.hammadde_adi} - {self.miktar} - {self.fiyat} - {self.tedarikci}"

class Depo(models.Model):
    hammadde = models.ForeignKey(Hammadde, on_delete=models.CASCADE)
    miktar = models.DecimalField(max_digits=10, decimal_places=2)
    kategori1 = models.DecimalField(max_digits=10, decimal_places=2, default=100)
    kategori2 = models.DecimalField(max_digits=10, decimal_places=2, default=80)
    kategori3 = models.DecimalField(max_digits=10, decimal_places=2, default=50)
    hammadde_maliyet = models.DecimalField(max_digits=10, decimal_places=2, default=20)  # kategori4 alanını ekleyin

    def get_stok_kategori(self):
        if self.miktar >= self.kategori1:
            return "İhtiyaç Fazlası"
        elif self.kategori2 <= self.miktar < self.kategori1:
            return "Normal Stok"
        elif self.kategori3 <= self.miktar < self.kategori2:
            return "Sipariş Gereği"
        else:
            return "Kriz Stok"

    def get_son_alis_fiyati(self):
        try:
            son_satin_alma = SatinAlmaList.objects.filter(hammadde=self.hammadde).latest('satin_alma__giris_tarihi')
            return son_satin_alma.fiyat
        except SatinAlmaList.DoesNotExist:
            return 0

    def __str__(self):
        return f"{self.hammadde.hammadde_adi} - {self.miktar}"

    class Meta:
        verbose_name = "Depo"
        verbose_name_plural = "Depolar"

class Muhasebe(models.Model):
    islem_turu = models.CharField(max_length=50)
    miktar = models.DecimalField(max_digits=10, decimal_places=2)
    tarih = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.tarih} - {self.islem_turu} - {self.miktar}"
    class Meta:
        verbose_name = "Finans"
        verbose_name_plural = "Muhasebe"

class Resept(models.Model):
    resept_adi = models.CharField(max_length=255)
    musteriUrn = models.CharField(max_length=50, choices=[('kesko', 'Kesko'), ('direk', 'Direk'), ('hok', 'HOK'), ('corint', 'Corint')])
    Urn_kategori = models.CharField(max_length=50, choices=[('salata', 'Salata'), ('yoğurt', 'Yoğurt'), ('wrap', 'Wrap'), ('bowl ', 'Bowl '), ('sandwich', 'Sandwich'), ('kilo', 'Kilo'), ('ateria', 'Ateria')])
    toplam_fiyat = models.DecimalField(max_digits=10, decimal_places=4)
    resept_gram = models.DecimalField(max_digits=10, decimal_places=4)

    def __str__(self):
        return self.resept_adi

    class Meta:
        verbose_name = "Resept"
        verbose_name_plural = "Resept"

class Resept_icerigi(models.Model):
    resept = models.ForeignKey(Resept, on_delete=models.CASCADE)
    hhmmadde = models.ForeignKey(Hammadde, on_delete=models.CASCADE)
    miktar = models.DecimalField(max_digits=10, decimal_places=4)
    gurup = models.DecimalField(max_digits=2, decimal_places=0)
    sira = models.DecimalField(max_digits=2, decimal_places=0)

    uretim_sasfhalari = [
        ('karisim', 'Karisim'),
        ('paketleme', 'Paketleme'),
        ('kaynatma', 'Kaynatma'),
        ('ambalaj', 'Ambalaj'),
        ('etiket', 'Etiket'),
        ('yogurt', 'Yogurt'),
    ]
    uretim_safhasi = models.CharField(max_length=50, choices= uretim_sasfhalari)

    def __str__(self):
        return f"{self.resept.resept_adi} - {self.hhmmadde.hammadde_adi} - {self.miktar} - {self.uretim_safhasi}"

    class Meta:
        verbose_name = "Resept_icerikleri"
        verbose_name_plural = "Resept_icerikleri"

# resept maliyetini depo hammaddemaliyet verisine gore hammaddetoplam maliyethesaplama
def hesapla_resept_maliyeti(resept_id):
    try:
        resept = Resept.objects.get(id=resept_id)  # Resepti al
        resept_icerikleri = Resept_icerigi.objects.filter(resept=resept)  # Reseptin içeriklerini al
        toplam_maliyet = 0  # Toplam maliyeti başlat

        # Her bir resept içeriği için döngü
        for icerik in resept_icerikleri:
            try:
                depo_kaydi = Depo.objects.get(hammadde=icerik.hhmmadde)  # Hammaddeye ait depo kaydını al
                hammadde_maliyeti = depo_kaydi.hammadde_maliyet  # Depodaki ham madde maliyetini al
                toplam_maliyet += hammadde_maliyeti * icerik.miktar  # Miktar ile maliyeti çarpıp toplam maliyete ekle
            except Depo.DoesNotExist:
                # Eğer depo kaydı yoksa, burada bir hata işleme yapabilirsiniz
                print(f"Hammadde {icerik.hhmmadde} için depo kaydı bulunamadı.")

        # Eğer resept maliyeti zaten varsa, onu güncelle, yoksa yeni bir kayıt oluştur
        resept_maliyet, created = Resept_maliyet.objects.get_or_create(resept=resept)
        resept_maliyet.hammaddeTopMaliyet = toplam_maliyet
        resept_maliyet.save()  # Hesaplanan maliyeti kaydet

        return toplam_maliyet  # İstenirse, toplam maliyeti geri döndür

    except Resept.DoesNotExist:
        print(f"Resept ID {resept_id} için resept bulunamadı.")
        return None

class Resept_maliyet(models.Model):
    resept = models.ForeignKey(Resept, on_delete=models.CASCADE)
    hammaddeTopMaliyet = models.DecimalField(max_digits=10, decimal_places=4, null=True)

    def __str__(self):
        return f"{self.resept.resept_adi} - {self.hammaddeTopMaliyet}"

class Musteri(models.Model):
    musteri_adi = models.CharField(max_length=255)
    telefon = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    adres = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.musteri_adi
    class Meta:
        verbose_name = "Musteri"
        verbose_name_plural = "Musteri"

class UretimIstatistik(models.Model):
    URUN_GRUPLARI = [
        ('Wrap', 'Wrap'),
        ('Blow', 'Blow'),
        ('Salad', 'Salad'),
        ('Jogurt', 'Jogurt'),
        ('Musli', 'Musli'),
        ('Sicak', 'Sicak'),
        ('Sandwich', 'Sandwich'),
        ('Kilo', 'Kilo'),
    ]

    tarih = models.DateField(default=timezone.now)
    urun_adi = models.CharField(max_length=50, choices=URUN_GRUPLARI)
    uretim_adedi = models.PositiveIntegerField()
    kac_kisi_calisti = models.PositiveIntegerField()
    baslama_saati = models.TimeField()
    bitis_saati = models.TimeField()
    toplam_calisma_saati = models.FloatField(editable=False)  # dakika olarak
    dakika_uretim = models.FloatField(editable=False)
    maas_saat = models.FloatField(default=17, blank=True, null=True)  # Varsayılan değer ve zorunlu değil
    maliyet_uretim = models.FloatField(editable=False)
    notlar = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        baslama_datetime = datetime.combine(date.min, self.baslama_saati)
        bitis_datetime = datetime.combine(date.min, self.bitis_saati)
        self.toplam_calisma_saati = (bitis_datetime - baslama_datetime).total_seconds() / 60  # dakika olarak hesaplama
        self.dakika_uretim = (self.toplam_calisma_saati * self.kac_kisi_calisti) / self.uretim_adedi
        if not self.maas_saat:
            self.maas_saat = 17  # Varsayılan değer
        self.maliyet_uretim = (self.maas_saat / 60) * self.dakika_uretim
        super().save(*args, **kwargs)

    def get_toplam_calisma_saati_formatted(self):
        hours, remainder = divmod(self.toplam_calisma_saati, 60)
        minutes = remainder
        return f"{int(hours)} saat {int(minutes)} dakika"

    def get_dakika_uretim_formatted(self):
        total_seconds = self.dakika_uretim * 60
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        return f"{minutes} dak {seconds} sn"

    def get_maas_saat_euro(self):
        return f"€{self.maas_saat:.2f}"

    def get_maliyet_uretim_euro(self):
        return f"€{self.maliyet_uretim:.4f}"

    def __str__(self):
        return f"{self.tarih} - {self.urun_adi}"

    class Meta:
        verbose_name = "Uretim statistik"
        verbose_name_plural = "Uretim statistik"
        permissions = [
            ("view_raporlar", "Can view raporlar"),
        ]

class Uretim(models.Model):
    musteri = models.ForeignKey(Musteri, on_delete=models.CASCADE, default=1)
    uretim_tarihi = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Satis: {self.musteri.musteri_adi} - {self.uretim_tarihi}"

    class Meta:
        verbose_name = "Uretimler"
        verbose_name_plural = "Uretimler"

# class UretimDetay(models.Model):
#     Udetay = models.ForeignKey('Uretim', on_delete=models.CASCADE)
#     Uresept = models.ForeignKey('Resept', on_delete=models.CASCADE)
#     miktar = models.PositiveIntegerField()
#
#     tarih = models.DateField(editable=False, blank=True, null=True)
#     musteri = models.CharField(max_length=255, editable=False, blank=True, null=True)
#     resept_fiyati = models.DecimalField(max_digits=10, decimal_places=2, editable=False, blank=True, null=True)
#
#
#     def save(self, *args, **kwargs):
#
#         self.tarih = self.Udetay.uretim_tarihi
#         self.musteri = self.Udetay.musteri.id
#         self.resept_fiyati = self.Uresept.toplam_fiyat
#
#         super(UretimDetay, self).save(*args, **kwargs)
#         self.guncelle_depo_and_muhasebe()
#         self.guncelle_gider()
#
#     def guncelle_depo_and_muhasebe(self):
#         toplam_fiyat = Decimal(0)
#         uretilenlr = Resept_icerigi.objects.filter(resept=self.Uresept)
#         for item in uretilenlr:
#             try:
#                 depo_kaydi = Depo.objects.get(hammadde=item.hhmmadde)
#                 depo_kaydi.miktar -= item.miktar * self.miktar
#                 depo_kaydi.save()
#             except Depo.DoesNotExist:
#                 pass
#         toplam_fiyat += Decimal(self.Uresept.toplam_fiyat) * Decimal(self.miktar)
#         Muhasebe.objects.create(islem_turu="Urun Satışı", miktar=toplam_fiyat)
#
#         # Günlük gelir kaydını oluştur veya güncelle
#         gunluk_gelir, created = GunlukGelir.objects.get_or_create(tarih=self.Udetay.uretim_tarihi)
#         gunluk_gelir.toplam_gelir = Decimal(gunluk_gelir.toplam_gelir) + toplam_fiyat
#         gunluk_gelir.save()
#
#     def guncelle_gider(self):
#         try:
#             # Resept maliyetini al
#             resept_maliyet = Resept_maliyet.objects.get(resept=self.Uresept)
#             toplam_maliyet = Decimal(resept_maliyet.hammaddeTopMaliyet) * Decimal(self.miktar)
#
#             # Günlük gider kaydını oluştur veya güncelle ve hammadde giderini yaz
#             gunluk_gider, created = GunlukGider.objects.get_or_create(tarih=self.Udetay.uretim_tarihi)
#             gunluk_gider.hammadde_gideri = Decimal(gunluk_gider.hammadde_gideri) + toplam_maliyet
#
#             # Eğer sabit gider payı yoksa hesapla
#             if not gunluk_gider.sabit_gider_payi:
#                 self.guncelle_sabit_gider(gunluk_gider)
#
#             gunluk_gider.save()
#
#         except Resept_maliyet.DoesNotExist:
#             # Eğer reseptin maliyeti bulunamazsa, herhangi bir işlem yapmadan devam edebiliriz
#             pass
#
#     def guncelle_sabit_gider(self, gunluk_gider):
#         # Bugünün ayını ve yılını al
#         bugun = timezone.now().date()
#         ay = bugun.month
#         yil = bugun.year
#
#         # Sabit giderleri bu ay için al
#         sabit_giderler = SabitGider.objects.filter(tarih__month=ay, tarih__year=yil)
#
#         # Sabit giderlerin toplamını hesapla
#         toplam_sabit_gider = Decimal(0)
#         for gider in sabit_giderler:
#             toplam_sabit_gider += gider.tutar
#
#         # Bu ayın iş günlerini hesapla
#         is_gunleri = self.ay_is_gunleri(ay, yil)
#
#         # Eğer iş günü varsa, sabit gider payını iş günlerine böl
#         if is_gunleri > 0:
#             sabit_gider_payi = toplam_sabit_gider / is_gunleri
#             gunluk_gider.sabit_gider_payi = sabit_gider_payi
#
#     def ay_is_gunleri(self, ay, yil):
#         """
#         Bu fonksiyon, verilen ayın iş günlerini (Pazartesi-Cuma) hesaplar.
#         """
#         ayin_gun_sayisi = calendar.monthrange(yil, ay)[1]  # Ayın toplam gün sayısını al
#         is_gunleri = 0
#
#         for gun in range(1, ayin_gun_sayisi + 1):
#             gun_tarihi = datetime.date(yil, ay, gun)
#             if gun_tarihi.weekday() < 5:  # Pazartesi (0) ile Cuma (4) arasında ise
#                 is_gunleri += 1
#
#         return is_gunleri


class UretimDetay(models.Model):
    Udetay = models.ForeignKey('Uretim', on_delete=models.CASCADE)
    Uresept = models.ForeignKey('Resept', on_delete=models.CASCADE)
    miktar = models.PositiveIntegerField()

    tarih = models.DateField(editable=False, blank=True, null=True)
    musteri = models.CharField(max_length=255, editable=False, blank=True, null=True)
    resept_fiyati = models.DecimalField(max_digits=10, decimal_places=2, editable=False, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.tarih = self.Udetay.uretim_tarihi
        self.musteri = self.Udetay.musteri.id
        self.resept_fiyati = self.Uresept.toplam_fiyat

        super(UretimDetay, self).save(*args, **kwargs)
        self.guncelle_depo_and_muhasebe()
        self.guncelle_gider()

    def guncelle_depo_and_muhasebe(self):
        toplam_fiyat = Decimal(0)
        uretilenler = Resept_icerigi.objects.filter(resept=self.Uresept)
        for item in uretilenler:
            try:
                depo_kaydi = Depo.objects.get(hammadde=item.hhmmadde)
                depo_kaydi.miktar -= item.miktar * self.miktar
                depo_kaydi.save()
            except Depo.DoesNotExist:
                pass
        toplam_fiyat += Decimal(self.Uresept.toplam_fiyat) * Decimal(self.miktar)
        Muhasebe.objects.create(islem_turu="Ürün Satışı", miktar=toplam_fiyat)

        # Günlük gelir kaydını oluştur veya güncelle
        gunluk_gelir, created = GunlukGelir.objects.get_or_create(tarih=self.Udetay.uretim_tarihi)
        gunluk_gelir.toplam_gelir = Decimal(gunluk_gelir.toplam_gelir) + toplam_fiyat
        gunluk_gelir.save()

    def guncelle_gider(self):
        try:
            # Resept maliyetini al
            resept_maliyet = Resept_maliyet.objects.get(resept=self.Uresept)
            toplam_maliyet = Decimal(resept_maliyet.hammaddeTopMaliyet) * Decimal(self.miktar)

            # Günlük gider kaydını oluştur veya güncelle ve hammadde giderini yaz
            gunluk_gider, created = GunlukGider.objects.get_or_create(tarih=self.Udetay.uretim_tarihi)
            gunluk_gider.hammadde_gideri = Decimal(gunluk_gider.hammadde_gideri) + toplam_maliyet

            # Eğer sabit gider payı yoksa hesapla
            if not gunluk_gider.sabit_gider_payi:
                self.guncelle_sabit_gider(gunluk_gider)

            gunluk_gider.save()

        except Resept_maliyet.DoesNotExist:
            # Eğer reseptin maliyeti bulunamazsa, herhangi bir işlem yapmadan devam edebiliriz
            pass

    def guncelle_sabit_gider(self, gunluk_gider):
        # Bugünün ayını ve yılını al
        bugun = timezone.now().date()
        ay = bugun.month
        yil = bugun.year

        # Sabit giderleri bu ay için al
        sabit_giderler = SabitGider.objects.filter(tarih__month=ay, tarih__year=yil)

        # Sabit giderlerin toplamını hesapla
        toplam_sabit_gider = sum([gider.tutar for gider in sabit_giderler])

        # Bu ayın iş günlerini hesapla
        is_gunleri = self.ay_is_gunleri(ay, yil)

        # Eğer iş günü varsa, sabit gider payını iş günlerine böl
        if is_gunleri > 0:
            sabit_gider_payi = toplam_sabit_gider / is_gunleri
            gunluk_gider.sabit_gider_payi = sabit_gider_payi

    def ay_is_gunleri(self, ay, yil):
        """
        Bu fonksiyon, verilen ayın iş günlerini (Pazartesi-Cuma) hesaplar.
        """
        ayin_gun_sayisi = calendar.monthrange(yil, ay)[1]  # Ayın toplam gün sayısını al
        is_gunleri = 0

        for gun in range(1, ayin_gun_sayisi + 1):
            gun_tarihi = date(yil, ay, gun)  # datetime.date yerine date kullandık
            if gun_tarihi.weekday() < 5:  # Pazartesi (0) ile Cuma (4) arasında ise
                is_gunleri += 1

        return is_gunleri




# def bugunku_uretim_resept_hammaddeleri(): # 28.12.24
#     """
#     Bugünkü üretimlere göre, tarih -> reçete grupları -> reçete formülleri
#     şeklinde organize edilmiş bir veri yapısı döndür.
#     """
#     bugun = now().date()
#
#     uretim_hammaddeleri = Resept_icerigi.objects.filter(
#         resept__uretimdetay__Udetay__uretim_tarihi=bugun
#     ).values(
#         'resept__resept_adi',
#         'hhmmadde__hammadde_adi',
#         'resept__id',
#         'resept__uretimdetay__Udetay__uretim_tarihi',
#     ).annotate(
#         toplam_miktar=Sum(F('miktar') * F('resept__uretimdetay__miktar')),
#         toplam_kilo=Sum(F('resept__uretimdetay__miktar')),
#         uretim_sayisi=Sum('resept__uretimdetay__miktar'),
#     ).order_by('resept__uretimdetay__Udetay__uretim_tarihi', 'resept__resept_adi')
#
#     # Tarih bazında organize etmek için sözlük oluştur
#     tarih_gruplari = {}
#     for uretim in uretim_hammaddeleri:
#         tarih = uretim['resept__uretimdetay__Udetay__uretim_tarihi']
#         resept_adi = uretim['resept__resept_adi']
#         hammadde_adi = uretim['hhmmadde__hammadde_adi']
#         toplam_miktar = uretim['toplam_miktar']
#         toplam_kilo = uretim['toplam_kilo']
#         uretim_sayisi = uretim['uretim_sayisi']
#
#         if tarih not in tarih_gruplari:
#             tarih_gruplari[tarih] = {}
#
#         if resept_adi not in tarih_gruplari[tarih]:
#             tarih_gruplari[tarih][resept_adi] = {
#                 'toplam_kilo': toplam_kilo,
#                 'uretim_sayisi': uretim_sayisi,
#                 'hammaddeler': []
#             }
#
#         tarih_gruplari[tarih][resept_adi]['hammaddeler'].append({
#             'hammadde': hammadde_adi,
#             'toplam_miktar': toplam_miktar
#         })
#
#     return tarih_gruplari
def bugunku_uretim_resept_hammaddeleri():
    """
    Bugünkü üretimlere göre, tarih -> grup -> sıra -> reçete hammaddeleri
    şeklinde organize edilmiş bir veri yapısı döndür.
    """
    bugun = now().date()

    # Reçete içeriklerini sorgulama
    uretim_hammaddeleri = Resept_icerigi.objects.filter(
        resept__uretimdetay__Udetay__uretim_tarihi=bugun
    ).values(
        'resept__resept_adi',
        'hhmmadde__hammadde_adi',
        'resept__id',
        'resept__uretimdetay__Udetay__uretim_tarihi',
        'gurup',
        'sira'
    ).annotate(
        toplam_miktar=Sum(F('miktar') * F('resept__uretimdetay__miktar')),
        toplam_kilo=Sum(F('resept__uretimdetay__miktar')),
        uretim_sayisi=Sum('resept__uretimdetay__miktar'),
    ).order_by(
        'resept__uretimdetay__Udetay__uretim_tarihi',
        'gurup',
        'sira'
    )

    # Tarih, grup ve sıra bazında organize etmek için sözlük oluştur
    tarih_gruplari = {}
    for uretim in uretim_hammaddeleri:
        tarih = uretim['resept__uretimdetay__Udetay__uretim_tarihi']
        gurup = uretim['gurup']
        sira = uretim['sira']
        resept_adi = uretim['resept__resept_adi']
        hammadde_adi = uretim['hhmmadde__hammadde_adi']
        toplam_miktar = uretim['toplam_miktar']
        toplam_kilo = uretim['toplam_kilo']
        uretim_sayisi = uretim['uretim_sayisi']

        if tarih not in tarih_gruplari:
            tarih_gruplari[tarih] = {}

        if gurup not in tarih_gruplari[tarih]:
            tarih_gruplari[tarih][gurup] = {}

        if sira not in tarih_gruplari[tarih][gurup]:
            tarih_gruplari[tarih][gurup][sira] = {
                'resept_adi': resept_adi,
                'toplam_kilo': toplam_kilo,
                'uretim_sayisi': uretim_sayisi,
                'hammaddeler': []
            }

        tarih_gruplari[tarih][gurup][sira]['hammaddeler'].append({
            'hammadde': hammadde_adi,
            'toplam_miktar': toplam_miktar
        })

    return tarih_gruplari


# def uretim_urun_grubu_detaylari(tarih=None, urun_grubu=None):# 28.12.24
#     """
#     Belirli bir tarihe ve ürün grubuna göre, üretim detaylarını döndür.
#     - tarih: Üretim tarihi (datetime.date formatında)
#     - urun_grubu: Ürün grubu adı
#     """
#     if not tarih:
#         tarih = now().date()  # Eğer tarih belirtilmezse bugünün tarihi kullanılır
#
#     # Verileri filtrele
#     uretim_hammaddeleri = Resept_icerigi.objects.filter(
#         resept__uretimdetay__Udetay__uretim_tarihi=tarih,
#         resept__Urn_kategori=urun_grubu  # Ürün grubuna göre filtre
#     ).values(
#         'resept__resept_adi',
#         'hhmmadde__hammadde_adi',
#         'resept__id',
#     ).annotate(
#         toplam_miktar=Sum(F('miktar') * F('resept__uretimdetay__miktar')),
#         toplam_kilo=Sum(F('resept__uretimdetay__miktar')),
#         uretim_sayisi=Sum('resept__uretimdetay__miktar'),
#     ).order_by('resept__resept_adi', 'hhmmadde__hammadde_adi')
#
#     # Veriyi organize etmek için bir yapı oluştur
#     urun_grubu_detaylari = {
#         'tarih': tarih,
#         'urun_grubu': urun_grubu,
#         'recepteler': {}
#     }
#
#     for uretim in uretim_hammaddeleri:
#         resept_adi = uretim['resept__resept_adi']
#         hammadde_adi = uretim['hhmmadde__hammadde_adi']
#         toplam_miktar = uretim['toplam_miktar']
#         toplam_kilo = uretim['toplam_kilo']
#         uretim_sayisi = uretim['uretim_sayisi']
#
#         if resept_adi not in urun_grubu_detaylari['recepteler']:
#             urun_grubu_detaylari['recepteler'][resept_adi] = {
#                 'toplam_kilo': toplam_kilo,
#                 'uretim_sayisi': uretim_sayisi,
#                 'hammaddeler': []
#             }
#
#         urun_grubu_detaylari['recepteler'][resept_adi]['hammaddeler'].append({
#             'hammadde': hammadde_adi,
#             'toplam_miktar': toplam_miktar
#         })
#
#     return urun_grubu_detaylari#28.12 24


def uretim_urun_grubu_detaylari(tarih=None, urun_grubu=None):
    """
    Belirli bir tarihe ve ürün grubuna göre, üretim detaylarını döndür.
    Reçetelerin içindeki hammaddeler grup ve sıra numaralarına göre sıralanır.
    """
    if not tarih:
        tarih = now().date()  # Eğer tarih belirtilmezse bugünün tarihi kullanılır

    # Verileri filtrele
    uretim_hammaddeleri = Resept_icerigi.objects.filter(
        resept__uretimdetay__Udetay__uretim_tarihi=tarih,
        resept__Urn_kategori=urun_grubu
    ).values(
        'resept__resept_adi',
        'hhmmadde__hammadde_adi',
        'resept__id',
        'gurup',  # Grup numarası
        'sira',   # Sıra numarası
    ).annotate(
        toplam_miktar=Sum(
            F('miktar') * F('resept__uretimdetay__miktar'),
            output_field=DecimalField()
        ),
        uretim_sayisi=Sum(
            F('resept__uretimdetay__miktar'),
            output_field=DecimalField()
        ),
    ).order_by(
        'resept__resept_adi',  # Reçete adına göre sırala
        'gurup',               # Grup numarasına göre sırala
        'sira'                 # Sıra numarasına göre sırala
    )

    # Veriyi organize etmek için bir yapı oluştur
    urun_grubu_detaylari = {
        'tarih': tarih,
        'urun_grubu': urun_grubu,
        'recepteler': {}
    }

    for uretim in uretim_hammaddeleri:
        resept_adi = uretim['resept__resept_adi']
        hammadde_adi = uretim['hhmmadde__hammadde_adi']
        gurup = uretim['gurup']
        sira = uretim['sira']

        # Grup 20 için özel kontrol
        if gurup == 20:
            toplam_miktar = int(uretim['toplam_miktar'])  # Gerektiğinde 1000'e bölme
            birim = "Adet"
        else:
            toplam_miktar = uretim['toplam_miktar'] / 1000  # Her zaman 1000'e böl
            birim = "kg"

        uretim_sayisi = uretim['uretim_sayisi']

        # Reçete kontrolü
        if resept_adi not in urun_grubu_detaylari['recepteler']:
            urun_grubu_detaylari['recepteler'][resept_adi] = {
                'toplam_kilo': 0,  # Başlangıç değeri 0
                'uretim_sayisi': uretim_sayisi,
                'hammaddeler': []
            }

        # Hammaddeleri ekle
        urun_grubu_detaylari['recepteler'][resept_adi]['hammaddeler'].append({
            'hammadde': hammadde_adi,
            'toplam_miktar': toplam_miktar,
            'birim': birim,
            'gurup': gurup,
            'sira': sira
        })

        # Grup 20 haricindeki hammaddelerin toplam miktarlarını topla
        if gurup != 20:
            urun_grubu_detaylari['recepteler'][resept_adi]['toplam_kilo'] += toplam_miktar

    # Hammaddeleri grup ve sıra numarasına göre sırala
    for resept in urun_grubu_detaylari['recepteler'].values():
        resept['hammaddeler'] = sorted(
            resept['hammaddeler'],
            key=lambda x: (x['gurup'], x['sira'])
        )

    return urun_grubu_detaylari





class Siparis(models.Model):
    kullanici = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="siparisler")
    tarih = models.DateTimeField(auto_now_add=True)
    durum = models.CharField(
        max_length=20,
        choices=[
            ('beklemede', 'Beklemede'),
            ('onaylandi', 'Onaylandı'),
            ('reddedildi', 'Reddedildi'),
        ],
        default='beklemede'
    )

    def __str__(self):
        return f"{self.kullanici.username} - {self.tarih}"


class Urun(models.Model):
    isim = models.CharField(max_length=255)
    varsayilan_fiyat = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.isim


class KullaniciUrunFiyati(models.Model):
    kullanici = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="urun_fiyatlari")
    urun = models.ForeignKey(Urun, on_delete=models.CASCADE, related_name="kullanici_fiyatlari")
    fiyat = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.kullanici.username} - {self.urun.isim} - {self.fiyat} EUR"





