import hashlib

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        MEMBER = "member", "Member"
        EXECUTIVE = "executive", "ULGA Executive Team"
        ADMIN = "admin", "System Administrator"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)


class ByLawDocument(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="bylaws/")
    version = models.CharField(max_length=32)
    changelog = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="uploaded_docs")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class DocumentChunk(models.Model):
    document = models.ForeignKey(ByLawDocument, on_delete=models.CASCADE, related_name="chunks")
    chunk_id = models.CharField(max_length=128)
    section = models.CharField(max_length=120, blank=True)
    page = models.IntegerField(default=0)
    content = models.TextField()


class QuestionThread(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="threads")
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="follow_ups")
    question = models.TextField()
    answer = models.TextField()
    overridden_answer = models.TextField(blank=True)
    sources = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Feedback(models.Model):
    thread = models.OneToOneField(QuestionThread, on_delete=models.CASCADE, related_name="feedback")
    helpful = models.BooleanField()
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class FAQEntry(models.Model):
    question = models.TextField()
    question_hash = models.CharField(max_length=64, unique=True, editable=False)
    answer = models.TextField()
    frequency = models.PositiveIntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def hash_question(question: str) -> str:
        return hashlib.sha256(question.strip().encode("utf-8")).hexdigest()

    def save(self, *args, **kwargs):
        self.question_hash = self.hash_question(self.question)
        update_fields = kwargs.get("update_fields")
        if update_fields is not None:
            kwargs["update_fields"] = list(set(update_fields) | {"question_hash"})
        super().save(*args, **kwargs)


class AuditLog(models.Model):
    actor = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=120)
    details = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)


class AccessLog(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=12)
    status_code = models.IntegerField()
    ip_address = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
