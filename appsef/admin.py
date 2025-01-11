# uretilenlerin musteri urungurubu sayi ve toplam fiyati ve tarihi kayit altina alinacak


from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.conf import settings
from django.conf.urls.static import static
from django.db.models import Sum
from django import forms
from django.utils.dateformat import time_format
from .forms import DepoForm
from datetime import time
from django.contrib.auth.admin import UserAdmin



from .models import (
    Tedarikci_SRK,
    Hammadde,
    SatinAlma,
    SatinAlmaList,
    Depo,
    Muhasebe,
    SatinAlinanlar,
    Resept,
    Resept_icerigi,
    Resept_maliyet,
    Musteri,
    Uretim,
    UretimDetay,
    UretimIstatistik,
    SabitGider,
    GunlukGider,
    Personel,
    PersonelGunlukCalisma,
    GunlukGelir,
    FormulCSVFile, CustomUser, Urun, Siparis, KullaniciUrunFiyati,
)

@admin.register(FormulCSVFile)
class FormulCSVFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'file', 'Yukleme_tarihi','Formul_tarihi')

@admin.register(Hammadde)
class HammaddeAdmin(admin.ModelAdmin):
    list_display = ('hammadde_adi', 'hammadde_kategori', 'birim')

class SatinAlmaListInline(admin.TabularInline):
    model = SatinAlmaList
    extra = 1
@admin.register(SatinAlma)
class SatinAlmaAdmin(admin.ModelAdmin):
    inlines = [SatinAlmaListInline]
    list_display = ('giris_tarihi', 'tedarikci', 'toplam_maliyet')

    def toplam_maliyet(self, obj):
        toplam_maliyet = sum(item.toplam_maliyet for item in obj.satinalmalist_set.all())
        return toplam_maliyet
    toplam_maliyet.short_description = 'Toplam Maliyet'

class SatinAlmaListAdmin(admin.ModelAdmin):
    list_display = ('satin_alma', 'hammadde', 'miktar', 'fiyat', 'toplam_maliyet')

class SatinAlinanlarAdmin(admin.ModelAdmin):
    list_display = ('satin_alma_tarihi', 'hammadde_adi', 'miktar', 'fiyat', 'tedarikci')

@admin.register(Depo)
class DepoAdmin(admin.ModelAdmin):
    form = DepoForm
    list_display = ('hammadde', 'miktar', 'get_stok_kategori', 'kategori1', 'kategori2', 'kategori3', 'hammadde_maliyet')  # kategori4 alanını ekleyin

    def get_stok_kategori(self, obj):
        return obj.get_stok_kategori()
    get_stok_kategori.short_description = 'Stok Kategorisi'

class Resept_icerigiInlineForm(forms.ModelForm):
    class Meta:
        model = Resept_icerigi
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['hhmmadde'].queryset = Hammadde.objects.all().order_by('hammadde_adi')

class Resept_icerigiInline(admin.TabularInline):
    model = Resept_icerigi
    form = Resept_icerigiInlineForm
    extra = 1

@admin.register(Resept)
class ReseptAdmin(admin.ModelAdmin):
    list_display = ('resept_adi','Urn_kategori','musteriUrn', 'toplam_fiyat')
    inlines = [Resept_icerigiInline]

@admin.register(Resept_maliyet)
class Resept_maliyetAdmin(admin.ModelAdmin):
    list_display = ('resept','hammaddeTopMaliyet')

class UretimDetayInline(admin.TabularInline):
    model = UretimDetay
    extra = 1

@admin.register(Uretim)
class UretimAdmin(admin.ModelAdmin):
    inlines = [UretimDetayInline]


@admin.register(Muhasebe)
class MuhasebeAdmin(admin.ModelAdmin):
    list_display = ('tarih', 'islem_turu', 'miktar')
    change_list_template = "admin/muhasebe_change_list.html"

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )

        if response is not None and hasattr(response, 'context_data'):
            try:
                qs = response.context_data['cl'].queryset
                toplam_gelir = qs.filter(miktar__gt=0).aggregate(Sum('miktar'))['miktar__sum'] or 0
                toplam_gider = qs.filter(miktar__lt=0).aggregate(Sum('miktar'))['miktar__sum'] or 0
                kasa_kalan = toplam_gelir + toplam_gider

                response.context_data['toplam_gelir'] = toplam_gelir
                response.context_data['toplam_gider'] = abs(toplam_gider)
                response.context_data['kasa_kalan'] = kasa_kalan
            except (AttributeError, KeyError):
                pass

        return response

@admin.register(UretimIstatistik)
class UretimIstatistikAdmin(admin.ModelAdmin):
    list_display = ('tarih', 'urun_adi', 'uretim_adedi', 'kac_kisi_calisti', 'get_baslama_saati_24', 'get_bitis_saati_24', 'get_toplam_calisma_saati_formatted', 'get_dakika_uretim_formatted', 'get_maas_saat_euro', 'get_maliyet_uretim_euro', 'notlar')

    def get_baslama_saati_24(self, obj):
        return time_format(obj.baslama_saati, 'H:i')
    get_baslama_saati_24.short_description = 'Başlama Saati (24 Saat)'

    def get_bitis_saati_24(self, obj):
        return time_format(obj.bitis_saati, 'H:i')
    get_bitis_saati_24.short_description = 'Bitiş Saati (24 Saat)'

    def get_toplam_calisma_saati_formatted(self, obj):
        return obj.get_toplam_calisma_saati_formatted()
    get_toplam_calisma_saati_formatted.short_description = 'Toplam Çalışma Saati'

    def get_dakika_uretim_formatted(self, obj):
        return obj.get_dakika_uretim_formatted()
    get_dakika_uretim_formatted.short_description = 'Dakika/Üretim'

    def get_maas_saat_euro(self, obj):
        return obj.get_maas_saat_euro()
    get_maas_saat_euro.short_description = 'Maaş/Saat (Euro)'

    def get_maliyet_uretim_euro(self, obj):
        return obj.get_maliyet_uretim_euro()
    get_maliyet_uretim_euro.short_description = 'Maliyet/Üretim (Euro)'

@admin.register(SabitGider)
class SabitGiderAdmin(admin.ModelAdmin):
    list_display = ('gider_tipi', 'tutar', 'tarih')

@admin.register(GunlukGider)
class GunlukGiderAdmin(admin.ModelAdmin):
    list_display = ('tarih', 'hammadde_gideri', 'personel_planlanan', 'personel_ilave',  'sabit_gider_payi', 'toplam_gider')

@admin.register(Personel)
class PersonelAdmin(admin.ModelAdmin):
    list_display = ('ad', 'soyad', 'pozisyon', 'saat_ucreti', 'baslangic_tarihi', 'departman', 'telefon', 'eposta', 'dogum_tarihi')
    search_fields = ('ad', 'soyad', 'pozisyon', 'departman')

@admin.register(PersonelGunlukCalisma)
class PersonelGunlukCalismaAdmin(admin.ModelAdmin):
    list_display = ('personel', 'tarih', 'giris_saati', 'cikis_saati', 'calisma_saatleri', 'gunluk_maliyet')
    list_filter = ('personel', 'tarih')
    search_fields = ('personel__ad', 'personel__soyad')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # Günlük gider hesaplaması
        today = obj.tarih
        # daily_fixed_cost_share = günlük_sabit_maliyet_pay_hesapla(today.month, today.year)

        # Günlük personel giderini hesapla
        personel_calismalari = PersonelGunlukCalisma.objects.filter(tarih=today)
        personel_gideri = sum([calisma.gunluk_maliyet() for calisma in personel_calismalari])

        gunluk_gider, created = GunlukGider.objects.get_or_create(tarih=today)
        gunluk_gider.personel_gideri = personel_gideri
        # gunluk_gider.sabit_gider_payi = daily_fixed_cost_share
        gunluk_gider.save()

@admin.register(GunlukGelir)
class GunlukGelirAdmin(admin.ModelAdmin):
    list_display = ('tarih', 'toplam_gelir')
    search_fields = ('tarih',)
    list_filter = ('tarih',)
    fields = ('tarih', 'toplam_gelir')

    def get_readonly_fields(self, request, obj=None):
        if obj:  # mevcut objeler için
            return ['tarih']
        else:
            return []


admin.site.register(CustomUser, UserAdmin)
admin.site.register(Urun)
admin.site.register(Siparis)
admin.site.register(KullaniciUrunFiyati)