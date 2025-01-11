# Generated by Django 5.1.4 on 2025-01-09 16:51

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='FormulCSVFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('file', models.FileField(upload_to='csv_files/')),
                ('Yukleme_tarihi', models.DateTimeField(default=django.utils.timezone.now)),
                ('Formul_tarihi', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='GunlukGelir',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tarih', models.DateField(default=django.utils.timezone.now)),
                ('toplam_gelir', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='GunlukGider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tarih', models.DateField(default=django.utils.timezone.now)),
                ('hammadde_gideri', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('personel_planlanan', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('personel_ilave', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('sabit_gider_payi', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Hammadde',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hammadde_kategori', models.CharField(choices=[('bakliyat', 'Bakliyat'), ('buzdolabı', 'Buzdolabı'), ('meyve_sebze', 'Meyve_Sebze'), ('ambalajli_urunler', 'Ambalajli_Urunler'), ('ambalaj_urtm', 'Ambalaj_Urtm'), ('baharat', 'Baharat'), ('donuk', 'Donuk'), ('katki_maddesi', 'Katki_Maddesi'), ('kuruyemis', 'Kuruyemis'), ('uretim', 'Uretim'), ('genel', 'Genel'), ('etiket', 'Etiket')], max_length=100)),
                ('hammadde_adi', models.CharField(max_length=100)),
                ('birim', models.CharField(choices=[('kg', 'Kilogram'), ('Ad', 'Adet')], max_length=50)),
                ('diger_notlar', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Hammadde',
                'verbose_name_plural': 'Hammadde',
                'ordering': ['hammadde_adi'],
            },
        ),
        migrations.CreateModel(
            name='Muhasebe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('islem_turu', models.CharField(max_length=50)),
                ('miktar', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tarih', models.DateField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': 'Finans',
                'verbose_name_plural': 'Muhasebe',
            },
        ),
        migrations.CreateModel(
            name='Musteri',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('musteri_adi', models.CharField(max_length=255)),
                ('telefon', models.CharField(max_length=20)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('adres', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Musteri',
                'verbose_name_plural': 'Musteri',
            },
        ),
        migrations.CreateModel(
            name='Personel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ad', models.CharField(max_length=100)),
                ('soyad', models.CharField(max_length=100)),
                ('pozisyon', models.CharField(max_length=100)),
                ('saat_ucreti', models.DecimalField(decimal_places=2, max_digits=10)),
                ('baslangic_tarihi', models.DateField()),
                ('departman', models.CharField(max_length=100)),
                ('telefon', models.CharField(blank=True, max_length=15, null=True)),
                ('eposta', models.EmailField(blank=True, max_length=254, null=True)),
                ('dogum_tarihi', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Resept',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resept_adi', models.CharField(max_length=255)),
                ('musteriUrn', models.CharField(choices=[('kesko', 'Kesko'), ('direk', 'Direk'), ('hok', 'HOK'), ('corint', 'Corint')], max_length=50)),
                ('Urn_kategori', models.CharField(choices=[('salata', 'Salata'), ('yoğurt', 'Yoğurt'), ('wrap', 'Wrap'), ('bowl ', 'Bowl '), ('sandwich', 'Sandwich'), ('kilo', 'Kilo'), ('ateria', 'Ateria')], max_length=50)),
                ('toplam_fiyat', models.DecimalField(decimal_places=4, max_digits=10)),
                ('resept_gram', models.DecimalField(decimal_places=4, max_digits=10)),
            ],
            options={
                'verbose_name': 'Resept',
                'verbose_name_plural': 'Resept',
            },
        ),
        migrations.CreateModel(
            name='SabitGider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gider_tipi', models.CharField(choices=[('kira', 'Kira'), ('kominal', 'Kominal'), ('reklam', 'Reklam'), ('transport', 'Transport'), ('bakim', 'Bakım/Onarım')], max_length=20)),
                ('tutar', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tarih', models.DateField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='SatinAlinanlar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('satin_alma_tarihi', models.DateField()),
                ('hammadde_adi', models.CharField(max_length=100)),
                ('miktar', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fiyat', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tedarikci', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='SatinAlma',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('giris_tarihi', models.DateField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Tedarikci_SRK',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tedarikciAdi', models.CharField(max_length=255)),
                ('adres', models.TextField()),
                ('telefonNumarasi', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=254)),
                ('vergiNumarasi', models.CharField(max_length=50)),
                ('website', models.URLField(blank=True, null=True)),
                ('iletisimKisi', models.CharField(max_length=255)),
                ('urunlerHizmetler', models.TextField()),
                ('bankaHesapBilgileri', models.TextField()),
                ('anlasmaTarihi', models.DateField()),
                ('durum', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], max_length=50)),
                ('ekNotlar', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Tedarikci',
                'verbose_name_plural': 'Tedarikci',
            },
        ),
        migrations.CreateModel(
            name='UretimIstatistik',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tarih', models.DateField(default=django.utils.timezone.now)),
                ('urun_adi', models.CharField(choices=[('Wrap', 'Wrap'), ('Blow', 'Blow'), ('Salad', 'Salad'), ('Jogurt', 'Jogurt'), ('Musli', 'Musli'), ('Sicak', 'Sicak'), ('Sandwich', 'Sandwich'), ('Kilo', 'Kilo')], max_length=50)),
                ('uretim_adedi', models.PositiveIntegerField()),
                ('kac_kisi_calisti', models.PositiveIntegerField()),
                ('baslama_saati', models.TimeField()),
                ('bitis_saati', models.TimeField()),
                ('toplam_calisma_saati', models.FloatField(editable=False)),
                ('dakika_uretim', models.FloatField(editable=False)),
                ('maas_saat', models.FloatField(blank=True, default=17, null=True)),
                ('maliyet_uretim', models.FloatField(editable=False)),
                ('notlar', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Uretim statistik',
                'verbose_name_plural': 'Uretim statistik',
                'permissions': [('view_raporlar', 'Can view raporlar')],
            },
        ),
        migrations.CreateModel(
            name='Urun',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isim', models.CharField(max_length=255)),
                ('varsayilan_fiyat', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('telefon', models.CharField(blank=True, max_length=15, null=True)),
                ('adres', models.TextField(blank=True, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Depo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('miktar', models.DecimalField(decimal_places=2, max_digits=10)),
                ('kategori1', models.DecimalField(decimal_places=2, default=100, max_digits=10)),
                ('kategori2', models.DecimalField(decimal_places=2, default=80, max_digits=10)),
                ('kategori3', models.DecimalField(decimal_places=2, default=50, max_digits=10)),
                ('hammadde_maliyet', models.DecimalField(decimal_places=2, default=20, max_digits=10)),
                ('hammadde', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appsef.hammadde')),
            ],
            options={
                'verbose_name': 'Depo',
                'verbose_name_plural': 'Depolar',
            },
        ),
        migrations.CreateModel(
            name='PersonelGunlukCalisma',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tarih', models.DateField(default=django.utils.timezone.now)),
                ('giris_saati', models.TimeField()),
                ('cikis_saati', models.TimeField(blank=True, null=True)),
                ('personel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appsef.personel')),
            ],
        ),
        migrations.CreateModel(
            name='Resept_icerigi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('miktar', models.DecimalField(decimal_places=4, max_digits=10)),
                ('gurup', models.DecimalField(decimal_places=0, max_digits=2)),
                ('sira', models.DecimalField(decimal_places=0, max_digits=2)),
                ('uretim_safhasi', models.CharField(choices=[('karisim', 'Karisim'), ('paketleme', 'Paketleme'), ('kaynatma', 'Kaynatma'), ('ambalaj', 'Ambalaj'), ('etiket', 'Etiket'), ('yogurt', 'Yogurt')], max_length=50)),
                ('hhmmadde', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appsef.hammadde')),
                ('resept', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appsef.resept')),
            ],
            options={
                'verbose_name': 'Resept_icerikleri',
                'verbose_name_plural': 'Resept_icerikleri',
            },
        ),
        migrations.CreateModel(
            name='Resept_maliyet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hammaddeTopMaliyet', models.DecimalField(decimal_places=4, max_digits=10, null=True)),
                ('resept', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appsef.resept')),
            ],
        ),
        migrations.CreateModel(
            name='SatinAlmaList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('miktar', models.DecimalField(decimal_places=1, default=0, max_digits=10)),
                ('fiyat', models.DecimalField(decimal_places=4, default=0, max_digits=10)),
                ('toplam_maliyet', models.DecimalField(blank=True, decimal_places=2, max_digits=10)),
                ('hammadde', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appsef.hammadde')),
                ('satin_alma', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='satinalmalist_set', to='appsef.satinalma')),
            ],
        ),
        migrations.CreateModel(
            name='Siparis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tarih', models.DateTimeField(auto_now_add=True)),
                ('durum', models.CharField(choices=[('beklemede', 'Beklemede'), ('onaylandi', 'Onaylandı'), ('reddedildi', 'Reddedildi')], default='beklemede', max_length=20)),
                ('kullanici', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='siparisler', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='satinalma',
            name='tedarikci',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appsef.tedarikci_srk'),
        ),
        migrations.CreateModel(
            name='Uretim',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uretim_tarihi', models.DateField(default=django.utils.timezone.now)),
                ('musteri', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='appsef.musteri')),
            ],
            options={
                'verbose_name': 'Uretimler',
                'verbose_name_plural': 'Uretimler',
            },
        ),
        migrations.CreateModel(
            name='UretimDetay',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('miktar', models.PositiveIntegerField()),
                ('tarih', models.DateField(blank=True, editable=False, null=True)),
                ('musteri', models.CharField(blank=True, editable=False, max_length=255, null=True)),
                ('resept_fiyati', models.DecimalField(blank=True, decimal_places=2, editable=False, max_digits=10, null=True)),
                ('Udetay', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appsef.uretim')),
                ('Uresept', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appsef.resept')),
            ],
        ),
        migrations.CreateModel(
            name='KullaniciUrunFiyati',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fiyat', models.DecimalField(decimal_places=2, max_digits=10)),
                ('kullanici', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='urun_fiyatlari', to=settings.AUTH_USER_MODEL)),
                ('urun', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='kullanici_fiyatlari', to='appsef.urun')),
            ],
        ),
    ]