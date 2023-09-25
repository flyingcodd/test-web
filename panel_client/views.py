from datetime import datetime
import http
from http.client import HTTPResponse
###PDF
from django.http import HttpResponse
from django.template.loader import get_template
###PDF
import json
from re import S
from tkinter import Canvas
from urllib import response
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required

from panel_admin.models import TColegio, TAlumno, TEncuesta, TPregunta, TRespuesta, TVocacion, TCarrera, TComunicado,TCategoria,TFicha_alumno,TFicha_alumno_detalle,TConfiguracion

from django.db import connection
from django.contrib import messages
from weasyprint import HTML, CSS
# variables globales

# Create your views here.
def index(request):
    comunicados = TComunicado.objects.filter(estado_comunicado=1).order_by('-id_comunicado')
    if comunicados:
        ids_comunicados = []
        for comunicado in comunicados:
            ids_comunicados.append(comunicado.id_comunicado)
        # obtener datos de configuraciones
        return render(request, 'panel_client/index.html', {'comunicados': comunicados, 'ids_comunicados': ids_comunicados})
    else:
        return render(request, 'panel_client/index.html')

def iniciar_seccion(request):
    if request.method == 'POST':
        username_colegio = request.POST.get('username')
        password_colegio = request.POST.get('password')
        dni_alumno = request.POST.get('dni_alumno')
        user = authenticate(username=username_colegio, password=password_colegio)
        print(user)
        if user is not None and TColegio.objects.filter(usuario=user.id).exists():
            idColegio = TColegio.objects.get(usuario=user.id).id_colegio
            if TColegio.objects.get(usuario=user.id).estado_colegio == 0:
                messages.error(request, 'El colegio se encuentra desactivado')
                return render(request, 'panel_client/login/iniciar_seccion.html')
            if TAlumno.objects.filter(dni_alumno=dni_alumno).exists() and TAlumno.objects.get(dni_alumno=dni_alumno).id_colegio.id_colegio != idColegio:
                messages.error(request, 'El alumno no pertenece a este colegio')
                return render(request, 'panel_client/login/iniciar_seccion.html')
            login(request, user)
                # Guardar el CORREO en la variable de sesión
            colegio = TColegio.objects.get(usuario=user.id)
            request.session['nombreColegio'] = colegio.nombre_colegio
            request.session['logoColegio'] = colegio.logo_colegio.url
            request.session['idColegio'] = colegio.id_colegio
            request.session['dniAlumno'] = dni_alumno
            if TAlumno.objects.filter(dni_alumno=dni_alumno).exists():
                request.session['idAlumno'] = TAlumno.objects.get(dni_alumno=dni_alumno).id_alumno
                request.session['nombreAlumno'] = TAlumno.objects.get(dni_alumno=dni_alumno).nombre_alumno + ', ' + TAlumno.objects.get(dni_alumno=dni_alumno).apellido_alumno
            return redirect('registro')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
            return render(request, 'panel_client/login/iniciar_seccion.html')
    else:
        # Verificar si el usuario ya inicio sesión
        if request.user.is_authenticated and request.user.is_superuser == False and request.user.is_staff == False:
            if TAlumno.objects.filter(dni_alumno=request.session.get('dniAlumno')).exists():
                return redirect('menu_preguntas')
            else:
                return redirect('registro')
        else:
            cerrar_seccion(request)
            return render(request, 'panel_client/login/iniciar_seccion.html')

def cerrar_seccion(request):
    logout(request)
    return redirect('iniciar_seccion')


@login_required
def registro(request):
    check_login_registro(request)
    if request.method == 'POST':
        print(request.POST)
        id_colegio = request.session.get('idColegio')
        alumno = TAlumno()
        alumno.nombre_alumno = request.POST['nombre_alumno']
        alumno.apellido_alumno = request.POST['apellido_alumno']
        alumno.dni_alumno = request.POST['dni_alumno']
        alumno.fecha_nacimiento_alumno = request.POST['fecha_nacimiento_alumno']
        alumno.genero_alumno = request.POST['genero_alumno']
        alumno.grado_alumno = request.POST['grado_alumno']
        alumno.estado_alumno = 1
        alumno.id_colegio = TColegio.objects.get(id_colegio=id_colegio)
        alumno.save()
        # retornando con mensaje de exito
        request.session['idAlumno'] = alumno.id_alumno
        request.session['nombreAlumno'] = alumno.nombre_alumno + ', ' + alumno.apellido_alumno
        dni_alumno = request.session.get('dniAlumno')
        request.session['idAlumno'] = TAlumno.objects.get(dni_alumno=dni_alumno).id_alumno
        return redirect('menu_preguntas')
    else:
        # Verificar si el alumno ya se registro
        dni_alumno = request.session.get('dniAlumno')
        if TAlumno.objects.filter(dni_alumno=dni_alumno).exists():
            messages.success(request, 'Bienvenido ' + TAlumno.objects.get(dni_alumno=dni_alumno).nombre_alumno + ', ' + TAlumno.objects.get(dni_alumno=dni_alumno).apellido_alumno)
            return redirect('menu_preguntas')
        else:
            return render(request, 'panel_client/login/registro.html')


@login_required
def preguntas(request,id_categoria, id_pregunta, contador_pregunta=0):
    check_login_col(request)
    # verificar si existe la pregunta
    if request.method == 'POST':
        id_alumno = request.session.get('idAlumno')
        if TEncuesta.objects.filter(id_alumno=id_alumno).exists():
            id_encuesta = TEncuesta.objects.get(id_alumno=id_alumno).id_encuesta
        else :
            # fecha actual formato: 2020-05-05
            fecha_actual = datetime.now().strftime('%Y-%m-%d')
            # hora actual formato: 12:00:00
            hora_actual = datetime.now().strftime('%H:%M:%S')
            encuesta = TEncuesta()
            encuesta.fecha_encuesta = fecha_actual
            encuesta.hora_encuesta = hora_actual
            encuesta.id_alumno = TAlumno.objects.get(id_alumno=id_alumno)
            encuesta.estado_encuesta = 0
            encuesta.save()
            id_encuesta = encuesta.id_encuesta

        if TRespuesta.objects.filter(id_encuesta=id_encuesta, id_pregunta=id_pregunta).exists():
            respuesta = TRespuesta.objects.get(id_encuesta=id_encuesta, id_pregunta=id_pregunta)
            respuesta.valor_respuesta = request.POST['option']
            respuesta.save()
        else:
            respuesta = TRespuesta()
            respuesta.valor_respuesta = request.POST['option']
            respuesta.id_encuesta = TEncuesta.objects.get(id_encuesta=id_encuesta)
            respuesta.id_pregunta = TPregunta.objects.get(id_pregunta=id_pregunta)
            if TEncuesta.objects.filter(id_encuesta=id_encuesta,estado_encuesta=False).exists():
                respuesta.save()
        # contador_pre
        contador_pregunta = contador_pregunta + 1

        if contador_pregunta == TPregunta.objects.filter(id_categoria=id_categoria,estado_pregunta=True).count():
            return redirect('menu_preguntas')
        else:
            # hallando la id_pregunta siguiente a la actual sin sumar 1
            id_pregunta_siguiente = TPregunta.objects.filter(id_pregunta__gt=id_pregunta, estado_pregunta=True).first().id_pregunta
            # redirect con el id de la siguiente pregunta y ademas enviar el contador
            return redirect('pregunta', id_categoria = id_categoria, id_pregunta=id_pregunta_siguiente, contador_pregunta=contador_pregunta)
    else:
        pregunta = TPregunta.objects.get(id_pregunta=id_pregunta)
        #contador = contador + 1
        cantidad_preguntas_categoria = TPregunta.objects.filter(id_categoria=id_categoria,estado_pregunta=True).count()
        contador_pregunta = contador_pregunta + 0
        id_encuesta = TEncuesta.objects.get(id_alumno=request.session['idAlumno']).id_encuesta
        if TRespuesta.objects.filter(id_pregunta=id_pregunta, id_encuesta=id_encuesta).exists():
            respuesta = TRespuesta.objects.get(id_pregunta=id_pregunta, id_encuesta=id_encuesta)
            return render(request, 'panel_client/preguntas/preguntas.html', {'pregunta': pregunta, 'respuesta': respuesta,'contador_pregunta':contador_pregunta, 'cantidad_preguntas_categoria': cantidad_preguntas_categoria})
        else:
            '''
            if TEncuesta.objects.filter(id_alumno=request.session.get('idAlumno')).exists():
                id_encuesta = TEncuesta.objects.get(id_alumno=request.session.get('idAlumno')).id_encuesta
                if TRespuesta.objects.filter(id_pregunta=id, id_encuesta=id_encuesta).exists():
                    respuesta = TRespuesta.objects.get(id_pregunta=id, id_encuesta=id_encuesta)
                    return render(request, 'panel_client/preguntas/preguntas.html', {'pregunta': pregunta, 'respuesta': respuesta,'contador_pregunta':contador_pregunta, 'cantidad_preguntas': cantidad_preguntas})
                else:
                    return render(request, 'panel_client/preguntas/preguntas.html', {'pregunta': pregunta,'contador_pregunta':contador_pregunta, 'cantidad_preguntas': cantidad_preguntas})
            else:
                return render(request, 'panel_client/preguntas/preguntas.html', {'pregunta': pregunta})'''
            return render(request, 'panel_client/preguntas/preguntas.html', {'pregunta': pregunta, 'contador_pregunta':contador_pregunta, 'cantidad_preguntas_categoria': cantidad_preguntas_categoria})
        
        
@login_required
def respuesta(request):
    check_login_col(request)
    dni_alumno = request.session.get('dniAlumno')
    #nombreAlumno = TAlumno.objects.get(dni_alumno=dni_alumno).nombre_alumno + ', ' + TAlumno.objects.get(dni_alumno=dni_alumno).apellido_alumno
    id_alumno = request.session.get('idAlumno')
    if TFicha_alumno.objects.filter(id_ficha_alumno=id_alumno).exists():
        id_ficha_alumno = TFicha_alumno.objects.get(id_ficha_alumno=id_alumno).id_ficha_alumno
        ficha_alumno_detalle = TFicha_alumno_detalle.objects.filter(id_ficha_alumno=id_ficha_alumno)
        # imprimir solo una vez
        carreras = []
        for i in ficha_alumno_detalle:
            carreras.append(i.id_carrera)
        # eliminar duplicados
        carreras = list(dict.fromkeys(carreras))
        vocaciones = []
        for i in ficha_alumno_detalle:
            vocaciones.append(i.id_vocacion)
        # eliminar duplicados
        vocaciones = list(dict.fromkeys(vocaciones))
        context = {
            'nombre_completo': ficha_alumno_detalle[0].id_ficha_alumno.id_alumno.nombre_alumno + ' ' + ficha_alumno_detalle[0].id_ficha_alumno.id_alumno.apellido_alumno,
            'vocaciones': vocaciones,
            'carreras': carreras,
            'id_ficha_alumno': id_ficha_alumno,
        }
        return render(request, 'panel_client/preguntas/respuesta.html', context)
    else:
        id_vocaciones = []
        id_carreras = []

        ###########################################################
        c = connection.cursor()
        c.callproc('pa_suma', [id_alumno])
        tabla = c.fetchall()
        # pasar a un json
        vocaciones = []
        for i in tabla:
            vocaciones.append({
                'id_vocacion': i[0],
                'nombre_vocacion': i[1],
                'suma': i[2]
            })
        print(vocaciones)
        mayor_vocacion = max(vocaciones, key=lambda x: x['suma'])
        for i in vocaciones:
            if i['suma'] == mayor_vocacion['suma']:
                id_vocaciones.append(i['id_vocacion'])
        vocaciones_carrera = []
        tamaño_vocaciones = len(id_vocaciones)
        for i in id_vocaciones:
            if tamaño_vocaciones == 1:
                id_carreras = list(TCarrera.objects.filter(id_vocacion=i).values_list('id_carrera', flat=True))[:4]
                vocaciones_carrera.append({'id_vocacion': i, 'id_carrera': id_carreras})
            elif tamaño_vocaciones == 2:
                id_carreras = list(TCarrera.objects.filter(id_vocacion=i).values_list('id_carrera', flat=True))[:2]
                vocaciones_carrera.append({'id_vocacion': i, 'id_carrera': id_carreras})
            else:
                id_carreras = list(TCarrera.objects.filter(id_vocacion=i).values_list('id_carrera', flat=True))[:1]
                vocaciones_carrera.append({'id_vocacion': i, 'id_carrera': id_carreras})
        
        ficha_alumno = TFicha_alumno()
        ficha_alumno.id_ficha_alumno = id_alumno
        ficha_alumno.id_alumno = TAlumno.objects.get(id_alumno=id_alumno)
        ficha_alumno.fecha_ficha_alumno = datetime.now().strftime('%Y-%m-%d')
        ficha_alumno.hora_ficha_alumno = datetime.now().strftime('%H:%M:%S')
        ficha_alumno.save()
        for i in vocaciones_carrera:
            for j in i['id_carrera']:
                ficha_alumno_detalle = TFicha_alumno_detalle()
                ficha_alumno_detalle.id_ficha_alumno = TFicha_alumno.objects.get(id_ficha_alumno=id_alumno)
                ficha_alumno_detalle.id_vocacion = TVocacion.objects.get(id_vocacion=i['id_vocacion'])
                ficha_alumno_detalle.id_carrera = TCarrera.objects.get(id_carrera=j)
                ficha_alumno_detalle.save()
        
        return redirect('respuesta')
        ###########################################################


@login_required
def generar_pdf(request, id_ficha_alumno):
    #return render(request, 'panel_client/pdf2.html')
    if request.method == 'GET' and TFicha_alumno.objects.filter(id_ficha_alumno=id_ficha_alumno).exists():
        template = get_template('panel_client/pdf2.html')
        # Begin::Datos de la tabla
        ficha_alumno = TFicha_alumno.objects.get(id_ficha_alumno=id_ficha_alumno)
        ficha_alumno_detalle = TFicha_alumno_detalle.objects.filter(id_ficha_alumno=id_ficha_alumno)
        # imprimir solo una vez
        carreras = []
        for i in ficha_alumno_detalle:
            carreras.append(i.id_carrera)
        # eliminar duplicados
        carreras = list(dict.fromkeys(carreras))
        vocaciones = []
        for i in ficha_alumno_detalle:
            vocaciones.append(i.id_vocacion)
        # eliminar duplicados
        vocaciones = list(dict.fromkeys(vocaciones))
        configuracion = TConfiguracion.objects.first()
        datos_psicologo = {
            'nombre_psicologo': configuracion.datos_psicologo_configuracion.split(',')[0],
            'cargo_psicologo': configuracion.datos_psicologo_configuracion.split(',')[1],
            'firma': 'http://' + request.get_host() + configuracion.img_firma_configuracion.url,
        }
        
        url_logo = "http://" + request.get_host() + "/static/panel_client_registro/img/logo-ministerio.jpg"
        edad = (datetime.now().year)-(ficha_alumno.id_alumno.fecha_nacimiento_alumno.year)
        context = {
            'ficha_alumno': ficha_alumno,
            'vocaciones': vocaciones,
            'carreras': carreras,
            'id_ficha_alumno': id_ficha_alumno,
            'edad': edad,
            'url_logo': url_logo,
            'datos_psicologo': datos_psicologo
        }
        html = template.render(context)
        string = html.encode(encoding="UTF-8")
        # tamaño de una  hoja A4 210mm x 297mm
        pdf = HTML(string=string).write_pdf(stylesheets=[CSS(string='@page { size: A4; margin: 1cm }')])
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'filename="report-{}.pdf"'.format(ficha_alumno.id_alumno.dni_alumno)
        return response
    else:
        messages.error(request, 'No se encontro el registro')
        # retornar el mensaje error
        return HttpResponse('No se encontro la ficha del alumno, El error se puede deber a que el test no existe "falta completar" o fue eliminado')


@login_required
def menu_preguntas(request):
    check_login_col(request)
    if request.method == 'POST':
        categoria = request.POST.get('categoria')
        # convertir en diccionario
        categoria = categoria.replace("'", '"')
        categoria = json.loads(categoria)

        id_pregunta = TPregunta.objects.filter(id_categoria=categoria['id_categoria'])[int(categoria['cantidad_respuestas'])].id_pregunta
        return redirect('pregunta', id_categoria=categoria['id_categoria'], id_pregunta=id_pregunta, contador_pregunta=categoria['cantidad_respuestas'])
    else:
        if TEncuesta.objects.filter(id_alumno=request.session.get('idAlumno')).exists():
            categorias = TCategoria.objects.all()
            id_encuesta = TEncuesta.objects.get(id_alumno=request.session.get('idAlumno')).id_encuesta
            id_alumno = request.session.get('idAlumno')
            boton_activado = False
            if TPregunta.objects.filter(estado_pregunta=True).count() == TRespuesta.objects.filter(id_encuesta=id_encuesta).count() or TEncuesta.objects.filter(id_alumno=id_alumno,estado_encuesta=True).exists():
                boton_activado = True
                # actualizar el estado de la encuesta
                encuesta = TEncuesta.objects.get(id_alumno=id_alumno)
                encuesta.estado_encuesta = 1
                encuesta.save()
            cantidad_preguntas_categoria = []
            for i in categorias:
                cantidad_preguntas_categoria.append({
                    'id_categoria': i.id_categoria,
                    'nombre_categoria': i.nombre_categoria,
                    'imagen_categoria': i.imagen_categoria,
                    'cantidad_preguntas': TPregunta.objects.filter(id_categoria=i.id_categoria,estado_pregunta=True).count(),
                    'cantidad_respuestas': TRespuesta.objects.filter(id_encuesta=id_encuesta, id_pregunta__id_categoria=i.id_categoria).count()
                })
            return render(request, 'panel_client/preguntas/menu-preguntas.html', 
            {
            'cantidad_preguntas_categoria': cantidad_preguntas_categoria, 
            'boton_activado': boton_activado
            })
            
        else:
            id_alumno = request.session.get('idAlumno')
            # fecha actual formato: 2020-05-05
            fecha_actual = datetime.now().strftime('%Y-%m-%d')
            # hora actual formato: 12:00:00
            hora_actual = datetime.now().strftime('%H:%M:%S')
            encuesta = TEncuesta()
            encuesta.fecha_encuesta = fecha_actual
            encuesta.hora_encuesta = hora_actual
            encuesta.id_alumno = TAlumno.objects.get(id_alumno=id_alumno)
            encuesta.estado_encuesta = 0
            encuesta.save()
            id_encuesta = encuesta.id_encuesta
            categorias = TCategoria.objects.all()
            boton_activado = False
            if TPregunta.objects.filter(estado_pregunta=True).count() == TRespuesta.objects.filter(id_encuesta=id_encuesta).count():
                boton_activado = True
                # actualizar el estado de la encuesta
                encuesta = TEncuesta.objects.get(id_alumno=id_alumno)
                encuesta.estado_encuesta = 1
                encuesta.save()
            cantidad_preguntas_categoria = []
            for i in categorias:
                cantidad_preguntas_categoria.append({
                    'id_categoria': i.id_categoria,
                    'nombre_categoria': i.nombre_categoria,
                    'cantidad_preguntas': TPregunta.objects.filter(id_categoria=i.id_categoria,estado_pregunta=True).count(),
                    'cantidad_respuestas': TRespuesta.objects.filter(id_encuesta=id_encuesta, id_pregunta__id_categoria=i.id_categoria).count()
                })
            return render(request, 'panel_client/preguntas/menu-preguntas.html', {'cantidad_preguntas_categoria': cantidad_preguntas_categoria})


### funciones complementarias ###
def check_login_col(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            logout(request)
            return redirect('index_client')
        else:
            # cerrando sesion
            return redirect('menu_preguntas')
    else:
        return redirect('iniciar_seccion')

def check_login_registro(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            logout(request)
            return redirect('index_client')
        else:
            # cerrando sesion
            return redirect('registro')
    else:
        return redirect('iniciar_seccion')