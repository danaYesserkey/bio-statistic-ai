from rest_framework import serializers
from polymorphic.contrib.drf.serializers import PolymorphicSerializer

from .models import Quiz, Question, MultipleChoiceQuestion, EnterValueQuestion, AnswerOption, QuizContext, WithQuizContext, WithoutQuizContext


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

class ContextSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizContext
        fields = '__all__'

class WithContextSerializer(serializers.ModelSerializer):
    class Meta:
        model = WithQuizContext
        fields = ('title', 'text', 'dataset_file',)

class WithoutContextSerializer(serializers.ModelSerializer):
    class Meta:
        model = WithoutQuizContext
        fields = '__all__'

class QuizContextSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        QuizContext: ContextSerializer,
        WithQuizContext: WithContextSerializer,
        WithoutQuizContext: WithoutContextSerializer,
    }

class QuizSerializer(serializers.ModelSerializer):
    blocks = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = '__all__'
    
    def get_blocks(self, obj):
        blocks = []

        for context in obj.contexts.all():
            context_data = QuizContextSerializer(context).data
            questions = QuestionPolymorphicSerializer(context.questions.all(), many=True).data

            if context_data['resourcetype'] is 'WithoutQuizContext':
                blocks.append({'context': None, 'questions': questions})
            else:
                del context_data['resourcetype']
                blocks.append({'context': context_data, 'questions': questions})

        return blocks

class MCQAnswerSerializer(serializers.Serializer):
    question_type = serializers.CharField(default='mcq')
    question_id = serializers.IntegerField()
    selected_choice = serializers.IntegerField()

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