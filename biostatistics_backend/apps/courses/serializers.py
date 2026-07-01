#third party modules
from rest_framework import serializers
from polymorphic.contrib.drf.serializers import PolymorphicSerializer
# Local modules
from apps.courses.models import Course, Module, Lesson, Content
from apps.stats.models import CourseStatistics

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


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = [
            'id', 
            'lesson', 
            'order', 
            'file', 
            'original_filename', 
            'file_size', 
            'mime_type', 
            'created_at'
        ]
        # Эти поля мы запрещаем передавать в POST-запросе, 
        # потому что модель собирает их сама под капотом
        read_only_fields = ['original_filename', 'file_size', 'mime_type', 'created_at']


class LessonDetailSerializer(serializers.ModelSerializer):
    contents = ContentSerializer(many=True, read_only=True)
    has_access = serializers.BooleanField(default=True)
    has_quiz = serializers.SerializerMethodField()
    can_score = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ["id", "module", "lesson_name", "order", "contents", "has_access", "has_quiz", "can_score"]

    def get_has_quiz(self, obj):
        return hasattr(obj, 'quiz') and obj.quiz is not None

    def get_can_score(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False

        try:
            stats = CourseStatistics.objects.get(lesson=obj, user=request.user)
            return not stats.completed
        except CourseStatistics.DoesNotExist:
            return True