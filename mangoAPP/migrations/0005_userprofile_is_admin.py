# Generated by Django 4.2.4 on 2023-09-01 01:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("mangoAPP", "0004_alter_userprofile_profile_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="is_admin",
            field=models.BooleanField(default=False),
        ),
    ]
