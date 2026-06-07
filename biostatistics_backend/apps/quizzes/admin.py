from django.contrib import admin
from nested_admin.nested import NestedTabularInline, NestedStackedInline, NestedModelAdmin

from .models import (
    Quiz,
    QuizContext,
    MultipleChoiceQuestion,
    EnterValueQuestion,
    AnswerOption
)


class AnswerOptionInline(NestedTabularInline):
    model = AnswerOption

    def get_extra(self, request, obj = ..., **kwargs):
        return 0 if obj else 4

class MultipleChoiceInline(NestedStackedInline):
    model = MultipleChoiceQuestion
    extra = 0
    fields = ('quiz', 'text',)
    inlines = [AnswerOptionInline]

class EnterValueInline(NestedStackedInline):
    model = EnterValueQuestion
    extra = 0
    fields = ('quiz', 'text', 'correct_value',)

class QuizContextInline(NestedStackedInline):
    model = QuizContext
    extra = 0
    # fields = ('',)
    inlines = [MultipleChoiceInline, EnterValueInline]

class QuizAdmin(NestedModelAdmin):
    inlines = [QuizContextInline, MultipleChoiceInline, EnterValueInline]

admin.site.register(Quiz, QuizAdmin)