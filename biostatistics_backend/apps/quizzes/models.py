from django.db import models
from polymorphic.models import PolymorphicModel


class Quiz(models.Model):
    lesson = models.OneToOneField('courses.Lesson', on_delete=models.CASCADE, related_name='quiz', unique=True)
    title = models.CharField(max_length=300, null=False)

class QuizAttempt(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField()
    completed_at = models.DateTimeField()
    passed = models.BooleanField(default=False)

class QuizContext(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='contexts')
    title = models.CharField(max_length=300, null=False)
    text = models.TextField(null=False)
    dataset_file = models.FileField(upload_to='derek', null=True, blank=True)

class Question(PolymorphicModel):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    context = models.ForeignKey(QuizContext, on_delete=models.CASCADE, related_name='questions', null=True, blank=True)
    text = models.TextField(null=False)

class MultipleChoiceQuestion(Question):
    pass

class EnterValueQuestion(Question):
    correct_value = models.CharField(max_length=70, null=False)

class AnswerOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answer_options')
    text = models.CharField(max_length=300, null=False)
    is_correct = models.BooleanField()