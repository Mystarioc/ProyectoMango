# Generated by Django 4.2.4 on 2023-09-05 23:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("mangoAPP", "0011_remove_viveros_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="viveros",
            name="user",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="mangoAPP.userprofile",
            ),
            preserve_default=False,
        ),
    ]
