# Generated by Django 4.2.4 on 2023-09-02 20:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("mangoAPP", "0006_rename_is_admin_userprofile_useradmin"),
    ]

    operations = [
        migrations.CreateModel(
            name="Propietario",
            fields=[
                ("Id_propietario", models.AutoField(primary_key=True, serialize=False)),
                ("nombre", models.CharField(max_length=100)),
                ("telefono", models.CharField(max_length=15)),
                ("correo", models.EmailField(max_length=254)),
                ("ubicacion", models.CharField(max_length=255)),
            ],
        ),
        migrations.RemoveField(
            model_name="planta",
            name="fase",
        ),
        migrations.RemoveField(
            model_name="planta",
            name="id",
        ),
        migrations.RemoveField(
            model_name="planta",
            name="imagen_base64",
        ),
        migrations.AddField(
            model_name="planta",
            name="Id_planta",
            field=models.AutoField(default=1, primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="userprofile",
            name="Id_movil",
            field=models.CharField(default=1, max_length=35),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="userprofile",
            name="ip_registro",
            field=models.CharField(default=1, max_length=35),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="planta",
            name="informacion_general",
            field=models.TextField(max_length=500),
        ),
        migrations.CreateModel(
            name="Viveros",
            fields=[
                ("Id_vivero", models.AutoField(primary_key=True, serialize=False)),
                ("nombre", models.CharField(max_length=255)),
                ("telefono", models.CharField(max_length=15)),
                ("correo", models.EmailField(max_length=254)),
                ("ubicacion", models.CharField(max_length=255)),
                (
                    "Id_propietario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="mangoAPP.propietario",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Tratamientos",
            fields=[
                ("Id_tratamiento", models.AutoField(primary_key=True, serialize=False)),
                ("producto_quimico", models.CharField(max_length=100)),
                ("producto_quimico_image", models.TextField()),
                ("descripcion_tratamiento", models.CharField(max_length=500)),
                (
                    "Id_enfermedad",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="mangoAPP.planta",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="enfermedad",
            fields=[
                ("Id_enfermedad", models.AutoField(primary_key=True, serialize=False)),
                ("nombre", models.CharField(max_length=100)),
                ("fase", models.CharField(max_length=100)),
                ("fase_image", models.TextField(default="")),
                ("informacion_general", models.CharField(max_length=500)),
                (
                    "Id_planta",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="mangoAPP.planta",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Empleados",
            fields=[
                ("Id_empleados", models.AutoField(primary_key=True, serialize=False)),
                ("nombres", models.CharField(max_length=200)),
                ("telefono", models.CharField(max_length=15)),
                ("correo", models.EmailField(max_length=254)),
                ("direccion", models.CharField(max_length=255)),
                ("cargo", models.CharField(max_length=100)),
                (
                    "Id_usuario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="mangoAPP.userprofile",
                    ),
                ),
                (
                    "Id_vivero",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="mangoAPP.viveros",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="planta",
            name="Id_vivero",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="mangoAPP.viveros",
            ),
            preserve_default=False,
        ),
    ]