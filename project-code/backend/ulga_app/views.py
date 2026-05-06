from collections import Counter

from django.db.models import Count
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .auth_serializers import CustomTokenObtainPairSerializer, RegisterSerializer
from .models import AuditLog, ByLawDocument, DocumentChunk, FAQEntry, Feedback, QuestionThread
from .permissions import IsAdmin, IsExecutiveOrAdmin
from .serializers import (
    AskQuestionSerializer,
    DocumentVersionSerializer,
    FAQSerializer,
    FeedbackSerializer,
    QuestionThreadSerializer,
    UploadDocumentSerializer,
)
from .services.rag_service import RAGService


BLOCKED_TERMS = ["harass", "abuse", "password", "ssn", "credit card"]


class LoginView(TokenObtainPairView):
    permission_classes = []
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "detail": "Signup successful.",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "username": user.username,
                "role": user.role,
            },
            status=status.HTTP_201_CREATED,
        )


class AskQuestionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AskQuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question = serializer.validated_data["question"].strip()
        parent_id = serializer.validated_data.get("parent_id")

        if len(question) < 5:
            return Response({"detail": "Question is too short."}, status=status.HTTP_400_BAD_REQUEST)

        lowered = question.lower()
        if any(term in lowered for term in BLOCKED_TERMS):
            return Response({"detail": "Question contains restricted content."}, status=status.HTTP_400_BAD_REQUEST)

        rag = RAGService()
        contexts = rag.retrieve(question, k=4)
        if not contexts:
            answer = "Insufficient by-law context found to answer confidently."
            sources = []
        else:
            answer = rag.answer(question, contexts)
            sources = [
                {
                    "text": c.page_content[:600],
                    "section": c.metadata.get("section", ""),
                    "page": c.metadata.get("page", 0),
                    "source": c.metadata.get("source", ""),
                }
                for c in contexts
            ]

        parent = None
        if parent_id:
            parent = QuestionThread.objects.filter(id=parent_id, user=request.user).first()

        thread = QuestionThread.objects.create(
            user=request.user,
            parent=parent,
            question=question,
            answer=answer,
            sources=sources,
        )

        faq, created = FAQEntry.objects.get_or_create(
            question_hash=FAQEntry.hash_question(question),
            defaults={"question": question, "answer": answer, "frequency": 1},
        )
        if not created:
            faq.question = question
            faq.frequency += 1
            faq.answer = answer
            faq.save(update_fields=["question", "frequency", "answer", "updated_at"])

        return Response(QuestionThreadSerializer(thread).data)


class QuestionHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rows = QuestionThread.objects.filter(user=request.user)
        return Response(QuestionThreadSerializer(rows, many=True).data)


class SubmitFeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        thread = QuestionThread.objects.filter(id=serializer.validated_data["thread_id"], user=request.user).first()
        if not thread:
            return Response({"detail": "Question thread not found."}, status=status.HTTP_404_NOT_FOUND)

        feedback, _ = Feedback.objects.update_or_create(
            thread=thread,
            defaults={
                "helpful": serializer.validated_data["helpful"],
                "comments": serializer.validated_data.get("comments", ""),
            },
        )
        return Response({"id": feedback.id, "detail": "Feedback submitted."})


class UploadDocumentView(APIView):
    permission_classes = [IsExecutiveOrAdmin]
    parser_classes = [MultiPartParser]

    def post(self, request):
        serializer = UploadDocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document = serializer.save(uploaded_by=request.user)

        rag = RAGService()
        loaded = rag.load_document(document.file.path)
        chunked = rag.chunk_documents(loaded)

        for idx, chunk in enumerate(chunked):
            metadata = chunk.metadata or {}
            DocumentChunk.objects.create(
                document=document,
                chunk_id=f"{document.id}-{idx}",
                section=str(metadata.get("section", "")),
                page=int(metadata.get("page", 0) or 0),
                content=chunk.page_content,
            )

        rag.append_documents_to_index(chunked)
        AuditLog.objects.create(actor=request.user, action="upload_document", details={"document_id": document.id})
        return Response(UploadDocumentSerializer(document).data, status=status.HTTP_201_CREATED)


class DocumentVersionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        docs = ByLawDocument.objects.all()
        return Response(DocumentVersionSerializer(docs, many=True).data)


class RebuildIndexView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        chunks = DocumentChunk.objects.filter(document__is_active=True)
        if not chunks.exists():
            return Response({"detail": "No active chunks found."}, status=status.HTTP_400_BAD_REQUEST)

        docs = []
        for item in chunks:
            docs.append(
                {
                    "page_content": item.content,
                    "metadata": {
                        "section": item.section,
                        "page": item.page,
                        "source": item.document.file.name,
                    },
                }
            )

        from langchain_core.documents import Document

        rag_docs = [Document(page_content=d["page_content"], metadata=d["metadata"]) for d in docs]
        rag = RAGService()
        chunked_docs = rag.chunk_documents(rag_docs)
        rag.rebuild_index_from_documents(chunked_docs)
        AuditLog.objects.create(
            actor=request.user,
            action="rebuild_index",
            details={"source_chunk_count": len(rag_docs), "embedded_chunk_count": len(chunked_docs)},
        )
        return Response(
            {
                "detail": "Index rebuilt successfully.",
                "source_chunk_count": len(rag_docs),
                "embedded_chunk_count": len(chunked_docs),
            }
        )


class FAQView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rows = FAQEntry.objects.order_by("-frequency", "-updated_at")[:50]
        return Response(FAQSerializer(rows, many=True).data)


class AnalyticsView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        total_questions = QuestionThread.objects.count()
        helpful = Feedback.objects.filter(helpful=True).count()
        not_helpful = Feedback.objects.filter(helpful=False).count()

        topic_keywords = {
            "membership": ["member", "membership", "dues"],
            "finance": ["finance", "budget", "fund", "money"],
            "elections": ["election", "vote", "nomination"],
        }
        questions = [q.question.lower() for q in QuestionThread.objects.all()]
        topic_distribution = Counter()
        for q in questions:
            matched = False
            for topic, words in topic_keywords.items():
                if any(word in q for word in words):
                    topic_distribution[topic] += 1
                    matched = True
                    break
            if not matched:
                topic_distribution["other"] += 1

        daily_usage = list(
            QuestionThread.objects.extra({"day": "date(created_at)"})
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )

        return Response(
            {
                "number_of_questions": total_questions,
                "topic_distribution": dict(topic_distribution),
                "accuracy_feedback": {"helpful": helpful, "not_helpful": not_helpful},
                "usage_over_time": daily_usage,
            }
        )


class OverrideAnswerView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, thread_id: int):
        new_answer = request.data.get("answer", "").strip()
        if not new_answer:
            return Response({"detail": "Answer is required."}, status=status.HTTP_400_BAD_REQUEST)

        thread = QuestionThread.objects.filter(id=thread_id).first()
        if not thread:
            return Response({"detail": "Thread not found."}, status=status.HTTP_404_NOT_FOUND)

        thread.overridden_answer = new_answer
        thread.save(update_fields=["overridden_answer"])
        AuditLog.objects.create(actor=request.user, action="override_answer", details={"thread_id": thread.id})
        return Response({"detail": "Answer override saved."})
