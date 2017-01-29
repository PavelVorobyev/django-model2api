# -*- coding: utf-8 -*-

from django.http import JsonResponse, QueryDict
from django.apps import apps
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict


# Список всех доступных моделей в проекте
def index(request):
    models = apps.get_models()
    data = {}

    for m in models:
        # Формируем имя модели для поиска в проекте через get_model
        model_path = '.'.join([m._meta.app_label, m._meta.model_name])

        # Список моделей и URL ресурсов для обращения к моделям
        # Для построения относительного URL используется паттер с именем api-model
        data[model_path] = request.build_absolute_uri(reverse('api-model', args=[model_path]))
    return JsonResponse(data)


# Получение объектов с фильтрацией, сортировкой и ограничением количества
# ! по умолчанию количество возвращаемых объектов - 100
def find(request, model):
    args = request.GET.dict()
    resource = apps.get_model(model)

    # Все доступные поля в модели
    fields = [field.name for field in resource._meta.get_fields()]

    # Поля, по которым делается filter, сами фильтруются по списку fields
    query = {k: v for k, v in args.iteritems() if k in fields}
    sort = args.get('sort', 'id')  # по умолчанию сортировка по id
    limit = int(args.get('limit', 100))

    objects = resource.objects

    if query:
        objects = objects.filter(**query)

    # конструкция list(...values()) для удобства сериализации в JSON
    data = list(objects.all().order_by(sort)[:limit].values())

    return JsonResponse(data, safe=False)


# Удаление объекта по имени модели и первичному ключу
def delete(request, model, pk):
    resource = apps.get_model(model)
    try:
        data = resource.objects.get(pk=pk)
    except resource.DoesNotExist:
        # Минимальное отлавливание ошибок
        response = {'response': 'Fail. Object {} does not exists'.format(pk)}
    else:
        data.delete()
        response = {'response': 'Successful'}

    return JsonResponse(response, safe=False)


# Создание объекта модели по имени
def create(request, model):
    args = request.POST.dict()

    resource = apps.get_model(model)
    fields = [field.name for field in resource._meta.get_fields()]
    query = {k: v for k, v in args.iteritems() if k in fields}

    resource.objects.create(**query)

    response = {'response': 'Successful'}

    return JsonResponse(response, safe=True)


# Получение отдельного объекта модели по первичному ключу
def get(request, model, pk):
    resource = apps.get_model(model)
    try:
        data = resource.objects.get(pk=pk)
    except resource.DoesNotExist:
        response = {'response': 'Fail. Object {} does not exists'.format(pk)}
    else:
        response = model_to_dict(data)

    return JsonResponse(response, safe=False)


# Обновление отдельного объекта модели по первичному ключу
def edit(request, model, pk):
    # При запросах методом PUT приходится
    args = QueryDict(request.body).dict()

    resource = apps.get_model(model)
    fields = [field.name for field in resource._meta.get_fields()]
    query = {k: v for k, v in args.iteritems() if k in fields}

    try:
        resource.objects.filter(id=pk).update(**query)
    except:
        response = {'response': 'Fail'}
    else:
        response = {'response': 'Successful'}

    return JsonResponse(response, safe=False)


# Декоратор @csrf_exempt используются как workaround. В продуктиве лучше предусмотреть авторизацию
# Функция dispatcher используется, чтобы к одному и тому же url можно было обращаться методами GET и POST
@csrf_exempt
def dispatcher(request, model):
    if request.method == 'GET':
        return find(request, model)
    elif request.method == 'POST':
        return create(request, model)


@csrf_exempt
def object_dispatcher(request, model, pk):
    if request.method == 'GET':
        return get(request, model, pk)
    elif request.method == 'PUT':
        return edit(request, model, pk)
    elif request.method == 'DELETE':
        return delete(request, model, pk)
