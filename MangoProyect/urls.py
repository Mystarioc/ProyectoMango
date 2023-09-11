"""
URL configuration for MangoProyect project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from mangoAPP import views

urlpatterns = [
    path("admin/", admin.site.urls),
    ### Usuarios ###
    path("login/", views.LoginUser, name="login"),
    path("register/", views.register_user, name="register"),
    path("Prediccted/", views.Prediccted, name="Prediccted"),
    path("base64/", views.imageBase64, name="base64"),
    path("UpdateImageProfile/", views.update_profile_image, name="UpdateImageProfile"),
    path("UpdateProfile/", views.update_profile_data, name="UpdateProfile"),
    path("getUserById/", views.get_user_by_id, name="getUserById"),
    path("get_users/", views.get_users, name="get_users"),
    path("delete_all_users/", views.delete_all_users, name="delete_all_users"),
    
    ### vivieros ###
    path("reg_vive/", views.crear_vivero, name="reg_vive"),
    path("get_viveByID/", views.consultar_vivero_por_id, name="get_viveByID"),
    path("get_all_vive/", views.consultar_viveros, name="get_all_vive"),
    path("del_vive/", views.eliminar_vivero, name="del_vive"),
    path("del_vive_all/", views.eliminar_todos_viveros, name="del_vive_all"),
    path("get_vive_by_propi/", views.consultar_viveros_por_usuario, name="get_vive_by_propi"),


    ### Empleados ###
    path("reg_emple/", views.crear_empleado, name="reg_emple"),
    path("update_empleByID/", views.actualizar_empleado, name="update_empleByID"),
    path("get_empleByID/", views.consultar_empleado_por_id, name="get_empleByID"),
    path("get_all_emple/", views.consultar_empleados, name="get_all_emple"),
    path("del_emple/", views.eliminar_empleado_id, name="del_emple"),
    path("get_empleados_idVivero/", views.consultar_empleados_por_vivero, name="get_empleados_idVivero"),
    path("login_empleado/", views.LoginEmpleado, name="login_empleado"),


    ### Plantas ###
    path("reg_planta/", views.crear_planta, name="reg_planta"),
    path("get_plantaByID/", views.consultar_planta_por_id, name="get_plantaByID"),
    path("update_planta/", views.actualizar_planta, name="update_planta"),
    path("del_planta/", views.eliminar_planta, name="del_planta"),
    path("get_planta_idVivero/", views.consultar_plantas_por_vivero, name="get_planta_idVivero"),
    path("get_all_plantas/", views.obtener_todas_las_plantas, name="get_all_plantas"),

    ### Enfermedad ###
    path("reg_enfer/", views.crear_enfermedad, name="reg_enfer"),
    path("del_enfer/", views.eliminar_enfermedad_por_id, name="del_enfer"),
    path("get_enferByID/", views.consultar_enfermedad_por_id, name="get_enferByID"),
    path("update_enfer/", views.actualizar_enfermedad, name="update_enfer"),
    path("get_all_enfer/", views.obtener_todas_enfermedades, name="get_all_enfer"),
    #path("get_enfer_idPlanta/", views.consultar_enfermedades_por_planta, name="get_enfer_idPlanta"),

    ### tratamiento ###
    path("reg_trata/", views.crear_tratamiento, name="reg_trata"),
    path("del_trata/", views.eliminar_tratamiento, name="del_trata"),
    path("get_trataByID/", views.consultar_tratamiento_por_id, name="get_trataByID"),
    path("update_trata/", views.actualizar_tratamiento_por_id, name="update_trata"),
    path("get_all_trata/", views.obtener_todos_los_tratamientos, name="get_all_trata"),
   
]

