# Generated by Django 4.2.4 on 2023-09-05 23:55

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("mangoAPP", "0014_remove_empleados_user_empleados_id_vivero"),
    ]

    operations = [
        migrations.RenameField(
            model_name="empleados",
            old_name="usuario",
            new_name="username",
        ),
    ]