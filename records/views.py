import os
from datetime import date

from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET, require_POST

from .forms import HealthRecordForm, UploadFileForm
from .models import HealthRecord
from .validators import validate_record_dict
from .utils import safe_filename, records_to_json_bytes, parse_data_bytes, DataFormatError


def home(request):
    json_count = len([f for f in os.listdir(settings.DATA_JSON_DIR) if f.lower().endswith('.json')])
    return render(request, 'records/home.html', {'json_count': json_count, 'db_count': HealthRecord.objects.count()})


def _record_values(record):
    return {
        'patient_full_name': record['patient_full_name'],
        'birth_date': record['birth_date'],
        'blood_type': record['blood_type'],
        'height_cm': record['height_cm'],
        'weight_kg': record['weight_kg'],
        'systolic_bp': record['systolic_bp'],
        'diastolic_bp': record['diastolic_bp'],
        'heart_rate': record['heart_rate'],
        'temperature_c': record['temperature_c'],
        'measurement_date': record['measurement_date'],
        'symptoms': record['symptoms'],
    }


def _same_record(record):
    qs = HealthRecord.objects.filter(
        patient_full_name=record['patient_full_name'], birth_date=record['birth_date'],
        blood_type=record['blood_type'], height_cm=record['height_cm'],
        weight_kg=record['weight_kg'], systolic_bp=record['systolic_bp'],
        diastolic_bp=record['diastolic_bp'], heart_rate=record['heart_rate'],
        temperature_c=record['temperature_c'], measurement_date=record['measurement_date'],
    )
    for existing in qs:
        if existing.symptoms == record['symptoms']:
            return True
    return False


def create_record(request):
    if request.method == 'POST':
        form = HealthRecordForm(request.POST)
        if form.is_valid():
            record = form.to_record_dict()
            errors = validate_record_dict(record)
            if errors:
                for err in errors:
                    messages.error(request, err)
            else:
                destination = request.POST.get('destination', 'json')
                if destination == 'db':
                    if _same_record(record):
                        messages.warning(request, 'Такая запись уже есть в базе данных. Дубликат не добавлен.')
                    else:
                        HealthRecord.objects.create(**_record_values(record))
                        messages.success(request, 'Запись успешно сохранена в SQLite.')
                    return redirect('records:create')
                filename = safe_filename('.json')
                with open(settings.DATA_JSON_DIR / filename, 'wb') as fh:
                    fh.write(records_to_json_bytes([record]))
                messages.success(request, f'Данные сохранены в JSON-файл «{filename}».')
                return redirect('records:create')
    else:
        form = HealthRecordForm()
    return render(request, 'records/create_form.html', {'form': form})


def edit_record(request, pk):
    instance = get_object_or_404(HealthRecord, pk=pk)
    initial = {
        'patient_full_name': instance.patient_full_name, 'birth_date': instance.birth_date,
        'blood_type': instance.blood_type, 'height_cm': instance.height_cm,
        'weight_kg': instance.weight_kg, 'systolic_bp': instance.systolic_bp,
        'diastolic_bp': instance.diastolic_bp, 'heart_rate': instance.heart_rate,
        'temperature_c': instance.temperature_c, 'measurement_date': instance.measurement_date,
        'symptoms': '\n'.join(instance.symptoms or []),
    }
    if request.method == 'POST':
        form = HealthRecordForm(request.POST)
        if form.is_valid():
            record = form.to_record_dict()
            errors = validate_record_dict(record)
            if errors:
                for err in errors:
                    messages.error(request, err)
            else:
                if _same_record(record) and not _same_record_for_instance(record, instance):
                    messages.error(request, 'Такая запись уже существует. Изменения не сохранены.')
                else:
                    for key, value in _record_values(record).items():
                        setattr(instance, key, value)
                    instance.save()
                    messages.success(request, 'Запись обновлена.')
                    return redirect('/data/?source=db')
    else:
        form = HealthRecordForm(initial=initial)
    return render(request, 'records/edit_form.html', {'form': form, 'record': instance})


def _same_record_for_instance(record, instance):
    return (instance.patient_full_name == record['patient_full_name'] and
            instance.birth_date.isoformat() == record['birth_date'] and
            instance.blood_type == record['blood_type'] and instance.height_cm == record['height_cm'] and
            instance.weight_kg == record['weight_kg'] and instance.systolic_bp == record['systolic_bp'] and
            instance.diastolic_bp == record['diastolic_bp'] and instance.heart_rate == record['heart_rate'] and
            instance.temperature_c == record['temperature_c'] and
            instance.measurement_date.isoformat() == record['measurement_date'] and
            (instance.symptoms or []) == record['symptoms'])


@require_POST
def delete_record(request, pk):
    record = get_object_or_404(HealthRecord, pk=pk)
    record.delete()
    messages.success(request, 'Запись удалена из базы данных.')
    return redirect('/data/?source=db')


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded = form.cleaned_data['data_file']
            filename = safe_filename('.json')
            file_path = settings.DATA_JSON_DIR / filename
            with open(file_path, 'wb') as fh:
                for chunk in uploaded.chunks():
                    fh.write(chunk)
            try:
                with open(file_path, 'rb') as fh:
                    records = parse_data_bytes(fh.read(), '.json')
                all_errors = []
                for idx, record in enumerate(records, start=1):
                    for err in validate_record_dict(record):
                        all_errors.append(f'Запись №{idx}: {err}')
                if all_errors:
                    raise DataFormatError('; '.join(all_errors))
            except DataFormatError as exc:
                if file_path.exists():
                    os.remove(file_path)
                messages.error(request, f'Файл не прошёл проверку и был удалён. Причина: {exc}')
                return redirect('records:upload')
            messages.success(request, f'Файл загружен: {filename} ({len(records)} записей).')
            return redirect('records:upload')
    else:
        form = UploadFileForm()
    return render(request, 'records/upload_form.html', {'form': form})


def _json_records():
    records, broken_files = [], []
    for filename in sorted(os.listdir(settings.DATA_JSON_DIR)):
        file_path = settings.DATA_JSON_DIR / filename
        if not file_path.is_file() or not filename.lower().endswith('.json'):
            continue
        try:
            with open(file_path, 'rb') as fh:
                items = parse_data_bytes(fh.read(), '.json')
            for item in items:
                records.append({**item, 'source_file': filename, 'id': None})
        except DataFormatError as exc:
            broken_files.append((filename, str(exc)))
    return records, broken_files


def view_data(request):
    source = request.GET.get('source', 'json')
    if source not in ('json', 'db'):
        source = 'json'
    query = request.GET.get('q', '').strip()
    broken_files = []
    if source == 'db':
        qs = HealthRecord.objects.all()
        if query:
            from django.db.models import Q
            qs = qs.filter(Q(patient_full_name__icontains=query) | Q(blood_type__icontains=query) | Q(symptoms__icontains=query))
        records = [{
            'id': r.pk, 'source_file': 'SQLite', 'patient_full_name': r.patient_full_name,
            'birth_date': r.birth_date.isoformat(), 'blood_type': r.blood_type,
            'height_cm': r.height_cm, 'weight_kg': r.weight_kg,
            'systolic_bp': r.systolic_bp, 'diastolic_bp': r.diastolic_bp,
            'heart_rate': r.heart_rate, 'temperature_c': r.temperature_c,
            'measurement_date': r.measurement_date.isoformat(), 'symptoms': r.symptoms or [],
        } for r in qs]
    else:
        records, broken_files = _json_records()
    return render(request, 'records/view_data.html', {
        'records': records, 'broken_files': broken_files,
        'no_files': not records and not broken_files, 'source': source, 'query': query,
    })


@require_GET
def ajax_search(request):
    query = request.GET.get('q', '').strip()
    from django.db.models import Q
    qs = HealthRecord.objects.all()
    if query:
        qs = qs.filter(Q(patient_full_name__icontains=query) | Q(blood_type__icontains=query) | Q(symptoms__icontains=query))
    results = [{
        'id': r.pk, 'patient_full_name': r.patient_full_name, 'birth_date': r.birth_date.isoformat(),
        'blood_type': r.blood_type, 'height_cm': r.height_cm, 'weight_kg': r.weight_kg,
        'systolic_bp': r.systolic_bp, 'diastolic_bp': r.diastolic_bp, 'heart_rate': r.heart_rate,
        'temperature_c': r.temperature_c, 'measurement_date': r.measurement_date.isoformat(),
        'symptoms': r.symptoms or [],
    } for r in qs[:200]]
    return JsonResponse({'results': results})
