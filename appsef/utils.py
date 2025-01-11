import calendar
from django.db.models import Sum  # Sum fonksiyonunu içe aktarın
from .models import SabitGider  # SabitGider modelini içe aktarın

def ayin_calisma_gunleri(year, month):
    c = calendar.Calendar(firstweekday=calendar.MONDAY)
    month_days = c.itermonthdays2(year, month)
    workdays = [day for day, weekday in month_days if day != 0 and weekday < 6] # <5 +cumaartesi icin <6
    return len(workdays)

def günlük_sabit_maliyet_pay_hesapla(month, year):
    workdays = ayin_calisma_gunleri(year, month)
    if workdays == 0:
        return 0
    total_fixed_costs = SabitGider.objects.filter(tarih__year=year, tarih__month=month).aggregate(Sum('tutar'))['tutar__sum'] or 0
    return total_fixed_costs / workdays if workdays > 0 else 0

