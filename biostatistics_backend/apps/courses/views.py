from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view

from apps.courses.models import Course, Module, Lesson
from apps.courses.serializers import (
    CourseSerializer, 
    CourseDetailSerializer, 
    ModuleSerializer, 
    LessonSerializer,
    ContentPolymorphicSerializer
)
from apps.courses.permissions import IsAdminOrTeacherOrReadOnly

class CourseViewSet(viewsets.ModelViewSet):
    # prefetch_related вытягивает модули и уроки за 3 быстрых запроса в БД, решая проблему N+1
    queryset = Course.objects.all().prefetch_related('modules__lessons')
    permission_classes = [IsAdminOrTeacherOrReadOnly]

    def get_serializer_class(self):
        # Если это GET-запрос на конкретный курс (/api/courses/<id>/) — отдаем жирную структуру
        if self.action == 'retrieve':
            return CourseDetailSerializer
        # Для списка (/api/courses/) или создания/удаления отдаем плоский сериализатор
        return CourseSerializer

    # Кэшируем детальную страницу курса на 2 часа (7200 секунд)
    @method_decorator(cache_page(7200, key_prefix="course_detail"))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [IsAdminOrTeacherOrReadOnly]

    def perform_create(self, serializer):
        # При создании модуля сбрасываем кэш курсов, чтобы фронт сразу увидел изменения
        cache.clear()
        super().perform_create(serializer)

    def perform_update(self, serializer):
        cache.clear()
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        cache.clear()
        instance.delete()


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAdminOrTeacherOrReadOnly]

    # Точно так же чистим кэш при любых изменениях в уроках
    def perform_create(self, serializer):
        cache.clear()
        super().perform_create(serializer)

    def perform_update(self, serializer):
        cache.clear()
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        cache.clear()
        instance.delete()

@api_view(['GET'])
def lesson_contents(request, id):
    lesson = get_object_or_404(Lesson, id=id)

    contents = lesson.contents.all()

    serializer = ContentPolymorphicSerializer(contents, many=True)

    return Response(serializer.data)