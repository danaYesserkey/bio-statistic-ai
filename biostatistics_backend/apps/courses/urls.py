from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, ModuleViewSet, LessonViewSet, lesson_contents

from apps.quizzes.views import lesson_quiz

# Создаем роутер и регистрируем наши ModelViewSet'ы
router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'modules', ModuleViewSet, basename='module')
router.register(r'lessons', LessonViewSet, basename='lesson')

# Урлы приложения просто включают в себя всё, что сгенерировал роутер
urlpatterns = [
    path('', include(router.urls)),
    path('lessons/<int:id>/contents/', lesson_contents),
    path('lessons/<int:id>/quiz/', lesson_quiz),
]