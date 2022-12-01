from django.urls import path
# import panel_admin.views
from panel_admin import views

urlpatterns = [
    path('', views.index, name='index'),
    path('encuestas/', views.encuestas, name='encuestas'),

    path('usuarios', views.usuarios, name='usuarios'),
    path('usuarios/crear', views.usuarios_crear, name='usuarios_crear'),
    path('usuarios/editar/<int:id_usuario>', views.usuarios_editar, name='usuarios_editar'),
    path('usuarios/eliminar/<int:id_usuario>', views.usuarios_eliminar, name='usuarios_eliminar'),

    path('colegios', views.colegios, name='colegios'),
    path('colegios/crear', views.colegios_crear, name='colegios_crear'),
    path('colegios/editar/<int:id_colegio>', views.colegios_editar, name='colegios_editar'),
    path('colegios/eliminar/<int:id_colegio>', views.colegios_eliminar, name='colegios_eliminar'),

    path('alumnos', views.alumnos, name='alumnos'),
    path('alumnos/crear', views.alumnos_crear, name='alumnos_crear'),
    path('alumnos/editar/<int:id_alumno>', views.alumnos_editar, name='alumnos_editar'),
    path('alumnos/eliminar/<int:id_alumno>', views.alumnos_eliminar, name='alumnos_eliminar'),

    path('categorias', views.categorias, name='categorias'),
    path('categorias/crear', views.categorias_crear, name='categorias_crear'),
    path('categorias/editar/<int:id_categoria>', views.categorias_editar, name='categorias_editar'),
    path('categorias/eliminar/<int:id_categoria>', views.categorias_eliminar, name='categorias_eliminar'),

    path('preguntas', views.preguntas, name='preguntas'),
    path('preguntas/crear', views.preguntas_crear, name='preguntas_crear'),
    path('preguntas/editar/<int:id_pregunta>', views.preguntas_editar, name='preguntas_editar'),
    path('preguntas/eliminar/<int:id_pregunta>', views.preguntas_eliminar, name='preguntas_eliminar'),

    path('respuestas', views.respuestas, name='respuestas'),

    path('configuracion', views.configuracion, name='configuracion'),

    path('comunicados', views.comunicados, name='comunicados'),
    path('comunicados/crear', views.comunicados_crear, name='comunicados_crear'),
    path('comunicados/editar/<int:id_comunicado>', views.comunicados_editar, name='comunicados_editar'),
    path('comunicados/eliminar/<int:id_comunicado>', views.comunicados_eliminar, name='comunicados_eliminar'),

    path('carreras', views.carreras, name='carreras'),
    path('carreras/crear', views.carreras_crear, name='carreras_crear'),
    path('carreras/editar/<int:id_carrera>', views.carreras_editar, name='carreras_editar'),
    path('carreras/eliminar/<int:id_carrera>', views.carreras_eliminar, name='carreras_eliminar'),

    path('vocaciones', views.vocaciones, name='vocaciones'),
    path('vocaciones/crear', views.vocaciones_crear, name='vocaciones_crear'),
    path('vocaciones/editar/<int:id_vocacion>', views.vocaciones_editar, name='vocaciones_editar'),
    path('vocaciones/eliminar/<int:id_vocacion>', views.vocaciones_eliminar, name='vocaciones_eliminar'),

    path('reportes', views.reportes, name='reportes'),

    path('login_admin', views.login_admin, name='login_admin'),
    path('logout_admin', views.logout_admin, name='logout_admin'),
    path('manual-user', views.manual_user, name='manual_user'),
    path('doc', views.doc, name='doc'),

    path('reporte_general', views.reporte_general, name='reporte_general'),
]