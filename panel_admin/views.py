import datetime
import json
from django.db import connection
from django.shortcuts import render, redirect

from panel_admin.models import *

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Permission

#import ajax
from django.http import JsonResponse

# Create your views here.

@login_required(login_url='login_admin')
def index(request):
    if request.method == 'GET':
        # top colegios por cantidad de encuestas
        colegios = TColegio.objects.all()
        colegios_top = []
        for colegio in colegios:
            colegios_top.append({
                'colegio': colegio.nombre_colegio,
                'cantidad': TAlumno.objects.filter(id_colegio=colegio.id_colegio).count()
            })
        colegios_top.sort(key=lambda x: x['cantidad'], reverse=True)
        colegios_top = colegios_top[:4]

        total_colegios = TColegio.objects.all().count()
        total_alumnos = TAlumno.objects.all().count()
        #total_encuestas = TEncuesta.objects.filter(estado_encuesta=1).count()
        total_encuestas = TEncuesta.objects.filter(estado_encuesta=1).count()

        # alumnos union con encuestas
        alumnos = TAlumno.objects.all()
        alumnos_encuestas = []
        for alumno in alumnos:
            encuestas = TEncuesta.objects.filter(id_alumno=alumno.id_alumno)
            if encuestas.count() > 0:
                alumnos_encuestas.append({
                    'fecha': encuestas[0].fecha_encuesta.strftime('%d/%m/%Y'),
                    'nombre': alumno.nombre_alumno+ ' ' + alumno.apellido_alumno,
                    'colegio': alumno.id_colegio.nombre_colegio,
                    'estado': encuestas[0].estado_encuesta,
                    'cantidad': TRespuesta.objects.filter(id_encuesta=encuestas[0].id_encuesta).count(),
                    'total': TPregunta.objects.all().count()
                })
        alumnos_encuestas.sort(key=lambda x: x['fecha'], reverse=True)
        alumnos_encuestas = alumnos_encuestas[:4]

        # grafico de encuestas por sexo INICIO
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM v_reportes_por_sexo order by mes desc LIMIT 6")
        rows = cursor.fetchall()
        sexo_alumno = []
        for row in rows:
            sexo_alumno.append({
                'meses': row[0],
                'm': row[2],
                'f': row[3]
            })
        # grafico de encuestas por sexo FIN
        # imprimr meses
        sexo_alumno = json.dumps(sexo_alumno)
        return render(request, 'panel_admin/index.html', {
            'colegios_top': colegios_top,
            'total_colegios': total_colegios,
            'total_alumnos': total_alumnos,
            'total_encuestas': total_encuestas,
            'alumnos_encuestas': alumnos_encuestas,
            'sexo_alumno': sexo_alumno
            })
    else:
        return render(request, 'panel_admin/index.html')
@login_required(login_url='login_admin')
def encuestas(request):
    if request.method == 'GET':
        # alumnos union con encuestas
        alumnos = TAlumno.objects.all()
        alumnos_encuestas = []
        for alumno in alumnos:
            encuestas = TEncuesta.objects.filter(id_alumno=alumno.id_alumno)
            if encuestas.count() > 0:
                alumnos_encuestas.append({
                    'fecha': encuestas[0].fecha_encuesta.strftime('%d/%m/%Y'),
                    'hora' : encuestas[0].hora_encuesta.strftime('%H:%M:%S'),
                    'nombre': alumno.nombre_alumno+ ' ' + alumno.apellido_alumno,
                    'colegio': alumno.id_colegio.nombre_colegio,
                    'estado': encuestas[0].estado_encuesta,
                    'cantidad': TRespuesta.objects.filter(id_encuesta=encuestas[0].id_encuesta).count(),
                    'total': TPregunta.objects.all().count()
                })
        alumnos_encuestas.sort(key=lambda x: x['fecha'], reverse=True)
        return render(request, 'panel_admin/encuestas/listar.html', {'alumnos_encuestas': alumnos_encuestas})
    else:
        return render(request, 'panel_admin/encuestas/listar.html')

# Begin colegios
@login_required(login_url='login_admin')
@permission_required('panel_admin.mispermisos_view_tcolegio', login_url='/admin/')
def colegios(request):
    colegios = TColegio.objects.all()
    return render(request, 'panel_admin/colegios/listar.html', {'colegios': colegios})
@login_required(login_url='login_admin')
@permission_required('panel_admin.mispermisos_view_tcolegio', login_url='/admin/')
def colegios_crear(request):
    # nuevo colegio
    if request.method == 'POST':
        username_colegio = request.POST['username_colegio']
        password_colegio = request.POST['password_colegio']
        user = User.objects.create_user(username_colegio, '', password_colegio)
        user.is_active = request.POST['estado_colegio']
        user.is_staff = False
        user.save()
        colegio = TColegio()
        colegio.codigo_colegio = request.POST['codigo_colegio']
        colegio.nombre_colegio = request.POST['nombre_colegio']
        colegio.telefono_colegio = request.POST['telefono_colegio']
        colegio.direccion_colegio = request.POST['direccion_colegio']
        colegio.estado_colegio = request.POST['estado_colegio']
        # obtener id de user creado
        colegio.usuario = user

        print(user)
        
        colegio.save()
        # retornando con mensaje de exito
        return redirect('colegios')
    else:
        return render(request, 'panel_admin/colegios/crear.html')
@login_required(login_url='login_admin')
@permission_required('panel_admin.mispermisos_view_tcolegio', login_url='/admin/')
def colegios_editar(request, id_colegio):
    # editar colegio
    colegio = TColegio.objects.get(id_colegio=id_colegio)
    if request.method == 'GET':
        return render(request, 'panel_admin/colegios/editar.html', {'colegio': colegio})
    else:
        colegio.codigo_colegio = request.POST['codigo_colegio']
        colegio.nombre_colegio = request.POST['nombre_colegio']
        colegio.telefono_colegio = request.POST['telefono_colegio']
        colegio.direccion_colegio = request.POST['direccion_colegio']
        username_colegio = request.POST['username_colegio']
        password_colegio = request.POST['password_colegio']
        colegio.estado_colegio = request.POST['estado_colegio']
        colegio.save()
        # actualizando usuario
        user = User.objects.get(id=colegio.usuario.id)
        user.username = username_colegio
        user.is_active = request.POST['estado_colegio']
        user.set_password(password_colegio)
        user.save()
        # retornando con mensaje de exito
        return redirect('colegios')
@login_required(login_url='login_admin')
@permission_required('panel_admin.mispermisos_view_tcolegio', login_url='/admin/')
def colegios_eliminar(request, id_colegio):
    # eliminar colegio
    colegio = TColegio.objects.get(id_colegio=id_colegio)
    colegio.delete()
    return redirect('colegios')
# End colegios


# Begin Alumnos
@login_required(login_url='login_admin')
@permission_required('panel_admin.mispermisos_view_talumno', login_url='/admin/')
def alumnos(request):
    alumnos = TAlumno.objects.all()
    return render(request, 'panel_admin/alumnos/listar.html', {'alumnos': alumnos})
@login_required(login_url='login_admin')
@permission_required('panel_admin.mispermisos_view_talumno', login_url='/admin/')
def alumnos_crear(request):
    # nuevo alumno
    if request.method == 'POST':
        alumno = TAlumno()
        alumno.nombre_alumno = request.POST['nombre_alumno']
        alumno.apellido_alumno = request.POST['apellido_alumno']
        alumno.dni_alumno = request.POST['dni_alumno']
        alumno.fecha_nacimiento_alumno = request.POST['fecha_nacimiento_alumno']
        alumno.grado_alumno = request.POST['grado_alumno']
        alumno.estado_alumno = request.POST['estado_alumno']
        alumno.id_colegio = TColegio.objects.get(id_colegio=request.POST['id_colegio'])
        alumno.save()
        # retornando con mensaje de exito
        return redirect('alumnos')
    else:
        colegios = TColegio.objects.all()
        return render(request, 'panel_admin/alumnos/crear.html', {'colegios': colegios})
@login_required(login_url='login_admin')
@permission_required('panel_admin.mispermisos_view_talumno', login_url='/admin/')
def alumnos_editar(request, id_alumno):
    # editar alumno
    alumno = TAlumno.objects.get(id_alumno=id_alumno)
    if request.method == 'GET':
        colegios = TColegio.objects.all()
        return render(request, 'panel_admin/alumnos/editar.html', {'alumno': alumno, 'colegios': colegios})
    else:
        alumno.nombre_alumno = request.POST['nombre_alumno']
        alumno.apellido_alumno = request.POST['apellido_alumno']
        alumno.dni_alumno = request.POST['dni_alumno']
        alumno.fecha_nacimiento_alumno = request.POST['fecha_nacimiento_alumno']
        alumno.grado_alumno = request.POST['grado_alumno']
        alumno.estado_alumno = request.POST['estado_alumno']
        colegio = TColegio.objects.get(id_colegio=request.POST['id_colegio'])
        alumno.id_colegio = colegio
        alumno.save()
        # retornando con mensaje de exito
        return redirect('alumnos')
@login_required(login_url='login_admin')
@permission_required('panel_admin.mispermisos_view_talumno', login_url='/admin/')
def alumnos_eliminar(request, id_alumno):
    # eliminar alumno
    alumno = TAlumno.objects.get(id_alumno=id_alumno)
    alumno.delete()
    return redirect('alumnos')
# End Alumnos


# Begin Categoria de las preguntas
@login_required(login_url='login_admin')
@permission_required('panel_admin.mispermisos_view_tcategoria', login_url='/admin/')
def categorias(request):
    categorias = TCategoria.objects.all()
    return render(request, 'panel_admin/categorias/listar.html', {'categorias': categorias})
@login_required(login_url='login_admin')
@permission_required('panel_admin.mispermisos_view_tcategoria', login_url='/admin/')
def categorias_crear(request):
    # nueva categoria
    if request.method == 'POST':
        categoria = TCategoria()
        categoria.nombre_categoria = request.POST['nombre_categoria']
        categoria.estado_categoria = request.POST['estado_categoria']
        categoria.save()
        # retornando con mensaje de exito
        return redirect('categorias')
    else:
        return render(request, 'panel_admin/categorias/crear.html')
@login_required(login_url='login_admin')
@permission_required('panel_admin.mispermisos_view_tcategoria', login_url='/admin/')
def categorias_editar(request, id_categoria):
    # editar categoria
    categoria = TCategoria.objects.get(id_categoria=id_categoria)
    if request.method == 'GET':
        return render(request, 'panel_admin/categorias/editar.html', {'categoria': categoria})
    else:
        categoria.nombre_categoria = request.POST['nombre_categoria']
        categoria.estado_categoria = request.POST['estado_categoria']
        categoria.save()
        # retornando con mensaje de exito
        return redirect('categorias')
@login_required(login_url='login_admin')
@permission_required('panel_admin.mispermisos_view_tcategoria', login_url='/admin/')
def categorias_eliminar(request, id_categoria):
    # eliminar categoria
    categoria = TCategoria.objects.get(id_categoria=id_categoria)
    categoria.delete()
    return redirect('categorias')
# End Categoria de las preguntas


# Begin preguntas
@login_required(login_url='login_admin')
@permission_required('panel_admin.mispermisos_view_tpregunta', login_url='/admin/')
def preguntas(request):
    preguntas = TPregunta.objects.all()
    return render(request, 'panel_admin/preguntas/listar.html', {'preguntas': preguntas})
@login_required(login_url='login_admin')
@permission_required('panel_admin.mispermisos_view_tpregunta', login_url='/admin/')
def preguntas_crear(request):
    # nueva pregunta
    if request.method == 'POST':
        pregunta = TPregunta()
        pregunta.nombre_pregunta = request.POST['nombre_pregunta']
        pregunta.id_vocacion = TVocacion.objects.get(id_vocacion=request.POST['id_vocacion'])
        pregunta.id_categoria = TCategoria.objects.get(id_categoria=request.POST['id_categoria'])
        pregunta.save()
        # retornando con mensaje de exito
        return redirect('preguntas')
    else:
        categorias = TCategoria.objects.all()
        vocaciones = TVocacion.objects.all()
        return render(request, 'panel_admin/preguntas/crear.html', {'categorias': categorias, 'vocaciones': vocaciones})
@login_required(login_url='login_admin')
@permission_required('panel_admin.mispermisos_view_tpregunta', login_url='/admin/')
def preguntas_editar(request, id_pregunta):
    # editar pregunta
    pregunta = TPregunta.objects.get(id_pregunta=id_pregunta)
    if request.method == 'GET':
        categorias = TCategoria.objects.all()
        vocaciones = TVocacion.objects.all()
        return render(request, 'panel_admin/preguntas/editar.html', {'pregunta': pregunta, 'categorias': categorias, 'vocaciones': vocaciones})
    else:
        pregunta.nombre_pregunta = request.POST['nombre_pregunta']
        pregunta.id_categoria = TCategoria.objects.get(id_categoria=request.POST['id_categoria'])
        pregunta.id_vocacion = TVocacion.objects.get(id_vocacion=request.POST['id_vocacion'])
        pregunta.save()
        # retornando con mensaje de exito
        return redirect('preguntas')
@login_required(login_url='login_admin')
@permission_required('panel_admin.mispermisos_view_tpregunta', login_url='/admin/')
def preguntas_eliminar(request, id_pregunta):
    # eliminar pregunta
    pregunta = TPregunta.objects.get(id_pregunta=id_pregunta)
    pregunta.delete()
    return redirect('preguntas')
# End preguntas



# Begin Respuestas
@login_required(login_url='login_admin')
@permission_required('panel_admin.mispermisos_view_trespuesta', login_url='/admin/')
def respuestas(request):
    if request.method == 'POST':
        # listar respuestas por dni
        dni_alumno = request.POST['dni_alumno']
        if TAlumno.objects.filter(dni_alumno=dni_alumno).exists():
            id_alumno = TAlumno.objects.get(dni_alumno=dni_alumno)
            id_encuesta = TEncuesta.objects.get(id_alumno=id_alumno)
            respuestas = TRespuesta.objects.filter(id_encuesta=id_encuesta)
            print(dni_alumno)
            return render(request, 'panel_admin/respuestas/listar.html', {'respuestas': respuestas, 'dni_alumno': dni_alumno})
        else:
            return render(request, 'panel_admin/respuestas/listar.html', {'mensaje': 'El alumno no existe'})
    else:
        return render(request, 'panel_admin/respuestas/listar.html')
# End Respuestas

# Begin Configuracion
@login_required(login_url='login_admin')
@permission_required('TConfiguracion.*', login_url='/admin/')
def configuracion(request):
    if request.method == 'GET':
        configuracion = TConfiguracion.objects.first()
        return render(request, 'panel_admin/configuracion/configuracion.html', {'configuracion': configuracion})
    else:
        configuracion = TConfiguracion.objects.get(id_configuracion=1)
        configuracion.telefono_configuracion = request.POST['telefono_conf']
        configuracion.correo_configuracion = request.POST['correo_conf']
        configuracion.direccion_configuracion = request.POST['direccion_conf']
        configuracion.save()
        return redirect('configuracion')
# End Configuracion

# Begin comunicados
@login_required(login_url='login_admin')
@permission_required('panel_admin.mispermisos_view_tcomunicado', login_url='/admin/')
def comunicados(request):
    comunicados = TComunicado.objects.all()
    return render(request, 'panel_admin/comunicados/listar.html', {'comunicados': comunicados})
@login_required(login_url='login_admin')
@permission_required('panel_admin.mispermisos_view_tcomunicado', login_url='/admin/')
def comunicados_crear(request):
    # nuevo comunicado
    if request.method == 'POST':
        comunicado = TComunicado()
        comunicado.nombre_comunicado = request.POST['nombre_comunicado']
        comunicado.img_comunicado = 'img_comunicado.jpg'
        comunicado.fecha_comunicado = request.POST['fecha_comunicado']
        comunicado.estado_comunicado = request.POST['estado_comunicado']
        comunicado.save()
        # retornando con mensaje de exito
        return redirect('comunicados')
    else:
        return render(request, 'panel_admin/comunicados/crear.html')
@login_required(login_url='login_admin')
@permission_required('panel_admin.mispermisos_view_tcomunicado', login_url='/admin/')
def comunicados_editar(request, id_comunicado):
    # editar comunicado
    comunicado = TComunicado.objects.get(id_comunicado=id_comunicado)
    if request.method == 'GET':
        return render(request, 'panel_admin/comunicados/editar.html', {'comunicado': comunicado})
    else:
        comunicado.nombre_comunicado = request.POST['nombre_comunicado']
        comunicado.fecha_comunicado = request.POST['fecha_comunicado']
        comunicado.img_comunicado = 'img_comunicado.jpg'
        comunicado.estado_comunicado = request.POST['estado_comunicado']
        comunicado.save()
        # retornando con mensaje de exito
        return redirect('comunicados')
@login_required(login_url='login_admin')
@permission_required('panel_admin.mispermisos_view_tcomunicado', login_url='/admin/')
def comunicados_eliminar(request, id_comunicado):
    # eliminar comunicado
    comunicado = TComunicado.objects.get(id_comunicado=id_comunicado)
    comunicado.delete()
    return redirect('comunicados')
# End comunicados


# Begin Carreras
@login_required(login_url='login_admin')
@permission_required('panel_admin.mispermisos_view_tcarrera', login_url='/admin/')
def carreras(request):
    carreras = TCarrera.objects.all()
    return render(request, 'panel_admin/carreras/listar.html', {'carreras': carreras})
@login_required(login_url='login_admin')
@permission_required('panel_admin.mispermisos_view_tcarrera', login_url='/admin/')
def carreras_crear(request):
    # nueva carrera
    if request.method == 'POST':
        carrera = TCarrera()
        carrera.nombre_carrera = request.POST['nombre_carrera']
        carrera.id_vocacion = TVocacion.objects.get(id_vocacion=request.POST['id_vocacion'])
        carrera.estado_carrera = request.POST['estado_carrera']
        carrera.save()
        # retornando con mensaje de exito
        return redirect('carreras')
    else:
        vocaciones = TVocacion.objects.all()
        return render(request, 'panel_admin/carreras/crear.html', {'vocaciones': vocaciones})
@login_required(login_url='login_admin')
@permission_required('panel_admin.mispermisos_view_tcarrera', login_url='/admin/')
def carreras_editar(request, id_carrera):
    # editar carrera
    carrera = TCarrera.objects.get(id_carrera=id_carrera)
    if request.method == 'GET':
        vocaciones = TVocacion.objects.all()
        return render(request, 'panel_admin/carreras/editar.html', {'carrera': carrera, 'vocaciones': vocaciones})
    else:
        carrera.nombre_carrera = request.POST['nombre_carrera']
        carrera.id_vocacion = TVocacion.objects.get(id_vocacion=request.POST['id_vocacion'])
        carrera.estado_carrera = request.POST['estado_carrera']
        carrera.save()
        # retornando con mensaje de exito
        return redirect('carreras')
@login_required(login_url='login_admin')
@permission_required('panel_admin.mispermisos_view_tcarrera', login_url='/admin/')
def carreras_eliminar(request, id_carrera):
    # eliminar carrera
    carrera = TCarrera.objects.get(id_carrera=id_carrera)
    carrera.delete()
    return redirect('carreras')
# End Carreras


# Begin vocaciones
@login_required(login_url='login_admin')
@permission_required('panel_admin.mispermisos_view_tvocacion', login_url='/admin/')
def vocaciones(request):
    vocaciones = TVocacion.objects.all()
    return render(request, 'panel_admin/vocaciones/listar.html', {'vocaciones': vocaciones})
@login_required(login_url='login_admin')
@permission_required('panel_admin.mispermisos_add_tvocacion', login_url='/admin/')
def vocaciones_crear(request):
    # nueva vocacion
    if request.method == 'POST':
        vocacion = TVocacion()
        vocacion.nombre_vocacion = request.POST['nombre_vocacion']
        vocacion.estado_vocacion = request.POST['estado_vocacion']
        vocacion.save()
        # retornando con mensaje de exito
        return redirect('vocaciones')
    else:
        return render(request, 'panel_admin/vocaciones/crear.html')
@login_required(login_url='login_admin')
@permission_required('panel_admin.mispermisos_change_tvocacion', login_url='/admin/')
def vocaciones_editar(request, id_vocacion):
    # editar vocacion
    vocacion = TVocacion.objects.get(id_vocacion=id_vocacion)
    if request.method == 'GET':
        return render(request, 'panel_admin/vocaciones/editar.html', {'vocacion': vocacion})
    else:
        vocacion.nombre_vocacion = request.POST['nombre_vocacion']
        vocacion.estado_vocacion = request.POST['estado_vocacion']
        vocacion.save()
        # retornando con mensaje de exito
        return redirect('vocaciones')
@login_required(login_url='login_admin')
@permission_required('panel_admin.mispermisos_delete_tvocacion', login_url='/admin/')
def vocaciones_eliminar(request, id_vocacion):
    # eliminar vocacion
    vocacion = TVocacion.objects.get(id_vocacion=id_vocacion)
    vocacion.delete()
    return redirect('vocaciones')
# End vocaciones

# Begin reportes
@login_required(login_url='login_admin')
def reportes(request):
    # llamando a la vista de reportes
    cursor = connection.cursor()

    #Write the SQL code
    sql_string1 = "SET lc_time_names = 'es_ES'"
    sql_string2 = "select * from v_reportes top limit 10"
    #Execute the SQL
    cursor.execute(sql_string1)
    cursor.execute(sql_string2)
    result =  cursor.fetchall()
    reportes = []
    for row in result:
        reporte = {}
        reporte['mes'] = row[0]
        reporte['colegio'] = row[1]
        reporte['alumnos'] = row[2]
        reporte['m'] = row[3]
        reporte['f'] = row[4]
        reportes.append(reporte)
    #reportes = VReporte.objects.all()
    reporte_grafico = "select * from v_reportes_por_sexo top limit 10"
    cursor.execute(reporte_grafico)
    result_grafico =  cursor.fetchall()
    reportes_grafico = []
    for row in result_grafico:
        reporte_g = {}
        reporte_g['mes'] = row[0]
        reporte_g['alumnos'] = row[1]
        reporte_g['m'] = row[2]
        reporte_g['f'] = row[3]
        reportes_grafico.append(reporte_g)
    print(reportes_grafico)
    list_meses = []
    list_alumnos = []
    for reporte in result_grafico:
        # almacenando el mes de la bd en un array
        list_meses.append(reporte[0])
        list_alumnos.append(reporte[1])
    # quitando la , y [ ] del array
    list_meses = list_meses[::-1]
    list_alumnos = list_alumnos[::-1]
    list_meses =  json.dumps(list_meses).replace('[', '').replace(']', '').replace('"', '')
    list_alumnos =  (json.dumps(list_alumnos).replace('[', '').replace(']', '').replace('"', ''))
    # ultimo mes
    ultimo_mes = list_meses.split(',')[0]
    return render(request, 'panel_admin/reportes/listar.html', {
        'reportes': reportes,
        'list_meses': list_meses,
        'list_alumnos': (list_alumnos),
        'reportes_grafico': reportes_grafico,
        'ultimo_mes': ultimo_mes
        })
# End reportes

# Begin login_admin
def login_admin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active and user.is_staff:
                login(request, user)
                return redirect('index')
            else:
                messages.error(request, 'Usuario no activo')
                return redirect('login_admin')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
            return redirect('login_admin')
    else:
        return render(request, 'panel_admin/auth/login_admin.html')

def logout_admin(request):
    logout(request)
    return redirect('login_admin')
# End login_admin

# Begin usuarios
@login_required(login_url='login_admin')
@permission_required('panel_admin.mispermisos_view_tusuario', login_url='/admin/')
def usuarios(request):
    # llamando a la vista de usuarios
    usuarios = TUsuario.objects.all()
    # obteniedo los permisos del usuario tabla intermedia
    return render(request, 'panel_admin/usuarios/listar.html', {'usuarios': usuarios })
@login_required(login_url='login_admin')
@permission_required('panel_admin.mispermisos_add_tusuario', login_url='/admin/')
def usuarios_crear(request):
    # nuevo usuario
    if request.method == 'POST':
        username_usuario = request.POST['username_usuario']
        password_usuario = request.POST['password_usuario']
        user = User.objects.create_user(username_usuario, '', password_usuario)
        user.is_active = request.POST['estado_usuario']
        user.is_staff = True
        user.save()
        usuario = TUsuario()
        usuario.nombre_usuario = request.POST['nombre_usuario']
        usuario.apellido_usuario = request.POST['apellido_usuario']
        usuario.dni_usuario = request.POST['dni_usuario']
        usuario.estado_usuario = request.POST['estado_usuario']
        usuario.usuario = user
        usuario.save()
        # agreagdo permisos
        id_permisos = []
        for permiso in request.POST.getlist('id_permiso[]'):
            id_permisos.append(permiso)
        usuario.usuario.user_permissions.set(id_permisos)
        # retornando con mensaje de exito
        return redirect('usuarios')
    else:
        permisos = Permission.objects.filter(codename__icontains="mispermisos_").order_by('id')
        return render(request, 'panel_admin/usuarios/crear.html' , {'permisos': permisos})
@login_required(login_url='login_admin')
@permission_required('panel_admin.mispermisos_change_tusuario', login_url='/admin/')
def usuarios_editar(request, id_usuario):
    # editar usuario
    usuario = TUsuario.objects.get(id_usuario=id_usuario)
    if request.method == 'GET':
        permisos = Permission.objects.filter(codename__icontains="mispermisos_")
        user_permisos = usuario.usuario.user_permissions.all()
        return render(request, 'panel_admin/usuarios/editar.html', {'usuario': usuario, 'permisos': permisos, 'user_permisos': user_permisos})
    else:
        usuario.nombre_usuario = request.POST['nombre_usuario']
        usuario.apellido_usuario = request.POST['apellido_usuario']
        usuario.dni_usuario = request.POST['dni_usuario']
        usuario.estado_usuario = request.POST['estado_usuario']
        usuario.save()
        # actualizando usuario
        username_usuario = request.POST['username_usuario']
        password_usuario = request.POST['password_usuario']
        user = User.objects.get(id=usuario.usuario.id)
        user.is_active = request.POST['estado_usuario']
        user.username = username_usuario
        user.set_password(password_usuario)
        user.save()
        # actualizando permisos
        id_permisos = []
        for permiso in request.POST.getlist('id_permiso[]'):
            id_permisos.append(permiso)
        usuario.usuario.user_permissions.set(id_permisos)
        # retornando con mensaje de exito
        return redirect('usuarios')
@login_required(login_url='login_admin')
@permission_required('panel_admin.mispermisos_delete_tusuario', login_url='/admin/')
def usuarios_eliminar(request, id_usuario):
    # eliminar usuario
    usuario = TUsuario.objects.get(id_usuario=id_usuario)
    usuario.delete()
    return redirect('usuarios')
# End usuarios

# Begin manual de usuario
@login_required(login_url='login_admin')
def manual_user(request):
    return render(request, 'panel_admin/manual_user.html')
# End manual de usuario

# Begin manual de doc
@login_required(login_url='login_admin')
def doc(request):
    return render(request, 'panel_admin/documentacion.html')

# End manual de doc

# Begin reporte_general
@login_required(login_url='login_admin')
def reporte_general(request):
    # peticion ajax
    if request.method == 'POST':
        # obteniendo datos
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        # obteniendo datos de la base de datos
        cursor = connection.cursor()

        #Write the SQL code
        sql_string1 = "SET lc_time_names = 'es_ES'"
        sql_string2 = "select * from v_reportes top limit 10"
        #Execute the SQL
        cursor.execute(sql_string1)
        cursor.execute(sql_string2)
        result =  cursor.fetchall()
        reportes = []
        for row in result:
            reporte = {}
            reporte['mes'] = row[0]
            reporte['colegio'] = row[1]
            reporte['alumnos'] = row[2]
            reporte['m'] = row[3]
            reporte['f'] = row[4]
            if fecha_inicio>=reporte['mes'] and fecha_fin<=reporte['mes']:
                reportes.append(reporte)
        # filtrando por fechas
        # retornando datos
        return JsonResponse({'reportes': reportes})