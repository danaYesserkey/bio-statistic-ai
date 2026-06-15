from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated

from .serializers import QuizSerializer, QuizAttemptSerializer, UserResponseSerializer
from .models import Quiz, Question, MultipleChoiceQuestion, EnterValueQuestion, AnswerOption, QuizAttempt, QuizResults
from apps.courses.models import Lesson
from apps.users.models import CustomUser


@api_view(['GET'])
def lesson_quiz(request, id):
    lesson = get_object_or_404(Lesson, id=id)

    quiz = get_object_or_404(Quiz, lesson_id=lesson.id)
    quiz_serializer = QuizSerializer(quiz)

    try:
        user = CustomUser.objects.get(id=request.user.id)
        last_attempt = QuizAttempt.objects.filter(user=user, quiz=quiz).order_by("-completed_at").first()
        result_serializer = UserResponseSerializer(last_attempt)
    finally:
        if last_attempt:
            for i in range(len(quiz_serializer.data["blocks"])):
                for j in range(len(quiz_serializer.data["blocks"][i]["questions"])):
                    question_id = quiz_serializer.data["blocks"][i]["questions"][j]["id"]
                    choice = next((value for value in result_serializer.data["quizresults_set"] if value["question"] == question_id), None)

                    if choice:
                        quiz_serializer.data["blocks"][i]["questions"][j]["user_answer"] = choice["answer"]
                        quiz_serializer.data["blocks"][i]["questions"][j]["is_correct"] = choice["is_correct"]
                        quiz_serializer.data["blocks"][i]["questions"][j]["correct_answer"] = choice["correct_answer"]
            # quiz_serializer.data["passed"] = last_attempt.passed
            
    return Response(quiz_serializer.data)


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
        
        results, score, user_answers = self._calculate_score(quiz_id, answers)
        passed = False
        score_percentage = (score * 100) / len(valid_questions)
        if score_percentage >= 90:
            passed = True

        user = get_object_or_404(CustomUser, id=request.user.id)

        with transaction.atomic():
            attempt = QuizAttempt.objects.create(
                user=user,
                quiz=quiz,
                score=score_percentage,
                passed=passed,
                completed_at=timezone.now()
            )
        
        user_results = []
        for u in user_answers:
            user_results.append(QuizResults(
                attempt=attempt,
                question=u["q"],
                answer=u["a"],
                correct_answer=u["correct_answer"],
                is_correct=u["is_correct"])
            )
            
            print(u["a"])
        
        QuizResults.objects.bulk_create(user_results)

        return Response({
            "id": attempt.id,
            "quiz": attempt.quiz_id,
            "total_questions": len(valid_questions),
            "score": score,
            "score_percentage": attempt.score,
            "completed_at": attempt.completed_at,
            "passed": attempt.passed,
            "results": results,
        })
    
    def _calculate_score(self, quiz_id, answers):
        total_score = 0
        results = []
        user_answers = []

        for answer in answers:
            question_id = answer['question_id']
            question_type = answer['question_type']

            question = get_object_or_404(Question, id=question_id, quiz_id=quiz_id)

            if question_type == 'mcq':
                is_correct, points, correct_answer = self._score_mcq(question, answer['selected_choice'])
                user_response = answer['selected_choice']
            elif question_type == 'text':
                is_correct, points, correct_answer = self._score_text(question, answer['text_response'])
                user_response = answer['text_response']
            else:
                is_correct, points, correct_answer = False, 0, None
                user_response = None
            
            total_score += points

            result = {
                "question_id": question_id,
                "question_type": question_type,
                "text": question.text,
                "is_correct": is_correct,
                "user_answer": user_response,
                "correct_answer": correct_answer,
            }
            results.append(result)

            user_answer = {"q": question, "a": user_response, "is_correct": is_correct, "correct_answer": correct_answer}
            user_answers.append(user_answer)
        
        return results, total_score, user_answers
    
    def _score_mcq(self, question, selected_choice):
        if not isinstance(question, MultipleChoiceQuestion):
            return False, 0, None
        
        correct_option = AnswerOption.objects.get(question_id=question.id, is_correct=True)

        is_correct = selected_choice == correct_option.id
        points = 1 if is_correct else 0
        
        return is_correct, points, correct_option.id
    
    def _score_text(self, question, text_response):
        if not isinstance(question, EnterValueQuestion):
            return False, 0, None
        
        is_correct = text_response.strip().lower() == question.correct_value.lower()
        points = 1 if is_correct else 0
        
        return is_correct, points, question.correct_value