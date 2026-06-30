from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("workflows", "0017_alter_resumeexecution_file_name_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="resumeexecution",
            name="job_description",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="resumeexecution",
            name="job_title",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
