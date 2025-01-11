from django import forms
from .models import UretimIstatistik,Depo
from .models import Personel, PersonelGunlukCalisma,Urun
from datetime import time
from django.utils import timezone
from django import forms
from django.forms import formset_factory



class FormulUplCSVForm(forms.Form):
    # tur = forms.CharField(label='Türü')  # Seçim alanı
    formul_tarihi = forms.DateTimeField(
        label='Formül Tarihi',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),  # Tarih ve saat seçici widget
        initial=timezone.now,  # Varsayılan tarih ve saat bugünün tarihi
        required=False  # İsteğe bağlı tarih
    )
# class FormulUplCSVForm(forms.Form):
#     # NAME_CHOICES = [
#     #     ('Sicak', 'Sıcak'),
#     #     ('Kesko', 'Kesko'),
#     #     ('Hok', 'Hok'),
#     #     ('Bowl', 'Bowl'),
#     #     ('Wrap', 'Wrap'),
#     #     ('Sandvic', 'Sandviç'),
#     #     ('Donuk', 'Donuk'),
#     # ]
#     #
#     # selected_name = forms.ChoiceField(choices=NAME_CHOICES, label='Formul Türü')  # Seçim alanı
#     formul_tarihi = forms.DateField(
#         label='Formül Tarihi',
#         widget=forms.SelectDateWidget,  # Tarih seçici widget
#         initial=timezone.now,  # Varsayılan tarih bugünün tarihi
#         required=False  # İsteğe bağlı tarih
#     )

    file = forms.FileField(label='CSV Dosyası')  # Dosya yükleme alanı


# class UretimIstatistikForm(forms.ModelForm):
#     class Meta:
#         model = UretimIstatistik
#         fields = ['tarih', 'urun_adi', 'uretim_adedi', 'kac_kisi_calisti', 'baslama_saati', 'bitis_saati', 'notlar']
#         widgets = {
#             'baslama_saati': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}, format='%H:%M'),
#             'bitis_saati': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}, format='%H:%M'),
#             'tarih': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
#             'urun_adi': forms.Select(attrs={'class': 'form-control'}),
#             'uretim_adedi': forms.NumberInput(attrs={'class': 'form-control'}),
#             'kac_kisi_calisti': forms.NumberInput(attrs={'class': 'form-control'}),
#             'notlar': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
#         }
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['baslama_saati'].initial = time(8, 0)  # Varsayılan başlangıç saati 08:00
#         self.fields['bitis_saati'].initial = time(17, 0)  # Varsayılan bitiş saati 17:00






class UretimIstatistikForm(forms.ModelForm):
    class Meta:
        model = UretimIstatistik
        fields = ['urun_adi', 'uretim_adedi', 'kac_kisi_calisti', 'baslama_saati', 'bitis_saati', 'notlar']
        widgets = {
            'baslama_saati': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}, format='%H:%M'),
            'bitis_saati': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}, format='%H:%M'),
            'urun_adi': forms.Select(attrs={'class': 'form-control'}),
            'uretim_adedi': forms.NumberInput(attrs={'class': 'form-control'}),
            'kac_kisi_calisti': forms.NumberInput(attrs={'class': 'form-control'}),
            'notlar': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['baslama_saati'].initial = time(8, 0)  # Varsayılan başlangıç saati
        self.fields['bitis_saati'].initial = time(17, 0)  # Varsayılan bitiş saati

# Her bölüm için dört üretim girişi olacak şekilde formset tanımlıyoruz.
UretimFormSet = formset_factory(UretimIstatistikForm, extra=4)

class GunlukUretimForm(forms.Form):
    tarih = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Tarih",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Üç bölüm için ayrı ayrı formset ekliyoruz.
        self.bolum1_formset = UretimFormSet(prefix='bolum1')
        self.bolum2_formset = UretimFormSet(prefix='bolum2')
        self.bolum3_formset = UretimFormSet(prefix='bolum3')

    def is_valid(self):
        # Ana formu ve formsetleri doğruluyoruz.
        form_valid = super().is_valid()
        bolum1_valid = self.bolum1_formset.is_valid()
        bolum2_valid = self.bolum2_formset.is_valid()
        bolum3_valid = self.bolum3_formset.is_valid()
        return form_valid and bolum1_valid and bolum2_valid and bolum3_valid

    def save(self):
        # Ana formdaki tarihi alıyoruz.
        tarih = self.cleaned_data['tarih']

        # Her formset içerisindeki formları kaydediyoruz.
        for bolum_formset in [self.bolum1_formset, self.bolum2_formset, self.bolum3_formset]:
            for form in bolum_formset:
                if form.cleaned_data:
                    instance = form.save(commit=False)
                    instance.tarih = tarih
                    instance.save()














class UretimSayiYuklemeForm(forms.Form):
    csv_file = forms.FileField(label='CSV Dosyasını Seçin')
    uretim_tarihi = forms.DateField(label='Üretim Tarihini Seçin', widget=forms.TextInput(attrs={'type': 'date'}))

class DepoForm(forms.ModelForm):
    class Meta:
        model = Depo
        fields = ['hammadde', 'miktar', 'kategori1', 'kategori2', 'kategori3']



class PersonelForm(forms.ModelForm):
    class Meta:
        model = Personel
        fields = ['ad', 'soyad', 'pozisyon', 'saat_ucreti', 'baslangic_tarihi', 'departman', 'telefon', 'eposta', 'dogum_tarihi']



# Giriş saati formu
class PersonelGirisSaatiForm(forms.ModelForm):
    class Meta:
        model = PersonelGunlukCalisma
        fields = ['personel', 'giris_saati']
        widgets = {
            'giris_saati': forms.TimeInput(attrs={'type': 'time', 'id': 'girisSaati', 'step': 1 }),
        }

    giris_saati = forms.TimeField(
        input_formats=['%H:%M', '%H:%M:%S'],  # Hem saat:dk hem de saat:dk:saniye formatlarını kabul et
        widget=forms.TimeInput(attrs={'type': 'time', 'id': 'girisSaati', 'step': 1 }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:  # Form bağlanmamışsa (ilk yükleme)
            self.fields['giris_saati'].initial = timezone.now().time().strftime('%H:%M')
class PersonelCikisSaatiForm(forms.ModelForm):
    class Meta:
        model = PersonelGunlukCalisma
        fields = ['personel', 'cikis_saati']  # Tarih formdan kaldırıldı
        widgets = {
            'cikis_saati': forms.TimeInput(attrs={'type': 'time', 'id': 'cikisSaati'}),
        }

    cikis_saati = forms.TimeField(
        input_formats=['%H:%M', '%H:%M:%S'],  # Hem saat:dk hem de saat:dk:saniye formatlarını kabul et
        widget=forms.TimeInput(attrs={'type': 'time', 'id': 'cikisSaati'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:  # Form bağlanmamışsa (ilk yükleme)
            self.fields['cikis_saati'].initial = timezone.now().time().strftime('%H:%M')


class PersonelMesaiPlanForm(forms.Form):
    csv_file = forms.FileField(label="Personel Mesai planini Yükleyin")



class SiparisForm(forms.Form):
    urun = forms.ModelChoiceField(queryset=Urun.objects.all())
    miktar = forms.IntegerField(min_value=1)