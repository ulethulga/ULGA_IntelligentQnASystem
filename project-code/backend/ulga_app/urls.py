from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    AnalyticsView,
    AskQuestionView,
    DocumentVersionsView,
    FAQView,
    LoginView,
    RegisterView,
    OverrideAnswerView,
    QuestionHistoryView,
    RebuildIndexView,
    SubmitFeedbackView,
    UploadDocumentView,
)

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("questions/ask/", AskQuestionView.as_view(), name="ask_question"),
    path("questions/history/", QuestionHistoryView.as_view(), name="question_history"),
    path("questions/feedback/", SubmitFeedbackView.as_view(), name="submit_feedback"),
    path("documents/upload/", UploadDocumentView.as_view(), name="upload_document"),
    path("documents/versions/", DocumentVersionsView.as_view(), name="document_versions"),
    path("documents/rebuild-index/", RebuildIndexView.as_view(), name="rebuild_index"),
    path("faq/", FAQView.as_view(), name="faq"),
    path("admin/analytics/", AnalyticsView.as_view(), name="analytics"),
    path("admin/override-answer/<int:thread_id>/", OverrideAnswerView.as_view(), name="override_answer"),
]
