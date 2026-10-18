# Generated for the HealthRecord model.
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='HealthRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('patient_full_name', models.CharField(max_length=100, verbose_name='ФИО пациента')),
                ('birth_date', models.DateField(verbose_name='Дата рождения')),
                ('blood_type', models.CharField(choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')], max_length=3, verbose_name='Группа крови')),
                ('height_cm', models.PositiveSmallIntegerField(verbose_name='Рост (см)')),
                ('weight_kg', models.FloatField(verbose_name='Вес (кг)')),
                ('systolic_bp', models.PositiveSmallIntegerField(verbose_name='Верхнее давление')),
                ('diastolic_bp', models.PositiveSmallIntegerField(verbose_name='Нижнее давление')),
                ('heart_rate', models.PositiveSmallIntegerField(verbose_name='Пульс')),
                ('temperature_c', models.FloatField(verbose_name='Температура тела')),
                ('measurement_date', models.DateField(verbose_name='Дата измерения')),
                ('symptoms', models.JSONField(blank=True, default=list, verbose_name='Симптомы')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
            ],
            options={'verbose_name': 'Запись о здоровье', 'verbose_name_plural': 'Записи о здоровье', 'ordering': ['-measurement_date', 'patient_full_name']},
        ),
    ]
