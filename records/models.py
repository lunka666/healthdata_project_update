from django.db import models


class HealthRecord(models.Model):
    BLOOD_TYPES = [(v, v) for v in ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-')]

    patient_full_name = models.CharField('ФИО пациента', max_length=100)
    birth_date = models.DateField('Дата рождения')
    blood_type = models.CharField('Группа крови', max_length=3, choices=BLOOD_TYPES)
    height_cm = models.PositiveSmallIntegerField('Рост (см)')
    weight_kg = models.FloatField('Вес (кг)')
    systolic_bp = models.PositiveSmallIntegerField('Верхнее давление')
    diastolic_bp = models.PositiveSmallIntegerField('Нижнее давление')
    heart_rate = models.PositiveSmallIntegerField('Пульс')
    temperature_c = models.FloatField('Температура тела')
    measurement_date = models.DateField('Дата измерения')
    symptoms = models.JSONField('Симптомы', default=list, blank=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        ordering = ['-measurement_date', 'patient_full_name']
        verbose_name = 'Запись о здоровье'
        verbose_name_plural = 'Записи о здоровье'

    def __str__(self):
        return f'{self.patient_full_name} — {self.measurement_date}'
