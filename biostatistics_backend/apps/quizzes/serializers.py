from rest_framework import serializers
from polymorphic.contrib.drf.serializers import PolymorphicSerializer

from .models import Quiz, Question, MultipleChoiceQuestion, EnterValueQuestion, AnswerOption, QuizContext


class AnswerOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerOption
        fields = ('id', 'text',)

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'text',)

class MultipChoiceSerializer(serializers.ModelSerializer):
    answer_options = AnswerOptionSerializer(many=True, read_only=True)

    class Meta:
        model = MultipleChoiceQuestion
        fields = ('id', 'text', 'answer_options',)

class EnterValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnterValueQuestion
        fields = ('id', 'text',)

class QuestionPolymorphicSerializer(PolymorphicSerializer):
    resource_type_field_name = 'question_type'
    model_serializer_mapping = {
        Question: QuestionSerializer,
        MultipleChoiceQuestion: MultipChoiceSerializer,
        EnterValueQuestion: EnterValueSerializer,
    }

    def to_resource_type(self, model_or_instance):
        name = model_or_instance._meta.object_name.lower()

        if name == "multiplechoicequestion":
            return "mcq"
        elif name == "entervaluequestion":
            return "text"

        return name

class QuizContextSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizContext
        fields = ('title', 'text', 'dataset_file',)

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionPolymorphicSerializer(many=True, read_only=True)
    contexts = QuizContextSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = '__all__'


class MCQAnswerSerializer(serializers.Serializer):
    question_type = serializers.CharField(default='mcq')
    question_id = serializers.IntegerField()
    selected_choices = serializers.ListField(child=serializers.IntegerField())

class EnterValueSerializer(serializers.Serializer):
    question_type = serializers.CharField(default='text')
    question_id = serializers.IntegerField()
    text_response = serializers.CharField()

class AnswerSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        answer_type = data.get('question_type')

        if answer_type == 'mcq':
            serializer = MCQAnswerSerializer(data=data)
        elif answer_type == 'text':
            serializer = EnterValueSerializer(data=data)
        else:
            raise serializers.ValidationError(f"Invalid type: {answer_type}")
        
        if not serializer.is_valid():
            raise serializers.ValidationError(serializer.errors)
        
        return serializer.validated_data

class QuizAttemptSerializer(serializers.Serializer):
    answers = AnswerSerializer(many=True)