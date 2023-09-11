from django.db import models
from django.contrib.auth.models import User

##### Usuario #####
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.TextField(default='')
    email = models.EmailField()
    userAdmin = models.BooleanField(default=False)
    Id_movil = models.CharField(max_length=35)  # Campo para ID_movil como clave foránea
    ip_registro = models.CharField(max_length=35)

    def __str__(self):
        return self.user.username

#####  Viveros #####
class Viveros(models.Model):
    Id_vivero = models.AutoField(primary_key=True)  # Clave primaria autogenerada
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)  # Campo para ID_movil como clave foránea
    nombre = models.CharField(max_length=255)    
    telefono = models.CharField(max_length=15)
    correo = models.EmailField()
    ubicacion = models.CharField(max_length=255)
    def __str__(self):
        return self.nombre

class Empleados(models.Model):
    Id_empleados = models.AutoField(primary_key=True)
    Id_vivero = models.ForeignKey('Viveros', on_delete=models.CASCADE)
    nombres = models.CharField(max_length=255)
    username_emple = models.CharField(max_length=255,unique=True) 
    contraseña = models.CharField(max_length=50)
    telefono = models.CharField(max_length=15)
    correo = models.EmailField()
    direccion = models.CharField(max_length=255)
    cargo = models.CharField(max_length=100)

    def __str__(self):
        return self.nombres
    
#####  Planta #####
class Planta(models.Model):
    Id_planta = models.AutoField(primary_key=True)  # Clave primaria autogenerada
    Id_vivero = models.ForeignKey('Viveros', on_delete=models.CASCADE)  # Campo para ID_movil como clave foránea    
    nombre = models.CharField(max_length=100)
    informacion_general = models.TextField(max_length=500)
    def __str__(self):
        return self.nombre
    
#####  enfermedad #####
class enfermedad(models.Model):
    Id_enfermedad = models.AutoField(primary_key=True)
    Id_planta = models.ForeignKey('Planta', on_delete=models.CASCADE)  # Campo para ID_movil como clave foránea    
    nombre = models.CharField(max_length=100)
    fase = models.CharField(max_length=100)
    fase_image = models.TextField(default='')
    informacion_general = models.CharField(max_length=500)
    def __str__(self):
        return self.nombre
    
#####  tratamiento #####
class Tratamientos(models.Model):
    Id_tratamiento = models.AutoField(primary_key=True)
    Id_enfermedad = models.ForeignKey('enfermedad', on_delete=models.CASCADE)  # Campo para ID_movil como clave foránea    
    producto_quimico=models.CharField(max_length=100)
    producto_quimico_image= models.TextField()
    descripcion_tratamiento = models.CharField(max_length=500)

    def __str__(self):
        return self.producto_quimico