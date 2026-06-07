from django.urls import path

from .views import QuizSubmitCreateView


urlpatterns = [
    path('<int:quiz_id>/submit/', QuizSubmitCreateView.as_view()),
]