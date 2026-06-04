from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase
from rest_framework import status

from apps.courses.models import Course

User = get_user_model()

class CourseAPITestCase(APITestCase):
    def setUp(self):
    # Создаем тестовый курс
        self.course = Course.objects.create(course_name="Тестовый курс", description="Описание")
            
        # Автоматически генерируем урлы! Нам больше не важны префиксы в urls.py
        self.url_list = reverse('course-list') 
        self.url_detail = reverse('course-detail', kwargs={'pk': self.course.id})
            
            # Добавляем 'username' в аргументы, так как твой менеджер его требует
        self.student = User.objects.create_user(
            username="test_student",  # <-- Добавили
            email="stud@test.com", 
            password="password", 
            role="STUDENT"
        )
        self.teacher = User.objects.create_user(
            username="test_teacher",  # <-- Добавили
            email="teach@test.com", 
            password="password", 
            role="TEACHER"
        )

    def test_student_cannot_create_course(self):
        """Проверяем, что студент не может создать курс (Защита пермишна)"""
        self.client.force_authenticate(user=self.student)
        data = {"course_name": "Новый курс"}
        response = self.client.post(self.url_list, data)
        
        # Ожидаем 403 Forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_can_create_course(self):
        """Проверяем, что препод может создать курс"""
        self.client.force_authenticate(user=self.teacher)
        data = {"course_name": "Курс от препода", "description": "Инфо"}
        response = self.client.post(self.url_list, data)
        
        # Ожидаем 201 Created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_anyone_can_view_course_detail(self):
        """Проверяем, что детальный просмотр доступен и возвращает вложенную структуру"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.url_detail)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем, что вложенный сериализатор отработал и отдал поле modules
        self.assertIn("modules", response.data)