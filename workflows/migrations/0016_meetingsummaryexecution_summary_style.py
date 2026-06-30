from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("workflows", "0015_meetingsummaryexecution"),
    ]

    operations = [
        migrations.AddField(
            model_name="meetingsummaryexecution",
            name="summary_style",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
