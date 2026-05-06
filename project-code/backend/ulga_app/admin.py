from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import AccessLog, AuditLog, ByLawDocument, DocumentChunk, FAQEntry, Feedback, QuestionThread, User


@admin.register(User)
class ULGAUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Role", {"fields": ("role",)}),)


admin.site.register(ByLawDocument)
admin.site.register(DocumentChunk)
admin.site.register(QuestionThread)
admin.site.register(Feedback)
admin.site.register(FAQEntry)
admin.site.register(AuditLog)
admin.site.register(AccessLog)
