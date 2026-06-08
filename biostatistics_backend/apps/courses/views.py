from django.core.cache import cache
from django.shortcuts import get_object_or_404 # noqa
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.courses.models import Course, Module, Lesson
from apps.courses.serializers import (
    CourseSerializer, 
    CourseDetailSerializer, 
    ModuleSerializer, 
    LessonSerializer,
    ContentPolymorphicSerializer,
)
from apps.courses.permissions import IsAdminOrTeacherOrReadOnly


@api_view(['GET'])
def lesson_contents(request, id):
    lesson = get_object_or_404(Lesson, id=id)
    serializer = ContentPolymorphicSerializer(lesson.contents.all(), many=True)
    return Response(serializer.data)


# Выносим логику очистки в хелпер, так как курс может измениться через Модуль или Урок
def invalidate_course_cache(course_id):
    if course_id:
        cache.delete(f"course_detail_{course_id}")


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().prefetch_related("modules__lessons")
    permission_classes = [IsAdminOrTeacherOrReadOnly]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CourseDetailSerializer
        return CourseSerializer

    def retrieve(self, request, *args, **kwargs):
        course_id = kwargs.get("pk")

        # Строим уникальный ключ для кэша, учитывая ID курса И статус пользователя (опционально)
        # Если данные курса для всех одинаковые (и для админа, и для студента):
        cache_key = f"course_detail_{course_id}"

        # Если данные отличаются для админа и гостя, добавляем маркер:
        # is_staff = request.user.is_staff if request.user.is_authenticated else False
        # cache_key = f"course_detail_{course_id}_staff_{is_staff}"

        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        # Если в кэше нет — выполняем стандартный retrieve
        response = super().retrieve(request, *args, **kwargs)

        # Сохраняем в кэш именно response.data (dict), а не сам объект Response
        cache.set(cache_key, response.data, 7200)

        return response

    # Если сам курс обновили/удалили — чистим только его кэш
    def perform_update(self, serializer):
        instance = serializer.save()
        invalidate_course_cache(instance.id)

    def perform_destroy(self, instance):
        invalidate_course_cache(instance.id)
        instance.delete()


class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [IsAdminOrTeacherOrReadOnly]

    def perform_create(self, serializer):
        instance = serializer.save()
        invalidate_course_cache(
            instance.course_id
        )  # Чистим только тот курс, куда добавлен модуль

    def perform_update(self, serializer):
        instance = serializer.save()
        invalidate_course_cache(instance.course_id)

    def perform_destroy(self, instance):
        course_id = instance.course_id
        instance.delete()
        invalidate_course_cache(course_id)


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAdminOrTeacherOrReadOnly]

    def perform_create(self, serializer):
        instance = serializer.save()
        # Урок привязан к модулю, а модуль к курсу
        course_id = instance.module.course_id if instance.module else None
        invalidate_course_cache(course_id)

    def perform_update(self, serializer):
        instance = serializer.save()
        course_id = instance.module.course_id if instance.module else None
        invalidate_course_cache(course_id)

    def perform_destroy(self, instance):
        course_id = instance.module.course_id if instance.module else None
        instance.delete()
        invalidate_course_cache(course_id)