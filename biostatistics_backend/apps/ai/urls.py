from django.urls import path
from .views import AIChatView

urlpatterns = [
    path("chat/", AIChatView.as_view(), name="ai-chat"),
]


# cd /Users/yesserkeydana/Desktop/bio-statistic-ai/biostatistics_backend

# source venv/bin/activate

# python manage.py runserver http://127.0.0.1:8000/

# cd /Users/yesserkeydana/Desktop/bio-statistic-ai/biostatistics_frontend

# npm run dev
# http://localhost:5173 