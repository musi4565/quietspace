from django.urls import path

from apps.ai.views import AIStatusView, ChatView

urlpatterns = [
    path("chat/", ChatView.as_view(), name="ai-chat"),
    path("status/", AIStatusView.as_view(), name="ai-status"),
]