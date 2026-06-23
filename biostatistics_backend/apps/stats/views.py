from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import CourseStatistics
from apps.courses.models import Lesson
from apps.users.models import CustomUser
from apps.quizzes.models import Quiz


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def lesson_score(request, id):
    lesson = get_object_or_404(Lesson, id=id)
    user = get_object_or_404(CustomUser, id=request.user.id)

    try:
        quiz = Quiz.objects.filter(lesson=lesson)
        if quiz:
            print(quiz)
            return Response({"message": "Сабақты аяқтау үшін тест тапсыруыңыз керек"}, status=status.HTTP_400_BAD_REQUEST)

        previous_lesson = Lesson.objects.filter(id__lt=lesson.id).order_by('-id').first()
        previous_stats = CourseStatistics.objects.get(lesson=previous_lesson, user=user, course=previous_lesson.module.course)

        if previous_lesson:
            if previous_stats.completed:                
                CourseStatistics.objects.create(course=lesson.module.course, module=lesson.module, lesson=lesson, user=user, completed=True)
                return Response({"message": "Сабақ сәтті аяқталды"}, status=status.HTTP_201_CREATED)
    except Exception as e:
        print(e)
        if not previous_lesson:
            CourseStatistics.objects.create(course=lesson.module.course, module=lesson.module, lesson=lesson, user=user, completed=True)
            return Response({"message": "Сабақ сәтті аяқталды"}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"message": "Алдыңғы сабақты аяқтаңыз"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)