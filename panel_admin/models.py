from django.db import models

# Create your models here.

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import User


class TCarrera(models.Model):
    id_carrera = models.AutoField(primary_key=True)
    nombre_carrera = models.CharField(max_length=100)
    id_vocacion = models.ForeignKey('TVocacion', models.DO_NOTHING, db_column='id_vocacion')
    estado_carrera = models.IntegerField()

    class Meta:
        managed = False
        db_table = 't_carrera'
        permissions = (
            ('mispermisos_view_tcarrera', 'Puede ver las carreras'),
            ('mispermisos_add_tcarrera', 'Puede agregar carreras'),
            ('mispermisos_change_tcarrera', 'Puede editar carreras'),
            ('mispermisos_delete_tcarrera', 'Puede eliminar carreras'),
        )


class TCategoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    imagen_categoria = models.CharField(max_length=450, blank=True, null=True)
    nombre_categoria = models.CharField(max_length=50)
    estado_categoria = models.IntegerField()
    pregunta_categoria = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 't_categoria'
        permissions = (
            ('mispermisos_view_tcategoria', 'Puede ver las categorias'),
            ('mispermisos_add_tcategoria', 'Puede agregar categorias'),
            ('mispermisos_change_tcategoria', 'Puede editar categorias'),
            ('mispermisos_delete_tcategoria', 'Puede eliminar categorias'),
        )


class TColegio(models.Model):
    id_colegio = models.AutoField(primary_key=True)
    codigo_colegio = models.CharField(unique=True, max_length=50)
    nombre_colegio = models.CharField(max_length=50)
    telefono_colegio = models.CharField(max_length=12, blank=True, null=True)
    direccion_colegio = models.CharField(max_length=30, blank=True, null=True)
    logo_colegio = models.ImageField(upload_to='logos_colegio/', blank=True, null=True)
    estado_colegio = models.IntegerField()
    usuario = models.ForeignKey(User, models.DO_NOTHING, db_column='usuario', blank=True, null=True)

    class Meta:
        permissions = (
            ('mispermisos_view_tcolegio', 'Puede ver las colegios'),
            ('mispermisos_add_tcolegio', 'Puede agregar colegios'),
            ('mispermisos_change_tcolegio', 'Puede editar colegios'),
            ('mispermisos_delete_tcolegio', 'Puede eliminar colegios'),
        )

class TAlumno(models.Model):
    id_alumno = models.AutoField(primary_key=True)
    nombre_alumno = models.CharField(max_length=50)
    apellido_alumno = models.CharField(max_length=50)
    dni_alumno = models.CharField(unique=True, max_length=8)
    fecha_nacimiento_alumno = models.DateField()
    grado_alumno = models.IntegerField()
    genero_alumno = models.IntegerField()
    estado_alumno = models.IntegerField()
    id_colegio = models.ForeignKey(TColegio, models.DO_NOTHING, db_column='id_colegio')

    class Meta:
        managed = False
        db_table = 't_alumno'
        permissions = (
            ('mispermisos_view_talumno', 'Puede ver las alumnos'),
            ('mispermisos_add_talumno', 'Puede agregar alumnos'),
            ('mispermisos_change_talumno', 'Puede editar alumnos'),
            ('mispermisos_delete_talumno', 'Puede eliminar alumnos'),
        )

class TComunicado(models.Model):
    id_comunicado = models.AutoField(primary_key=True)
    nombre_comunicado = models.CharField(max_length=50, blank=True, null=True)
    img_comunicado = models.ImageField(upload_to='comunicados', blank=True, null=True)
    fecha_comunicado = models.DateField(blank=True, null=True)
    estado_comunicado = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_comunicado'
        permissions = (
            ('mispermisos_view_tcomunicado', 'Puede ver las comunicados'),
            ('mispermisos_add_tcomunicado', 'Puede agregar comunicados'),
            ('mispermisos_change_tcomunicado', 'Puede editar comunicados'),
            ('mispermisos_delete_tcomunicado', 'Puede eliminar comunicados'),
        )


class TConfiguracion(models.Model):
    id_configuracion = models.AutoField(primary_key=True)
    telefono_configuracion = models.CharField(max_length=12, blank=True, null=True)
    direccion_configuracion = models.CharField(max_length=50, blank=True, null=True)
    correo_configuracion = models.CharField(max_length=50, blank=True, null=True)
    manual_configuracion = models.FileField(upload_to='manual/', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_configuracion'
        permissions = (
            ('mispermisos_view_tconfiguracion', 'Puede ver las configuraciones'),
            ('mispermisos_change_tconfiguracion', 'Puede editar configuraciones'),
        )


class TEncuesta(models.Model):
    id_encuesta = models.AutoField(primary_key=True)
    fecha_encuesta = models.DateField(blank=True, null=True)
    hora_encuesta = models.TimeField(blank=True, null=True)
    id_alumno = models.ForeignKey(TAlumno, models.DO_NOTHING, db_column='id_alumno')
    estado_encuesta = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_encuesta'
        permissions = (
            ('mispermisos_view_tencuesta', 'Puede ver las encuestas'),
            ('mispermisos_add_tencuesta', 'Puede agregar encuestas'),
            ('mispermisos_change_tencuesta', 'Puede editar encuestas'),
            ('mispermisos_delete_tencuesta', 'Puede eliminar encuestas'),
        )


class TPregunta(models.Model):
    id_pregunta = models.AutoField(primary_key=True)
    nombre_pregunta = models.CharField(max_length=50, blank=True, null=True)
    estado_pregunta = models.IntegerField(blank=True, null=True)
    id_vocacion = models.ForeignKey('TVocacion', models.DO_NOTHING, db_column='id_vocacion')
    id_categoria = models.ForeignKey(TCategoria, models.DO_NOTHING, db_column='id_categoria')

    class Meta:
        managed = False
        db_table = 't_pregunta'
        permissions = (
            ('mispermisos_view_tpregunta', 'Puede ver las preguntas'),
            ('mispermisos_add_tpregunta', 'Puede agregar preguntas'),
            ('mispermisos_change_tpregunta', 'Puede editar preguntas'),
            ('mispermisos_delete_tpregunta', 'Puede eliminar preguntas'),
        )


class TRedSocial(models.Model):
    id_red_social = models.AutoField(primary_key=True)
    nombre_red_social = models.CharField(max_length=20, blank=True, null=True)
    url_red_social = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_red_social'


class TRespuesta(models.Model):
    id_respuesta = models.AutoField(primary_key=True)
    valor_respuesta = models.IntegerField()
    id_encuesta = models.ForeignKey(TEncuesta, models.DO_NOTHING, db_column='id_encuesta')
    id_pregunta = models.ForeignKey(TPregunta, models.DO_NOTHING, db_column='id_pregunta')

    class Meta:
        managed = False
        db_table = 't_respuesta'
        permissions = (
            ('mispermisos_view_trespuesta', 'Puede ver las respuestas'),
        )


class TUsuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nombre_usuario = models.CharField(max_length=50)
    apellido_usuario = models.CharField(max_length=50)
    dni_usuario = models.CharField(max_length=8)
    estado_usuario = models.CharField(max_length=100)
    usuario = models.ForeignKey(User, models.DO_NOTHING, db_column='usuario', blank=True, null=True)

    class Meta:
        permissions = (
            ('mispermisos_view_tusuario', 'Puede ver los usuarios'),
            ('mispermisos_add_tusuario', 'Puede agregar usuarios'),
            ('mispermisos_change_tusuario', 'Puede editar usuarios'),
            ('mispermisos_delete_tusuario', 'Puede eliminar usuarios'),
        )


class TVocacion(models.Model):
    id_vocacion = models.AutoField(primary_key=True)
    nombre_vocacion = models.CharField(max_length=100)
    estado_vocacion = models.IntegerField()

    class Meta:
        managed = False
        db_table = 't_vocacion'
        permissions = (
            ('mispermisos_view_tvocacion', 'Puede ver las vocaciones'),
            ('mispermisos_add_tvocacion', 'Puede agregar vocaciones'),
            ('mispermisos_change_tvocacion', 'Puede editar vocaciones'),
            ('mispermisos_delete_tvocacion', 'Puede eliminar vocaciones'),
        )

############################################################################
class TFicha_alumno(models.Model):
    id_ficha_alumno = models.AutoField(primary_key=True)
    fecha_ficha_alumno = models.DateField()
    hora_ficha_alumno = models.TimeField()
    id_alumno = models.ForeignKey(TAlumno, models.DO_NOTHING, db_column='id_alumno')

    class Meta:
        managed = False
        db_table = 't_ficha_alumno'

class TFicha_alumno_detalle(models.Model):
    id_ficha_alumno_detalle = models.AutoField(primary_key=True)
    id_ficha_alumno = models.ForeignKey(TFicha_alumno, models.DO_NOTHING, db_column='id_ficha_alumno')
    id_vocacion = models.ForeignKey(TVocacion, models.DO_NOTHING, db_column='id_vocacion')
    id_carrera = models.ForeignKey(TCarrera, models.DO_NOTHING, db_column='id_carrera')

    class Meta:
        managed = False
        db_table = 't_ficha_alumno_detalle'