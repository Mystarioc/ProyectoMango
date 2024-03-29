# Generated by Django 4.2.4 on 2023-08-31 21:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("mangoAPP", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Planta",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre", models.CharField(max_length=100)),
                ("fase", models.CharField(max_length=50)),
                ("imagen_blob", models.BinaryField()),
                ("informacion_general", models.TextField()),
            ],
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="profile_image",
            field=models.ImageField(blank=True, null=True, upload_to="profile_images/"),
        ),
    ]
