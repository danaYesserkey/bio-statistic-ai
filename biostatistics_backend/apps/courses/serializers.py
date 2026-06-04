#third party modules
from rest_framework import serializers
# Local modules
from apps.courses.models import Course, Module, Lesson


# 1. Сначала описываем самый глубокий уровень — Уроки
class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "module", "lesson_name", "content_kz", "order"]


# 2. Сериализатор для Модулей (для создания и редактирования)
class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ["id", "course", "module_name", "order"]


# 3. СПЕЦИАЛЬНЫЙ сериализатор для Модулей со списком уроков внутри.
# Он используется только на чтение внутри курса.
class ModuleWithLessonsSerializer(serializers.ModelSerializer):
    # Тут магия: говорим Django взять LessonSerializer
    # и вытащить все уроки, связанные с этим модулем
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ["id", "module_name", "order", "lessons"]


# 4. Базовый сериализатор для Курсов (для списка курсов / создания)
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "course_name", "description"]


# 5. Главный вложенный сериализатор для страницы курса.
# Фронтенд вызовет его один раз и получит всё дерево.
class CourseDetailSerializer(serializers.ModelSerializer):
    # Подтягиваем модули, а внутри них автоматически подтянутся уроки
    modules = ModuleWithLessonsSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ["id", "course_name", "description", "modules"]
