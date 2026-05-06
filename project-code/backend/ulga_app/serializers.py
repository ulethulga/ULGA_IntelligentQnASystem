from rest_framework import serializers

from .models import ByLawDocument, FAQEntry, Feedback, QuestionThread


class AskQuestionSerializer(serializers.Serializer):
    question = serializers.CharField()
    parent_id = serializers.IntegerField(required=False)


class FeedbackSerializer(serializers.Serializer):
    thread_id = serializers.IntegerField()
    helpful = serializers.BooleanField()
    comments = serializers.CharField(required=False, allow_blank=True)


class UploadDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ByLawDocument
        fields = ["id", "title", "file", "version", "changelog", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class DocumentVersionSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.CharField(source="uploaded_by.username", default="")

    class Meta:
        model = ByLawDocument
        fields = ["id", "title", "version", "changelog", "is_active", "uploaded_by", "created_at"]


class QuestionThreadSerializer(serializers.ModelSerializer):
    final_answer = serializers.SerializerMethodField()

    class Meta:
        model = QuestionThread
        fields = ["id", "parent", "question", "answer", "overridden_answer", "final_answer", "sources", "created_at"]

    def get_final_answer(self, obj: QuestionThread) -> str:
        return obj.overridden_answer or obj.answer


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQEntry
        fields = ["id", "question", "answer", "frequency", "updated_at"]
