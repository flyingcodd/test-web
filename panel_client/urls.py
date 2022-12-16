from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index_client'),
    path('iniciar_seccion/', views.iniciar_seccion, name='iniciar_seccion'),
    path('cerrar_seccion/', views.cerrar_seccion, name='cerrar_seccion'),
    path('registro/', views.registro, name='registro'),
    path('preguntas/<int:id_categoria>/<int:id_pregunta>/<int:contador_pregunta>', views.preguntas, name='pregunta'),
    path('respuesta/', views.respuesta, name='respuesta'),
    path('generar_pdf/<int:id_ficha_alumno>', views.generar_pdf, name='generar_pdf'),

    path('menu_preguntas/', views.menu_preguntas, name='menu_preguntas'),
]