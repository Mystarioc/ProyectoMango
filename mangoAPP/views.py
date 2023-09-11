from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from keras.models import load_model
import base64
from django.core.exceptions import ValidationError 
from django.core.validators  import validate_email
from .models import UserProfile,Planta ,Tratamientos,Viveros,enfermedad ,Empleados,Registros_enfermedad
import json
from PIL import Image
import numpy as np

# Create your views here.


@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        first_name = request.POST.get("first_name")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        id_movil = request.POST.get("id_movil")  # Agregar campo Id_movil desde la solicitud
        ip_registro = request.META.get("REMOTE_ADDR")  # Obtener la dirección IP del cliente

        if password1 == password2:
            email = request.POST.get("email")

            # Verificar si el email ya existe en la base de datos
            if User.objects.filter(email=email).exists():
                data = {
                    'message': 'Ya existe un usuario con este email',
                    'status': 'error'
                }
                return JsonResponse(data)

            try:
                user = User.objects.create_user(
                    request.POST.get("username"),
                    email,
                    password=password1,
                    first_name=first_name
                )

                try:
                    validate_email(email)  # Valida el formato del correo electrónico
                except ValidationError:
                    user.delete()  # Si el formato no es válido, elimina el usuario
                    data = {
                        'message': 'Formato de correo electrónico inválido',
                        'status': 'error'
                    }
                    return JsonResponse(data, status=400)

                # Crear un perfil de usuario y asociar los campos Id_movil e ip_registro
                profile = UserProfile.objects.get_or_create(user=user)[0]
                profile.profile_image = base64.b64encode(request.FILES.get("profile_image").read()).decode('utf-8') if request.FILES.get("profile_image") else ''
                profile.email = email
                profile.Id_movil = id_movil
                profile.ip_registro = ip_registro
                profile.save()

                data = {
                    'message': 'Usuario creado con éxito',
                    'status': 'success',
                }
                return JsonResponse(data)
            except IntegrityError:
                data = {
                    'message': 'Nombre de usuario ya existe',
                    'status': 'error'
                }
                return JsonResponse(data)

        data = {
            'message': 'Contraseñas no coinciden',
            'status': 'error'
        }
        return JsonResponse(data)

    data = {
        'message': 'Método no permitido',
        'status': 'error'
    }
    return JsonResponse(data)

@csrf_exempt
def LoginUser(request):
    if request.method == 'POST':
        post_data = json.loads(request.body)
        username = post_data.get("username")
        password = post_data.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            try:
                # Suponiendo que UserProfile esté relacionado con el modelo de usuario predeterminado de Django
                user_profile = UserProfile.objects.get(user=user)
                user_admin = user_profile.userAdmin
            except UserProfile.DoesNotExist:
                user_admin = False

            data = {
                'message': 'Inicio de sesión exitoso',
                'status': 'success',
                'user_id': user.id,
                'user_admin': user_admin  # Aquí se obtiene el valor de userAdmin
            }
            return JsonResponse(data)
        else:
            data = {
                'message': 'Credenciales inválidas',
                'status': 'error'
            }
            return JsonResponse(data)

    data = {
        'message': 'Método no permitido',
        'status': 'error'
    }
    return JsonResponse(data)
            
@csrf_exempt
def imageBase64(request):
    if request.method == 'POST':
        image_file = request.FILES.get('image')

        if image_file:
            image_data = image_file.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            return JsonResponse({'base64_image': base64_image})
        else:
            return JsonResponse({'error': 'No se proporcionó ninguna imagen'}, status=400)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def update_profile_image(request):
    if request.method == 'POST':
        user_identifier = request.POST.get("user_id")  # Obtener el ID o el nombre del usuario
        profile_image = request.FILES.get("profile_image")  # Obtener archivo adjunto

        try:
            user = User.objects.get(pk=user_identifier)  # Buscar por ID
        except User.DoesNotExist:
            try:
                user = User.objects.get(username=user_identifier)  # Buscar por nombre
            except User.DoesNotExist:
                data = {
                    'message': 'Usuario no encontrado',
                    'status': 'error'
                }
                return JsonResponse(data, status=404)

        if profile_image:
            try:
                profile = UserProfile.objects.get(user=user)
            except UserProfile.DoesNotExist:
                profile = UserProfile.objects.create(user=user)

            # Leer y convertir la imagen en formato Base64
            image_base64 = base64.b64encode(profile_image.read()).decode('utf-8')

            profile.profile_image = image_base64
            profile.save()

            data = {
                'message': 'Foto de perfil actualizada con éxito',
                'status': 'success'
            }
            return JsonResponse(data)

        data = {
            'message': 'No se proporcionó una nueva foto de perfil',
            'status': 'error'
        }
        return JsonResponse(data, status=400)

    data = {
        'message': 'Método no permitido',
        'status': 'error'
    }
    return JsonResponse(data, status=405)

@csrf_exempt
def update_profile_data(request):
    if request.method == 'PUT':
        json_data = json.loads(request.body)
        user_id = json_data.get("id")
        
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            data = {
                'message': 'Usuario no encontrado',
                'status': 'error'
            }
            return JsonResponse(data)
        new_first_name = json_data.get("first_name")
        new_name = json_data.get("name")
        new_email = json_data.get("email")

        # Verificar si otro usuario ya tiene el mismo correo electrónico
        if User.objects.filter(email=new_email).exclude(pk=user_id).exists():
            data = {
                'message': 'Otro usuario ya tiene este correo electrónico',
                'status': 'error'
            }
            return JsonResponse(data, status=400)

        try:
            validate_email(new_email)
        except ValidationError:
            data = {
                'message': 'Formato de correo electrónico inválido',
                'status': 'error'
            }
            return JsonResponse(data, status=400)
        user.first_name= new_first_name
        user.username = new_name
        user.email = new_email
        user.save()

        data = {
            'message': 'Perfil de usuario actualizado con éxito',
            'status': 'success'
        }
        return JsonResponse(data)

    data = {
        'message': 'Método no permitido',
        'status': 'error'
    }
    return JsonResponse(data)

@csrf_exempt
def get_users(request):
    if request.method == 'GET':
        users = User.objects.all()
        
        user_list = []
        for user in users:
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name
                
            }
            user_list.append(user_data)

        data = {
            'users': user_list,
            'status': 'success'
        }
        return JsonResponse(data)

    data = {
        'message': 'Método no permitido',
        'status': 'error'
    }
    return JsonResponse(data, status=405)

@csrf_exempt
def get_user_by_id(request):
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body)
            user_id = json_data.get("id")
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            data = {
                'message': 'Usuario no encontrado',
                'status': 'error'
            }
            return JsonResponse(data)

        try:
            profile = UserProfile.objects.get(user=user)
            if profile.profile_image:
                profile_image_base64 = profile.profile_image
            else:
                profile_image_base64 = None
            ip_registro = profile.ip_registro  # Obtener la dirección IP desde el perfil
            id_movil = profile.Id_movil  # Obtener el ID del dispositivo móvil desde el perfil
        except UserProfile.DoesNotExist:
            profile_image_base64 = None
            ip_registro = None
            id_movil = None

        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'is_admin': profile.userAdmin,
            'profile_image': profile_image_base64,
            'ip_registro': ip_registro,  # Agregar la dirección IP al JSON de respuesta
            'id_movil': id_movil,  # Agregar el ID del dispositivo móvil al JSON de respuesta
        }

        return JsonResponse(user_data)

    data = {
        'message': 'Método no permitido',
        'status': 'error'
    }
    return JsonResponse(data)

@csrf_exempt
def delete_all_users(request):
    if request.method == 'DELETE':
        try:
            # Eliminar todos los usuarios del modelo UserProfile
            UserProfile.objects.all().delete()

            data = {
                'message': 'Todos los usuarios han sido eliminados con éxito',
                'status': 'success',
            }
            return JsonResponse(data)
        except Exception as e:
            data = {
                'message': 'Error al eliminar todos los usuarios',
                'status': 'error',
                'error_message': str(e)
            }
            return JsonResponse(data, status=500)

    data = {
        'message': 'Método no permitido',
        'status': 'error'
    }
    return JsonResponse(data, status=405)


################################################################################
############################## Viveros #########################################
################################################################################
@csrf_exempt
def crear_vivero(request):
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body)
            nombre = json_data.get("nombre")
            telefono = json_data.get("telefono")
            correo = json_data.get("correo")
            ubicacion = json_data.get("ubicacion")
            id_usuario = json_data.get("id_usuario")

            # Verificar si el usuario existe (asumiendo que UserProfile está relacionado con User)
            try:
                usuario = UserProfile.objects.get(pk=id_usuario)
            except UserProfile.DoesNotExist:
                data = {
                    'message': 'Usuario no encontrado',
                    'status': 'error'
                }
                return JsonResponse(data, status=404)

            # Crear un nuevo vivero en la base de datos
            vivero = Viveros.objects.create(
                nombre=nombre,
                telefono=telefono,
                correo=correo,
                ubicacion=ubicacion,
                user=usuario  # Asigna la instancia de UserProfile (usuario) al campo 'user'
            )

            data = {
                'message': 'Vivero registrado con éxito',
                'status': 'success',
                'vivero_id': vivero.Id_vivero
            }
            return JsonResponse(data)
        except Exception as e:
            data = {
                'message': 'Error al registrar el vivero',
                'status': 'error',
                'error_message': str(e)
            }
            return JsonResponse(data, status=400)

    data = {
        'message': 'Método no permitido',
        'status': 'error'
    }
    return JsonResponse(data, status=405)

@csrf_exempt
def eliminar_vivero(request):
    if request.method == 'DELETE':
        try:
            json_data = json.loads(request.body)
            vivero_id = json_data.get("id")

            # Intentar eliminar el vivero por su ID
            vivero = Viveros.objects.get(pk=vivero_id)
            vivero.delete()

            data = {
                'message': 'Vivero eliminado con éxito',
                'status': 'success',
            }
            return JsonResponse(data)
        except Viveros.DoesNotExist:
            data = {
                'message': 'Vivero no encontrado',
                'status': 'error'
            }
            return JsonResponse(data, status=404)
        except Exception as e:
            data = {
                'message': 'Error al eliminar el vivero',
                'status': 'error',
                'error_message': str(e)
            }
            return JsonResponse(data, status=500)

    data = {
        'message': 'Método no permitido',
        'status': 'error'
    }
    return JsonResponse(data, status=405)

@csrf_exempt
def consultar_viveros(request):
    if request.method == 'GET':
        try:
            # Consultar todos los viveros en la base de datos
            viveros = Viveros.objects.all()

            # Crear una lista de viveros en formato JSON
            viveros_list = []
            for vivero in viveros:
                vivero_data = {
                    'id': vivero.Id_vivero,
                    'nombre': vivero.nombre,
                    'telefono': vivero.telefono,
                    'correo': vivero.correo,
                    'ubicacion': vivero.ubicacion,
                    'user_id': vivero.user.user.id,  # Acceder al ID del propietario
                }
                viveros_list.append(vivero_data)

            data = {
                'message': 'Viveros consultados con éxito',
                'status': 'success',
                'viveros': viveros_list
            }
            return JsonResponse(data)
        except Exception as e:
            data = {
                'message': 'Error al consultar los viveros',
                'status': 'error',
                'error_message': str(e)
            }
            return JsonResponse(data, status=500)

    data = {
        'message': 'Método no permitido',
        'status': 'error'
    }
    return JsonResponse(data, status=405)

@csrf_exempt
def consultar_vivero_por_id(request):
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body)
            vivero_id = json_data.get("id")

            # Consultar el vivero por su ID
            try:
                vivero = Viveros.objects.get(pk=vivero_id)

                # Obtener el ID del propietario del vivero a través del campo 'user' en lugar de 'Id_propietario'
                usuario_id = vivero.user.user.id

                # Crear un JSON con los datos del vivero y el ID del propietario
                vivero_data = {
                    'id': vivero.Id_vivero,
                    'nombre': vivero.nombre,
                    'telefono': vivero.telefono,
                    'correo': vivero.correo,
                    'ubicacion': vivero.ubicacion,
                    'usuario_id': usuario_id,
                }

                data = {
                    'message': 'Vivero consultado con éxito',
                    'status': 'success',
                    'vivero': vivero_data
                }
                return JsonResponse(data)
            except Viveros.DoesNotExist:
                data = {
                    'message': 'Vivero no encontrado',
                    'status': 'error'
                }
                return JsonResponse(data, status=404)

        except Exception as e:
            data = {
                'message': 'Error al consultar el vivero',
                'status': 'error',
                'error_message': str(e)
            }
            return JsonResponse(data, status=500)

    data = {
        'message': 'Método no permitido',
        'status': 'error'
    }
    return JsonResponse(data, status=405)

@csrf_exempt
def eliminar_todos_viveros(request):
    if request.method == 'DELETE':
        try:
            # Eliminar todos los viveros de la base de datos
            Viveros.objects.all().delete()

            data = {
                'message': 'Todos los viveros han sido eliminados con éxito',
                'status': 'success',
            }
            return JsonResponse(data)
        except Exception as e:
            data = {
                'message': 'Error al eliminar todos los viveros',
                'status': 'error',
                'error_message': str(e)
            }
            return JsonResponse(data, status=500)

    data = {
        'message': 'Método no permitido',
        'status': 'error'
    }
    return JsonResponse(data, status=405)

@csrf_exempt
def consultar_viveros_por_usuario(request):
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body)
            user_id = json_data.get("user_id")  # Cambiamos la clave a 'user_id'

            # Verificar si el usuario existe (asumiendo que UserProfile está relacionado con User)
            try:
                usuario = UserProfile.objects.get(pk=user_id)
            except UserProfile.DoesNotExist:
                data = {
                    'message': 'Usuario no encontrado',
                    'status': 'error'
                }
                return JsonResponse(data, status=404)

            # Consultar todos los viveros asociados al usuario (propietario)
            viveros = Viveros.objects.filter(user=usuario)  # Usamos el campo 'user' en lugar de 'Id_propietario'

            # Crear una lista de viveros en formato JSON
            viveros_list = []
            for vivero in viveros:
                vivero_data = {
                    'id': vivero.Id_vivero,
                    'nombre': vivero.nombre,
                    'telefono': vivero.telefono,
                    'correo': vivero.correo,
                    'ubicacion': vivero.ubicacion,
                }
                viveros_list.append(vivero_data)

            data = {
                'message': 'Viveros consultados por propietario con éxito',
                'status': 'success',
                'viveros': viveros_list
            }
            return JsonResponse(data)
        except Exception as e:
            data = {
                'message': 'Error al consultar los viveros por propietario',
                'status': 'error',
                'error_message': str(e)
            }
            return JsonResponse(data, status=500)

    data = {
        'message': 'Método no permitido',
        'status': 'error'
    }
    return JsonResponse(data, status=405)


################################################################################
############################ Empleados #########################################
################################################################################

@csrf_exempt
def crear_empleado(request):
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body)
            id_vivero = json_data.get("id_vivero")
            nombres = json_data.get("nombres")
            username_emple = json_data.get("username_emple")
            contraseña = json_data.get("contraseña")
            telefono = json_data.get("telefono")
            correo = json_data.get("correo")
            direccion = json_data.get("direccion")
            cargo = json_data.get("cargo")

            # Verificar si el vivero existe
            try:
                vivero = Viveros.objects.get(pk=id_vivero)
            except Viveros.DoesNotExist:
                data = {
                    'message': 'Vivero no encontrado',
                    'status': 'error'
                }
                return JsonResponse(data, status=404)

            # Verificar si el username ya existe en la base de datos
            if Empleados.objects.filter(username_emple=username_emple).exists():
                data = {
                    'message': 'El nombre de usuario ya está en uso',
                    'status': 'error'
                }
                return JsonResponse(data, status=400)

            # Crear un nuevo empleado en la base de datos
            empleado = Empleados.objects.create(
                Id_vivero=vivero,
                nombres=nombres,
                username_emple=username_emple,
                contraseña=contraseña,
                telefono=telefono,
                correo=correo,
                direccion=direccion,
                cargo=cargo
            )

            data = {
                'message': 'Empleado creado con éxito',
                'status': 'success',
                'empleado_id': empleado.Id_empleados
            }
            return JsonResponse(data, status=201)
        except Exception as e:
            data = {
                'message': 'Error al crear el empleado',
                'status': 'error',
                'error_message': str(e)
            }
            return JsonResponse(data, status=500)

    data = {
        'message': 'Método no permitido',
        'status': 'error'
    }
    return JsonResponse(data, status=405)

@csrf_exempt
def LoginEmpleado(request):
    if request.method == 'POST':
        try:
            # Obtener el JSON del cuerpo de la solicitud
            json_data = json.loads(request.body)
            username_emple = json_data.get('username_emple')
            contrasena = json_data.get('contrasena')
            if username_emple:
                empleado = Empleados.objects.get(username_emple=username_emple)
                # Puedes devolver la información del empleado en JSON como respuesta
                if contrasena == empleado.contraseña:
                    data = {
                    'message':'Logeado con exito',
                    'empleado_id': empleado.Id_empleados,
                    }
                return JsonResponse(data, status=200)
            else:
                response_data = {
                    'message': 'Campo "username_emple" no proporcionado en el JSON',
                    'error_message': 'Campo "username_emple" requerido'
                }
                return JsonResponse(response_data, status=400)
        except Empleados.DoesNotExist:
            response_data = {
                'message': 'Empleado no encontrado',
                'error_message': 'No se encontró un empleado con el username_emple proporcionado'
            }
            return JsonResponse(response_data, status=404)
        except json.JSONDecodeError as e:
            response_data = {
                'message': 'JSON inválido',
                'error_message': str(e)
            }
            return JsonResponse(response_data, status=400)
        except Exception as e:
            response_data = {
                'message': 'Credenciales Invalidas',
                'error_message': 'Unauthorized'
            }
            return JsonResponse(response_data, status=500)
    else:
        response_data = {
            'message': 'Método no permitido',
            'error_message': 'Se esperaba una solicitud POST'
        }
        return JsonResponse(response_data, status=405)

@csrf_exempt
def consultar_empleado_por_id(request):
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body)
            empleado_id = json_data.get("empleado_id")

            empleado = Empleados.objects.get(pk=empleado_id)

            empleado_data = {
                'id': empleado.Id_empleados,
                'id_vivero': empleado.Id_vivero_id,
                'username': empleado.username_emple,
                'nombres': empleado.nombres,
                'telefono': empleado.telefono,
                'correo': empleado.correo,
                'direccion': empleado.direccion,
                'cargo': empleado.cargo
            }

            data = {
                'message': 'Empleado consultado con éxito',
                'status': 'success',
                'empleado': empleado_data
            }
            return JsonResponse(data)
        except Empleados.DoesNotExist:
            data = {
                'message': 'Empleado no encontrado',
                'status': 'error'
            }
            return JsonResponse(data, status=404)
        except Exception as e:
            data = {
                'message': 'Error al consultar el empleado',
                'status': 'error',
                'error_message': str(e)
            }
            return JsonResponse(data, status=500)

    data = {
        'message': 'Método no permitido',
        'status': 'error'
    }
    return JsonResponse(data, status=405)

@csrf_exempt
def actualizar_empleado(request):
    if request.method == 'PUT':
        try:
            json_data = json.loads(request.body)
            empleado_id = json_data.get("empleado_id")
            id_vivero = json_data.get("id_vivero")
            nombres = json_data.get("nombres")
            username_emple = json_data.get("username_emple")
            contraseña = json_data.get("contraseña")
            telefono = json_data.get("telefono")
            correo = json_data.get("correo")
            direccion = json_data.get("direccion")
            cargo = json_data.get("cargo")

            # Verificar si otro empleado ya tiene el mismo username_emple
            existing_empleado = Empleados.objects.exclude(pk=empleado_id).filter(username_emple=username_emple)
            if existing_empleado.exists():
                data = {
                    'message': 'El nombre de usuario ya está en uso por otro empleado',
                    'status': 'error'
                }
                return JsonResponse(data, status=400)

            empleado = Empleados.objects.get(pk=empleado_id)
            empleado.Id_vivero_id = id_vivero
            empleado.nombres = nombres
            empleado.username_emple = username_emple
            empleado.contraseña = contraseña
            empleado.telefono = telefono
            empleado.correo = correo
            empleado.direccion = direccion
            empleado.cargo = cargo
            empleado.save()

            data = {
                'message': 'Empleado actualizado con éxito',
                'status': 'success',
            }
            return JsonResponse(data)
        except Empleados.DoesNotExist:
            data = {
                'message': 'Empleado no encontrado',
                'status': 'error'
            }
            return JsonResponse(data, status=404)
        except Exception as e:
            data = {
                'message': 'Error al actualizar el empleado',
                'status': 'error',
                'error_message': str(e)
            }
            return JsonResponse(data, status=500)

    data = {
        'message': 'Método no permitido',
        'status': 'error'
    }
    return JsonResponse(data, status=405)

@csrf_exempt
def eliminar_empleado_id(request):
    if request.method == 'DELETE':
        try:
            json_data = json.loads(request.body)
            empleado_id = json_data.get("empleado_id")

            empleado = Empleados.objects.get(pk=empleado_id)
            empleado.delete()

            data = {
                'message': 'Empleado eliminado con éxito',
                'status': 'success',
            }
            return JsonResponse(data)
        except Empleados.DoesNotExist:
            data = {
                'message': 'Empleado no encontrado',
                'status': 'error'
            }
            return JsonResponse(data, status=404)
        except Exception as e:
            data = {
                'message': 'Error al eliminar el empleado',
                'status': 'error',
                'error_message': str(e)
            }
            return JsonResponse(data, status=500)

    data = {
        'message': 'Método no permitido',
        'status': 'error'
    }
    return JsonResponse(data, status=405)

@csrf_exempt
def consultar_empleados(request):
    if request.method == 'GET':
        try:
            # Consultar todos los empleados en la base de datos
            empleados = Empleados.objects.all()

            # Crear una lista de empleados en formato JSON
            empleados_list = []
            for empleado in empleados:
                empleado_data = {
                    'id_empleado': empleado.Id_empleados,
                    'id_vivero': empleado.Id_vivero_id,
                    'username_emple': empleado.username_emple,
                    'nombres': empleado.nombres,
                    'telefono': empleado.telefono,
                    'correo': empleado.correo,
                    'direccion': empleado.direccion,
                    'cargo': empleado.cargo
                }
                empleados_list.append(empleado_data)

            data = {
                'message': 'Empleados consultados con éxito',
                'status': 'success',
                'empleados': empleados_list
            }
            return JsonResponse(data)
        except Exception as e:
            data = {
                'message': 'Error al consultar los empleados',
                'status': 'error',
                'error_message': str(e)
            }
            return JsonResponse(data, status=500)

    data = {
        'message': 'Método no permitido',
        'status': 'error'
    }
    return JsonResponse(data, status=405)

@csrf_exempt
def consultar_empleados_por_vivero(request):
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body)
            vivero_id = json_data.get("vivero_id")

            # Consultar todos los empleados de un vivero específico
            empleados = Empleados.objects.filter(Id_vivero_id=vivero_id)

            # Crear una lista de empleados en formato JSON
            empleados_list = []
            for empleado in empleados:
                empleado_data = {
                    'id': empleado.Id_empleados,
                    'id_vivero': empleado.Id_vivero_id,
                    'nombres': empleado.nombres,
                    'telefono': empleado.telefono,
                    'correo': empleado.correo,
                    'direccion': empleado.direccion,
                    'cargo': empleado.cargo
                }
                empleados_list.append(empleado_data)

            data = {
                'message': 'Empleados consultados por vivero con éxito',
                'status': 'success',
                'empleados': empleados_list
            }
            return JsonResponse(data)
        except Exception as e:
            data = {
                'message': 'Error al consultar los empleados por vivero',
                'status': 'error',
                'error_message': str(e)
            }
            return JsonResponse(data, status=500)

    data = {
        'message': 'Método no permitido',
        'status': 'error'
    }
    return JsonResponse(data, status=405)

################################################################################
############################## Plantas #########################################
################################################################################

@csrf_exempt
def crear_planta(request):
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body)
            id_vivero = json_data.get("id_vivero")
            nombre = json_data.get("nombre")
            informacion_general = json_data.get("informacion_general")

            planta = Planta.objects.create(
                Id_vivero_id=id_vivero,
                nombre=nombre,
                informacion_general=informacion_general
            )

            data = {
                'message': 'Planta creada con éxito',
                'status': 'success',
                'planta_id': planta.Id_planta
            }
            return JsonResponse(data, status=201)
        except Exception as e:
            data = {
                'message': 'Error al crear la planta',
                'status': 'error',
                'error_message': str(e)
            }
            return JsonResponse(data, status=500)

    data = {
        'message': 'Método no permitido',
        'status': 'error'
    }
    return JsonResponse(data, status=405)

@csrf_exempt
def consultar_planta_por_id(request):
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body)
            planta_id = json_data.get("planta_id")

            planta = Planta.objects.get(pk=planta_id)

            planta_data = {
                'id_planta': planta.Id_planta,
                'id_vivero': planta.Id_vivero_id,
                'nombre': planta.nombre,
                'informacion_general': planta.informacion_general
            }

            data = {
                'message': 'Planta consultada con éxito',
                'status': 'success',
                'planta': planta_data
            }
            return JsonResponse(data)
        except Planta.DoesNotExist:
            data = {
                'message': 'Planta no encontrada',
                'status': 'error'
            }
            return JsonResponse(data, status=404)
        except Exception as e:
            data = {
                'message': 'Error al consultar la planta',
                'status': 'error',
                'error_message': str(e)
            }
            return JsonResponse(data, status=500)

    data = {
        'message': 'Método no permitido',
        'status': 'error'
    }
    return JsonResponse(data, status=405)

@csrf_exempt
def actualizar_planta(request):
    if request.method == 'PUT':
        try:
            json_data = json.loads(request.body)
            planta_id = json_data.get("planta_id")
            id_vivero = json_data.get("id_vivero")
            nombre = json_data.get("nombre")
            informacion_general = json_data.get("informacion_general")

            planta = Planta.objects.get(pk=planta_id)
            planta.Id_vivero_id = id_vivero
            planta.nombre = nombre
            planta.informacion_general = informacion_general
            planta.save()

            data = {
                'message': 'Planta actualizada con éxito',
                'status': 'success',
            }
            return JsonResponse(data)
        except Planta.DoesNotExist:
            data = {
                'message': 'Planta no encontrada',
                'status': 'error'
            }
            return JsonResponse(data, status=404)
        except Exception as e:
            data = {
                'message': 'Error al actualizar la planta',
                'status': 'error',
                'error_message': str(e)
            }
            return JsonResponse(data, status=500)

    data = {
        'message': 'Método no permitido',
        'status': 'error'
    }
    return JsonResponse(data, status=405)

@csrf_exempt
def eliminar_planta(request):
    if request.method == 'DELETE':
        try:
            json_data = json.loads(request.body)
            planta_id = json_data.get("planta_id")

            planta = Planta.objects.get(pk=planta_id)
            planta.delete()

            data = {
                'message': 'Planta eliminada con éxito',
                'status': 'success',
            }
            return JsonResponse(data)
        except Planta.DoesNotExist:
            data = {
                'message': 'Planta no encontrada',
                'status': 'error'
            }
            return JsonResponse(data, status=404)
        except Exception as e:
            data = {
                'message': 'Error al eliminar la planta',
                'status': 'error',
                'error_message': str(e)
            }
            return JsonResponse(data, status=500)

    data = {
        'message': 'Método no permitido',
        'status': 'error'
    }
    return JsonResponse(data, status=405)

@csrf_exempt
def consultar_plantas_por_vivero(request):
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body)
            vivero_id = json_data.get("vivero_id")

            # Consultar todas las plantas de un vivero específico
            plantas = Planta.objects.filter(Id_vivero_id=vivero_id)

            # Crear una lista de plantas en formato JSON
            plantas_list = []
            for planta in plantas:
                planta_data = {
                    'id_planta': planta.Id_planta,
                    'id_vivero': planta.Id_vivero_id,
                    'nombre': planta.nombre,
                    'informacion_general': planta.informacion_general
                }
                plantas_list.append(planta_data)

            data = {
                'message': 'Plantas consultadas por vivero con éxito',
                'status': 'success',
                'plantas': plantas_list
            }
            return JsonResponse(data)
        except Exception as e:
            data = {
                'message': 'Error al consultar las plantas por vivero',
                'status': 'error',
                'error_message': str(e)
            }
            return JsonResponse(data, status=500)

    data = {
        'message': 'Método no permitido',
        'status': 'error'
    }
    return JsonResponse(data, status=405)

@csrf_exempt
def obtener_todas_las_plantas(request):
    if request.method == 'POST':
        try:
            # Consultar todas las plantas en la base de datos
            plantas = Planta.objects.all()

            # Crear una lista de plantas en formato JSON
            plantas_list = []
            for planta in plantas:
                planta_data = {
                    'id_planta': planta.Id_planta,
                    'id_vivero': planta.Id_vivero_id,
                    'nombre': planta.nombre,
                    'informacion_general': planta.informacion_general
                    # Agregar otros campos si es necesario
                }
                plantas_list.append(planta_data)

            data = {
                'message': 'Plantas consultadas con éxito',
                'status': 'success',
                'plantas': plantas_list
            }
            return JsonResponse(data)
        except Exception as e:
            data = {
                'message': 'Error al consultar las plantas',
                'status': 'error',
                'error_message': str(e)
            }
            return JsonResponse(data, status=500)

    data = {
        'message': 'Método no permitido',
        'status': 'error'
    }
    return JsonResponse(data, status=405)

################################################################################
########################## Enfermendad #########################################
################################################################################

@csrf_exempt
def crear_enfermedad(request):
    if request.method == 'POST':
        id_planta = request.POST.get("id_planta")
        nombre = request.POST.get("nombre")
        fase = request.POST.get("fase")
        informacion_general = request.POST.get("informacion_general")
        fase_image = request.FILES.get("fase_image")  # Obtener archivo adjunto de imagen
        try:
            # Crear la enfermedad sin la imagen
            enfermedad_nueva = enfermedad.objects.create(
                Id_planta_id=id_planta,
                nombre=nombre,
                fase=fase,
                informacion_general=informacion_general
            )

            if fase_image:
                # Leer y convertir la imagen en formato Base64
                fase_image_base64 = base64.b64encode(fase_image.read()).decode('utf-8')
                enfermedad_nueva.fase_image = fase_image_base64
                enfermedad_nueva.save()

            data = {
                'message': 'Enfermedad creada con éxito',
                'status': 'success',
                'enfermedad_id': enfermedad_nueva.Id_enfermedad
            }
            return JsonResponse(data, status=201)
        except Exception as e:
            data = {
                'message': 'Error al crear la enfermedad',
                'status': 'error',
                'error_message': str(e)
            }
            return JsonResponse(data, status=500)

    data = {
        'message': 'Método no permitido',
        'status': 'error'
    }
    return JsonResponse(data, status=405)

@csrf_exempt
def obtener_todas_enfermedades(request):
    if request.method == 'GET':
        try:
            todas_las_enfermedades = enfermedad.objects.all()
            enfermedades_data = []

            for enfermedad_item in todas_las_enfermedades:
                enfermedad_info = {
                    'id_enfermedad': enfermedad_item.Id_enfermedad,
                    'id_planta': enfermedad_item.Id_planta_id,
                    'nombre': enfermedad_item.nombre,
                    'fase': enfermedad_item.fase,
                    'informacion_general': enfermedad_item.informacion_general,
                    'fase_image': enfermedad_item.fase_image,
                }
                enfermedades_data.append(enfermedad_info)

            data = {
                'message': 'Enfermedades consultadas con éxito',
                'status': 'success',
                'enfermedades': enfermedades_data
            }
            return JsonResponse(data, status=200)
        except Exception as e:
            data = {
                'message': 'Error al consultar las enfermedades',
                'status': 'error',
                'error_message': str(e)
            }
            return JsonResponse(data, status=500)

    data = {
        'message': 'Método no permitido',
        'status': 'error'
    }
    return JsonResponse(data, status=405)

@csrf_exempt
def actualizar_enfermedad(request):
    if request.method == 'POST':
        try:
            Id_enfermedad = request.POST.get("enfermedad_id")

            # Verificar si la enfermedad existe antes de intentar actualizarla
            if enfermedad.objects.filter(pk=Id_enfermedad).exists():
                id_planta = request.POST.get("id_planta")
                nombre = request.POST.get("nombre")
                fase = request.POST.get("fase")
                informacion_general = request.POST.get("informacion_general")
                fase_image = request.FILES.get("fase_image")  # Obtener la imagen como archivo adjunto

                # Buscar la enfermedad por su ID de manera segura
                enfermedad_model = enfermedad.objects.get(pk=Id_enfermedad)

                if id_planta:
                    enfermedad_model.Id_planta_id = id_planta
                if nombre:
                    enfermedad_model.nombre = nombre
                if fase:
                    enfermedad_model.fase = fase
                if informacion_general:
                    enfermedad_model.informacion_general = informacion_general
                if fase_image:
                    # Leer y convertir la imagen en formato Base64
                    fase_image_base64 = base64.b64encode(fase_image.read()).decode('utf-8')
                    enfermedad_model.fase_image = fase_image_base64

                enfermedad_model.save()

                data = {
                    'message': 'Enfermedad actualizada con éxito',
                    'status': 'success'
                }
                return JsonResponse(data)
            else:
                data = {
                    'message': 'Enfermedad no encontrada',
                    'status': 'error'
                }
                return JsonResponse(data, status=404)
        except Exception as e:
            data = {
                'message': 'Error al actualizar la enfermedad',
                'status': 'error',
                'error_message': str(e)
            }
            return JsonResponse(data, status=500)

    data = {
        'message': 'Método no permitido',
        'status': 'error'
    }
    return JsonResponse(data, status=405)

@csrf_exempt
def consultar_enfermedad_por_id(request):
    if request.method == 'GET':
        try:
            json_data = json.loads(request.body)
            enfermedad_id = json_data.get("enfermedad_id")

            # Consultar la enfermedad por su ID
            try:
                enfermedad_obj = enfermedad.objects.get(pk=enfermedad_id)

                # Crear un JSON con los datos de la enfermedad
                enfermedad_data = {
                    'id_enfermedad': enfermedad_obj.Id_enfermedad,
                    'id_planta': enfermedad_obj.Id_planta_id,
                    'nombre': enfermedad_obj.nombre,
                    'fase': enfermedad_obj.fase,
                    'informacion_general': enfermedad_obj.informacion_general,
                    'fase_image': enfermedad_obj.fase_image
                }

                data = {
                    'message': 'Enfermedad consultada con éxito',
                    'status': 'success',
                    'enfermedad': enfermedad_data
                }
                return JsonResponse(data)
            except enfermedad.DoesNotExist:
                data = {
                    'message': 'Enfermedad no encontrada',
                    'status': 'error'
                }
                return JsonResponse(data, status=404)

        except Exception as e:
            data = {
                'message': 'Error al consultar la enfermedad',
                'status': 'error',
                'error_message': str(e)
            }
            return JsonResponse(data, status=500)

    data = {
        'message': 'Método no permitido',
        'status': 'error'
    }
    return JsonResponse(data, status=405)

@csrf_exempt
def eliminar_enfermedad_por_id(request):
    if request.method == 'DELETE':
        try:
            # Obtener el ID de la enfermedad desde el JSON de la solicitud
            json_data = json.loads(request.body)
            enfermedad_id = json_data.get("enfermedad_id")

            # Consultar la enfermedad por su ID
            enfermedad_obj = enfermedad.objects.get(pk=enfermedad_id)

            # Eliminar la enfermedad
            enfermedad_obj.delete()

            data = {
                'message': 'Enfermedad eliminada con éxito',
                'status': 'success'
            }
            return JsonResponse(data)
        except enfermedad.DoesNotExist:
            data = {
                'message': 'Enfermedad no encontrada',
                'status': 'error'
            }
            return JsonResponse(data, status=404)
        except Exception as e:
            data = {
                'message': 'Error al eliminar la enfermedad',
                'status': 'error',
                'error_message': str(e)
            }
            return JsonResponse(data, status=500)

    data = {
        'message': 'Método no permitido',
        'status': 'error'
    }
    return JsonResponse(data, status=405)


################################################################################
########################## Tratamiento #########################################
################################################################################

@csrf_exempt
def crear_tratamiento(request):
    if request.method == 'POST':
        id_enfermedad = request.POST.get("id_enfermedad")
        producto_quimico = request.POST.get("producto_quimico")
        descripcion_tratamiento = request.POST.get("descripcion_tratamiento")
        producto_quimico_image = request.FILES.get("producto_quimico_image")  # Obtener archivo adjunto de imagen

        try:
            # Crear el tratamiento sin la imagen
            tratamiento_nuevo = Tratamientos.objects.create(
                Id_enfermedad_id=id_enfermedad,
                producto_quimico=producto_quimico,
                descripcion_tratamiento=descripcion_tratamiento
            )

            if producto_quimico_image:
                # Leer y convertir la imagen en formato Base64
                producto_quimico_image_base64 = base64.b64encode(producto_quimico_image.read()).decode('utf-8')
                tratamiento_nuevo.producto_quimico_image = producto_quimico_image_base64
                tratamiento_nuevo.save()

            data = {
                'message': 'Tratamiento creado con éxito',
                'status': 'success',
                'tratamiento_id': tratamiento_nuevo.Id_tratamiento
            }
            return JsonResponse(data, status=201)
        except Exception as e:
            data = {
                'message': 'Error al crear el tratamiento',
                'status': 'error',
                'error_message': str(e)
            }
            return JsonResponse(data, status=500)

    data = {
        'message': 'Método no permitido',
        'status': 'error'
    }
    return JsonResponse(data, status=405)

@csrf_exempt
def consultar_tratamiento_por_id(request):
    if request.method == 'GET':
        try:
            # Obtener el ID del tratamiento desde el JSON de la solicitud
            json_data = json.loads(request.body)
            tratamiento_id = json_data.get("tratamiento_id")

            # Consultar el tratamiento por su ID
            tratamiento = Tratamientos.objects.get(pk=tratamiento_id)

            # Crear un JSON con los datos del tratamiento
            tratamiento_data = {
                'Id_tratamiento': tratamiento.Id_tratamiento,
                'Id_enfermedad': tratamiento.Id_enfermedad_id,
                'producto_quimico': tratamiento.producto_quimico,
                'producto_quimico_image': tratamiento.producto_quimico_image,
                'descripcion_tratamiento': tratamiento.descripcion_tratamiento
            }

            data = {
                'message': 'Tratamiento consultado con éxito',
                'status': 'success',
                'tratamiento': tratamiento_data
            }
            return JsonResponse(data)
        except Tratamientos.DoesNotExist:
            data = {
                'message': 'Tratamiento no encontrado',
                'status': 'error'
            }
            return JsonResponse(data, status=404)
        except Exception as e:
            data = {
                'message': 'Error al consultar el tratamiento',
                'status': 'error',
                'error_message': str(e)
            }
            return JsonResponse(data, status=500)

    data = {
        'message': 'Método no permitido',
        'status': 'error'
    }
    return JsonResponse(data, status=405)

@csrf_exempt
def actualizar_tratamiento_por_id(request):
    if request.method == 'POST':
        try:
            # Obtener datos del formulario y el archivo adjunto
            tratamiento_id = request.POST.get("tratamiento_id")
            producto_quimico = request.POST.get("producto_quimico")
            descripcion_tratamiento = request.POST.get("descripcion_tratamiento")
            producto_quimico_image = request.FILES.get("producto_quimico_image")  # Obtener archivo adjunto de imagen

            # Verificar si el tratamiento existe antes de intentar actualizarlo
            if Tratamientos.objects.filter(pk=tratamiento_id).exists():
                # Consultar el tratamiento por su ID
                tratamiento = Tratamientos.objects.get(pk=tratamiento_id)

                # Actualizar los campos del tratamiento
                tratamiento.producto_quimico = producto_quimico
                tratamiento.descripcion_tratamiento = descripcion_tratamiento

                if producto_quimico_image:
                    # Leer y convertir la imagen en formato Base64
                    producto_quimico_image_base64 = base64.b64encode(producto_quimico_image.read()).decode('utf-8')
                    tratamiento.producto_quimico_image = producto_quimico_image_base64

                tratamiento.save()

                data = {
                    'message': 'Tratamiento actualizado con éxito',
                    'status': 'success'
                }
                return JsonResponse(data)
            else:
                data = {
                    'message': 'Tratamiento no encontrado',
                    'status': 'error'
                }
                return JsonResponse(data, status=404)
        except Exception as e:
            data = {
                'message': 'Error al actualizar el tratamiento',
                'status': 'error',
                'error_message': str(e)
            }
            return JsonResponse(data, status=500)

    data = {
        'message': 'Método no permitido',
        'status': 'error'
    }
    return JsonResponse(data, status=405)

@csrf_exempt
def eliminar_tratamiento(request):
    if request.method == 'DELETE':
        try:
            # Obtener el ID del tratamiento desde el JSON de la solicitud
            json_data = json.loads(request.body)
            tratamiento_id = json_data.get("tratamiento_id")

            # Consultar el tratamiento por su ID
            tratamiento = Tratamientos.objects.get(pk=tratamiento_id)

            # Eliminar el tratamiento
            tratamiento.delete()

            data = {
                'message': 'Tratamiento eliminado con éxito',
                'status': 'success'
            }
            return JsonResponse(data)
        except Tratamientos.DoesNotExist:
            data = {
                'message': 'Tratamiento no encontrado',
                'status': 'error'
            }
            return JsonResponse(data, status=404)
        except Exception as e:
            data = {
                'message': 'Error al eliminar el tratamiento',
                'status': 'error',
                'error_message': str(e)
            }
            return JsonResponse(data, status=500)

    data = {
        'message': 'Método no permitido',
        'status': 'error'
    }
    return JsonResponse(data, status=405)

@csrf_exempt
def obtener_todos_los_tratamientos(request):
    if request.method == 'GET':
        try:
            # Consultar todos los tratamientos en la base de datos
            tratamientos = Tratamientos.objects.all()

            # Crear una lista para almacenar los datos de los tratamientos
            tratamientos_data = []

            for tratamiento in tratamientos:
                tratamiento_data = {
                    'Id_tratamiento': tratamiento.Id_tratamiento,
                    'Id_enfermedad': tratamiento.Id_enfermedad_id,
                    'producto_quimico': tratamiento.producto_quimico,
                    'producto_quimico_image': tratamiento.producto_quimico_image,
                    'descripcion_tratamiento': tratamiento.descripcion_tratamiento
                }
                tratamientos_data.append(tratamiento_data)

            data = {
                'message': 'Tratamientos consultados con éxito',
                'status': 'success',
                'tratamientos': tratamientos_data
            }
            return JsonResponse(data)
        except Exception as e:
            data = {
                'message': 'Error al consultar los tratamientos',
                'status': 'error',
                'error_message': str(e)
            }
            return JsonResponse(data, status=500)

    data = {
        'message': 'Método no permitido',
        'status': 'error'
    }
    return JsonResponse(data, status=405)

################################################################################
################### Registro enfermedades ######################################
################################################################################

@csrf_exempt
def Prediccted(request):
    if request.method == 'POST':
        # Procesar la imagen aquí

        if 'image' in request.FILES:
            image_file = request.FILES['image']

            # Crea una instancia de PIL Image desde el archivo

            image = Image.open(image_file).convert("RGB")
            image = image.resize((224, 224))

            # Convertir la imagen a una cadena Base64
            image_base64 = base64.b64encode(image.tobytes()).decode('utf-8')

            # Convert the image to a NumPy array
            image = np.array(image)
            image = image / 255.0
            image = image.reshape(1, 224, 224, 3)
            print(image.shape)

            model_path = './(Adam_39.42%)Mobilnet.h5'
            model = load_model(model_path)
            # Predict the label
            prediction = model.predict(image)
            prediction = prediction.tolist()

            # Obtener el valor más alto en la lista anidada
            valor_mas_alto = max(prediction[0])
            print(valor_mas_alto)
            # Obtener el índice del valor más alto
            indice_mas_alto = prediction[0].index(valor_mas_alto)

            # Obtener los campos nombre de planta, enfermedad y predict
            nombre_planta = 'Mango'
            enfermedad = 'hongos'
            predict = indice_mas_alto

            # Guardar los campos en la tabla Registros_enfermedad
            registro = Registros_enfermedad(
                nombre_planta=nombre_planta,
                nombre_enfer=enfermedad,
                fase=str(predict),  # Convierte predict en una cadena
                imagen=image_base64  # Guarda la imagen como Base64
            )
            registro.save()

            data = {
                'status': 'success',
                'nombre de planta': nombre_planta,
                'enfermedad': enfermedad,
                'Fase': predict
            }
            return JsonResponse(data)
        else:
            data = {
                'message': 'No se proporcionó ninguna imagen',
                'status': 'error'
            }
            return JsonResponse(data)








