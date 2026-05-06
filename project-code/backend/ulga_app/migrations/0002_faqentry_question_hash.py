import hashlib

from django.db import migrations, models


def populate_question_hash(apps, schema_editor):
    FAQEntry = apps.get_model("ulga_app", "FAQEntry")
    for faq in FAQEntry.objects.all().only("id", "question"):
        faq.question_hash = hashlib.sha256(faq.question.strip().encode("utf-8")).hexdigest()
        faq.save(update_fields=["question_hash"])


class Migration(migrations.Migration):

    dependencies = [
        ("ulga_app", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="faqentry",
            name="question",
            field=models.TextField(),
        ),
        migrations.AddField(
            model_name="faqentry",
            name="question_hash",
            field=models.CharField(editable=False, max_length=64, null=True),
        ),
        migrations.RunPython(populate_question_hash, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="faqentry",
            name="question_hash",
            field=models.CharField(editable=False, max_length=64, unique=True),
        ),
    ]