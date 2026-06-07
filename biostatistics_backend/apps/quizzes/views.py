from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated

from .serializers import QuizSerializer, QuizAttemptSerializer
from .models import Quiz, Question, MultipleChoiceQuestion, EnterValueQuestion, AnswerOption, QuizAttempt
from apps.courses.models import Lesson
from apps.users.models import CustomUser


@api_view(['GET'])
def lesson_quiz(request, id):
    lesson = get_object_or_404(Lesson, id=id)

    quiz = get_object_or_404(Quiz, lesson_id=lesson.id)

    serializer = QuizSerializer(quiz)

    return Response(serializer.data)


class QuizSubmitCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, id=quiz_id)

        serializer = QuizAttemptSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
        
        answers = serializer.validated_data['answers']
        question_ids = [ans['question_id'] for ans in answers]
        valid_questions = Question.objects.filter(
            quiz_id=quiz_id, id__in=question_ids
        ).values_list('id', flat=True)

        if len(valid_questions) != len(set(question_ids)):
            return Response({"error": "One or more questions don't belong to this quiz!"}, status=status.HTTP_400_BAD_REQUEST)
        
        score = self._calculate_score(quiz_id, answers)
        passed = False
        if (score * 100) / len(valid_questions) >= 90:
            passed = True

        user = get_object_or_404(CustomUser, id=request.user.id)

        with transaction.atomic():
            attempt = QuizAttempt.objects.create(
                user=user,
                quiz=quiz,
                score=score,
                passed=passed,
                completed_at=timezone.now(),
            )

        return Response({
            "id": attempt.id,
            "quiz": attempt.quiz_id,
            "score": attempt.score,
            "completed_at": attempt.completed_at,
            "message": "Quiz ok!"
        })
    
    def _calculate_score(self, quiz_id, answers):
        total_score = 0

        for answer in answers:
            question_id = answer['question_id']
            question_type = answer['question_type']

            question = get_object_or_404(Question, id=question_id, quiz_id=quiz_id)

            if question_type == 'mcq':
                points = self._score_mcq(question, answer['selected_choices'])
            elif question_type == 'text':
                points = self._score_text(question, answer['text_response'])
            else:
                points = 0
            
            total_score += points
        
        return total_score
    
    def _score_mcq(self, question, selected_choices):
        if not isinstance(question, MultipleChoiceQuestion):
            return 0
        
        correct_options = set(
            AnswerOption.objects.filter(
                question_id=question.id,
                is_correct=True
            ).values_list('id', flat=True)
        )

        selected_set = set(selected_choices)

        if selected_set == correct_options:
            return 1
        
        return 0
    
    def _score_text(self, question, text_response):
        if not isinstance(question, EnterValueQuestion):
            return 0
        
        if text_response.strip().lower() == question.correct_value.lower():
            return 1
        
        return 0