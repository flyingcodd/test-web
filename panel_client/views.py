from datetime import datetime
import http
from http.client import HTTPResponse
import json
from re import S
from tkinter import Canvas
from urllib import response
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required

from panel_admin.models import TColegio, TAlumno, TEncuesta, TPregunta, TRespuesta, TVocacion, TCarrera, TComunicado

from django.db import connection
# variables globales

# Create your views here.
def index(request):
    comunicados = TComunicado.objects.all().order_by('-id_comunicado')
    if comunicados is not None:
        ids_comunicados = []
        for comunicado in comunicados:
            ids_comunicados.append(comunicado.id_comunicado)
        
        return render(request, 'panel_client/index.html', {'comunicados': comunicados, 'ids_comunicados': ids_comunicados})
    else:
        return render(request, 'panel_client/index.html')

def iniciar_seccion(request):
    if request.method == 'POST':
        username_colegio = request.POST.get('username')
        password_colegio = request.POST.get('password')
        dni_alumno = request.POST.get('dni_alumno')
        user = authenticate(username=username_colegio, password=password_colegio)
        if user is not None:
            login(request, user)
            # Guardar el CORREO en la variable de sesión
            colegio = TColegio.objects.get(usuario=user.id)
            request.session['nombreColegio'] = colegio.nombre_colegio
            request.session['idColegio'] = colegio.id_colegio
            request.session['dniAlumno'] = dni_alumno
            # Verificar si el alumno existe
            if TAlumno.objects.filter(dni_alumno=dni_alumno).exists():
                request.session['idAlumno'] = TAlumno.objects.get(dni_alumno=dni_alumno).id_alumno
                request.session['nombreAlumno'] = TAlumno.objects.get(dni_alumno=dni_alumno).nombre_alumno + ', ' + TAlumno.objects.get(dni_alumno=dni_alumno).apellido_alumno
                if TEncuesta.objects.filter(id_alumno=request.session['idAlumno']).exists():
                    id_encuesta=TEncuesta.objects.get(id_alumno=request.session['idAlumno']).id_encuesta
                    id_ultima_respuesta = TRespuesta.objects.filter(id_encuesta=id_encuesta).order_by('-id_pregunta')[0]
                    id_ultima_pregunta = id_ultima_respuesta.id_pregunta.id_pregunta
                    if id_ultima_pregunta == TPregunta.objects.all().order_by('-id_pregunta')[0].id_pregunta:
                        # actualizar el estado de la encuesta
                        encuesta = TEncuesta.objects.get(id_alumno=request.session['idAlumno'])
                        encuesta.estado_encuesta = 1
                        encuesta.save()
                        return redirect('respuesta')
                    contador_pregunta = TRespuesta.objects.filter(id_encuesta=id_encuesta).count()
                    return redirect('pregunta', id=id_ultima_pregunta,contador_pregunta=contador_pregunta)
                else:
                    primer_id_pregunta = TPregunta.objects.all().first().id_pregunta
                    return redirect('pregunta', id=primer_id_pregunta,contador_pregunta=1)
            else:
                return redirect('registro')
        else:
            return render(request, 'panel_client/login/iniciar_seccion.html', {'error': 'Usuario o contraseña incorrectos'})
    else:
        # Verificar si el usuario ya inicio sesión
        if request.user.is_authenticated:
            return redirect('registro')
        else:
            return render(request, 'panel_client/login/iniciar_seccion.html')

def cerrar_seccion(request):
    logout(request)
    return redirect('iniciar_seccion')


@login_required
def registro(request):
    if request.method == 'POST':
        id_colegio = request.session.get('idColegio')
        alumno = TAlumno()
        alumno.nombre_alumno = request.POST['nombre_alumno']
        alumno.apellido_alumno = request.POST['apellido_alumno']
        alumno.dni_alumno = request.POST['dni_alumno']
        alumno.fecha_nacimiento_alumno = request.POST['fecha_nacimiento_alumno']
        alumno.genero_alumno = request.POST['genero_alumno']
        alumno.grado_alumno = request.POST['grado_alumno']
        alumno.estado_alumno = '1'
        alumno.id_colegio = TColegio.objects.get(id_colegio=id_colegio)
        alumno.save()
        # retornando con mensaje de exito
        request.session['idAlumno'] = alumno.id_alumno
        request.session['nombreAlumno'] = alumno.nombre_alumno + ', ' + alumno.apellido_alumno
        primer_id_pregunta = TPregunta.objects.all().first().id_pregunta
        return redirect('pregunta', id=primer_id_pregunta, contador_pregunta=1)
    else:
        # Verificar si el alumno ya se registro
        dni_alumno = request.session.get('dniAlumno')
        if TAlumno.objects.filter(dni_alumno=dni_alumno).exists():

                
                if TEncuesta.objects.filter(id_alumno=request.session['idAlumno']).exists():
                    id_encuesta=TEncuesta.objects.get(id_alumno=request.session['idAlumno']).id_encuesta
                    id_ultima_respuesta = TRespuesta.objects.filter(id_encuesta=id_encuesta).order_by('-id_pregunta')[0]
                    id_ultima_pregunta = id_ultima_respuesta.id_pregunta.id_pregunta
                    if id_ultima_pregunta == TPregunta.objects.all().order_by('-id_pregunta')[0].id_pregunta:
                        encuesta = TEncuesta.objects.get(id_alumno=request.session['idAlumno'])
                        encuesta.estado_encuesta = 1
                        encuesta.save()
                        return redirect('respuesta')
                    contador_pregunta = TRespuesta.objects.filter(id_encuesta=id_encuesta).count()
                    return redirect('pregunta', id=id_ultima_pregunta,contador_pregunta=contador_pregunta)
                else:
                    primer_id_pregunta = TPregunta.objects.all().first().id_pregunta
                    return redirect('pregunta', id=primer_id_pregunta,contador_pregunta=1)

        else:
            return render(request, 'panel_client/login/registro.html')


@login_required
def preguntas(request, id, contador_pregunta=0):
    # verificar si existe la pregunta
    if request.method == 'POST':
        id_alumno = request.session.get('idAlumno')
        if TEncuesta.objects.filter(id_alumno=id_alumno).exists():
            id_encuesta = TEncuesta.objects.get(id_alumno=id_alumno).id_encuesta
            # Verificar si la pregunta existe
        else :
            # fecha actual formato: 2020-05-05
            fecha_actual = datetime.now().strftime('%Y-%m-%d')
            # hora actual formato: 12:00:00
            hora_actual = datetime.now().strftime('%H:%M:%S')
            encuesta = TEncuesta()
            encuesta.fecha_encuesta = fecha_actual
            encuesta.hora_encuesta = hora_actual
            encuesta.id_alumno = TAlumno.objects.get(id_alumno=id_alumno)
            encuesta.estado_encuesta = '0'
            encuesta.save()
            id_encuesta = encuesta.id_encuesta
            
        id_siguiente = id + 1
        contador = 0
        cantidad_preguntas = TPregunta.objects.all().count()
        while True:
            contador += 1
            if TPregunta.objects.filter(id_pregunta=id_siguiente).exists():
                break
            elif contador == cantidad_preguntas:
                if TRespuesta.objects.filter(id_pregunta = id, id_encuesta=id_encuesta).exists():
                    respuesta = TRespuesta.objects.get(id_pregunta = id, id_encuesta=id_encuesta)
                    # actualizar respuesta
                    respuesta.valor_respuesta = request.POST['option']
                    respuesta.save()
                    encuesta = TEncuesta.objects.get(id_alumno=request.session['idAlumno'])
                    encuesta.estado_encuesta = 1
                    encuesta.save()
                    return redirect('respuesta')
                else :
                    # Guardar las respuestas
                    respuesta = TRespuesta()
                    respuesta.valor_respuesta = request.POST['option']
                    respuesta.id_encuesta = TEncuesta.objects.get(id_encuesta=id_encuesta)
                    respuesta.id_pregunta = TPregunta.objects.get(id_pregunta=id)
                    respuesta.save()
                    encuesta = TEncuesta.objects.get(id_alumno=request.session['idAlumno'])
                    encuesta.estado_encuesta = 1
                    encuesta.save()
                    # redirect con parametro id
                    return redirect('respuesta')
            else:
                id_siguiente = id_siguiente + 1
        # cantidad de preguntas
        
        if TRespuesta.objects.filter(id_pregunta = id, id_encuesta=id_encuesta).exists():
            respuesta = TRespuesta.objects.get(id_pregunta = id, id_encuesta=id_encuesta)
            # actualizar respuesta
            respuesta.valor_respuesta = request.POST['option']
            respuesta.save()
        else :
            # Guardar las respuestas
            respuesta = TRespuesta()
            respuesta.valor_respuesta = request.POST['option']
            respuesta.id_encuesta = TEncuesta.objects.get(id_encuesta=id_encuesta)
            respuesta.id_pregunta = TPregunta.objects.get(id_pregunta=id)
            respuesta.save()
        contador_pregunta = contador_pregunta + 1
        # redirect con el id de la siguiente pregunta y ademas enviar el contador
        return redirect('pregunta', id = id_siguiente, contador_pregunta=contador_pregunta)
    else:
        pregunta = TPregunta.objects.get(id_pregunta=id)
        #contador = contador + 1
        cantidad_preguntas = TPregunta.objects.all().count()
        if TEncuesta.objects.filter(id_alumno=request.session.get('idAlumno')).exists():
            id_encuesta = TEncuesta.objects.get(id_alumno=request.session.get('idAlumno')).id_encuesta
            if TRespuesta.objects.filter(id_pregunta=id, id_encuesta=id_encuesta).exists():
                respuesta = TRespuesta.objects.get(id_pregunta=id, id_encuesta=id_encuesta)
                return render(request, 'panel_client/preguntas/preguntas.html', {'pregunta': pregunta, 'respuesta': respuesta,'contador_pregunta':contador_pregunta, 'cantidad_preguntas': cantidad_preguntas})
            else:
                return render(request, 'panel_client/preguntas/preguntas.html', {'pregunta': pregunta,'contador_pregunta':contador_pregunta, 'cantidad_preguntas': cantidad_preguntas})
        else:
            return render(request, 'panel_client/preguntas/preguntas.html', {'pregunta': pregunta})
        
        
@login_required
def respuesta(request):
    dni_alumno = request.session.get('dniAlumno')
    nombreAlumno = TAlumno.objects.get(dni_alumno=dni_alumno).nombre_alumno + ', ' + TAlumno.objects.get(dni_alumno=dni_alumno).apellido_alumno
    # select p.id_vocacion,v.nombre_vocacion,count(r.id_respuesta) as suma from t_respuesta as r
    # inner join t_encuesta as e on e.id_encuesta = r.id_encuesta
    # inner join t_pregunta as p on p.id_pregunta = r.id_pregunta
    # inner join t_vocacion as v on v.id_vocacion = p.id_vocacion
    # where r.valor_respuesta = 1 and e.id_alumno=1
    # group by p.id_vocacion
    # pasar al orm de django
    #tabla = TRespuesta.objects.raw('select p.id_vocacion,v.nombre_vocacion,count(r.id_respuesta) as suma from t_respuesta as r inner join t_encuesta as e on e.id_encuesta = r.id_encuesta inner join t_pregunta as p on p.id_pregunta = r.id_pregunta inner join t_vocacion as v on v.id_vocacion = p.id_vocacion where r.valor_respuesta = 1 and e.id_alumno=%s group by p.id_vocacion', [request.session.get('idAlumno')])[0]
    # imprimir tabla
    #print(tabla)
    # llamar a un procedimiento almacenado
    #pa = TRespuesta.objects.raw('call sp_vocacion(%s)', [request.session.get('idAlumno')])[0]
    c = connection.cursor()
    c.callproc('pa_suma', [request.session.get('idAlumno')])
    tabla = c.fetchall()
    # pasar a un json
    vocaciones = []
    for i in tabla:
        vocaciones.append({
            'id_vocacion': i[0],
            'nombre_vocacion': i[1],
            'suma': i[2]
        })
    # obtner el maximo de la columna suma
    maximo = max(vocaciones, key=lambda x:x['suma'])
    id_vocacion_maximo = maximo['id_vocacion']

    nombreVocacion = TVocacion.objects.get(id_vocacion=id_vocacion_maximo).nombre_vocacion
    id_vocacion = TVocacion.objects.get(id_vocacion=id_vocacion_maximo).id_vocacion
    # carreras de la vocacion random

    carreras = TCarrera.objects.filter(id_vocacion=id_vocacion_maximo).order_by('?')[:3]
    nombreVocacion = nombreVocacion.upper()
    return render(request, 'panel_client/preguntas/respuesta.html', {'nombreAlumno': nombreAlumno, 'nombreVocacion': nombreVocacion, 'carreras': carreras, 'id_vocacion': id_vocacion})


import os
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders



@login_required
def generar_pdf(request, id_vocacion):
    template_path = 'panel_client/pdf.html'
    # Begin::Datos de la tabla
    carreras = TCarrera.objects.filter(id_vocacion=id_vocacion)
    # mayusculas
    nombreVocacion = TVocacion.objects.get(id_vocacion=id_vocacion).nombre_vocacion.upper()
    alumno = TAlumno.objects.get(id_alumno=request.session.get('idAlumno'))
    url_logo = "http://" + request.get_host() + "/static/panel_client_registro/img/logo-ministerio.jpg"
    edad = (datetime.now().year)-(alumno.fecha_nacimiento_alumno.year)
    # End::Datos de la tabla
    context = {
        'carreras': carreras,
        'alumno': alumno,
        'url_logo': url_logo,
        'nombreVocacion': nombreVocacion,
        'edad': edad
        }
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response, link_callback=link_callback)
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('Ocurrio un error interno, comunicarse con la oficina <pre>' + html + '</pre>')
    return HttpResponse(response, content_type='application/pdf')
    
def link_callback(uri, rel):
            """
            Convert HTML URIs to absolute system paths so xhtml2pdf can access those
            resources
            """
            result = finders.find(uri)
            if result:
                    if not isinstance(result, (list, tuple)):
                            result = [result]
                    result = list(os.path.realpath(path) for path in result)
                    path=result[0]
            else:
                    sUrl = settings.STATIC_URL        # Typically /static/
                    sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
                    mUrl = settings.MEDIA_URL         # Typically /media/
                    mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/

                    if uri.startswith(mUrl):
                            path = os.path.join(mRoot, uri.replace(mUrl, ""))
                    elif uri.startswith(sUrl):
                            path = os.path.join(sRoot, uri.replace(sUrl, ""))
                    else:
                            return uri

            # make sure that file exists
            if not os.path.isfile(path):
                    raise Exception(
                            'media URI must start with %s or %s' % (sUrl, mUrl)
                    )
            return path
