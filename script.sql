create database test_db;
use test_db;

create table t_colegio(
id_colegio int primary key auto_increment not null,
codigo_colegio varchar(50) unique not null,
nombre_colegio varchar(50) not null,
telefono_colegio varchar(12),
direccion_colegio varchar(30),
estado_colegio tinyint not null  -- 1=habilitar login // 0=no dar permiso
);

-- insert into t_colegio values(not null, 'C001', 'Majesa', '987654321', 'jr. arica', 'majesa1','majesa1',0);

create table t_alumno(
id_alumno int primary key auto_increment not null,
nombre_alumno varchar(50) not null,
apellido_alumno varchar(50) not null,
dni_alumno varchar(8) not null unique,
fecha_nacimiento_alumno date not null,
grado_alumno int not null,
genero_alumno tinyint,
estado_alumno tinyint not null,
id_colegio int not null,
foreign key (id_colegio) references t_colegio(id_colegio)
 on delete cascade
);
create table t_vocacion(
id_vocacion int primary key auto_increment not null,
nombre_vocacion varchar(100) not null,
estado_vocacion tinyint not null
);
create table t_carrera(
id_carrera int primary key auto_increment not null,
nombre_carrera varchar(100) not null,
id_vocacion int not null,
estado_carrera tinyint not null,
foreign key (id_vocacion) references t_vocacion(id_vocacion)
on delete cascade
);
create table t_categoria(
id_categoria int primary key auto_increment not null,
nombre_categoria varchar(50) not null,
pregunta_categoria varchar(45),
estado_categoria tinyint not null
);
create table t_pregunta(
id_pregunta int primary key auto_increment not null,
nombre_pregunta varchar(150),
id_vocacion int not null,
id_categoria int not null,
foreign key (id_categoria) references t_categoria(id_categoria)
on delete cascade,
foreign key (id_vocacion) references t_vocacion(id_vocacion)
on delete cascade
);

create table t_encuesta(
id_encuesta int primary key auto_increment not null,
fecha_encuesta date,
estado_encuesta tinyint,
hora_encuesta time,
id_alumno int not null,
foreign key (id_alumno) references t_alumno(id_alumno)
on delete cascade
);
create table t_respuesta(
id_respuesta int primary key auto_increment not null,
valor_respuesta int not null,
id_encuesta int not null,
id_pregunta int not null,
foreign key (id_encuesta) references t_encuesta(id_encuesta)
on delete cascade,
foreign key (id_pregunta) references t_pregunta(id_pregunta)
on delete cascade
);

-- tablas generales ----------
create table t_configuracion(
id_configuracion int primary key auto_increment not null,
telefono_configuracion varchar(12),
direccion_configuracion varchar(50),
correo_configuracion varchar(50),
manual_configuracion varchar(100)
);
create table t_red_social(
id_red_social int primary key auto_increment not null,
nombre_red_social varchar(20),
url_red_social varchar(200)
);
create table t_comunicado(
id_comunicado int primary key auto_increment not null,
nombre_comunicado varchar(50),
img_comunicado varchar(100),
fecha_comunicado date,
estado_comunicado boolean
);
create table t_usuario(
id_usuario int primary key auto_increment not null,
nombre_usuario varchar(50) not null,
apellido_usuario varchar(50) not null,
dni_usuario varchar(8) not null,
estado_usuario tinyint not null
);

DELIMITER $$
CREATE PROCEDURE `pa_suma`(
    IN idAlumno int)
BEGIN
    select p.id_vocacion as id,v.nombre_vocacion,count(r.id_respuesta) as suma from t_respuesta as r
	inner join t_encuesta as e on e.id_encuesta = r.id_encuesta
	inner join t_pregunta as p on p.id_pregunta = r.id_pregunta
	inner join t_vocacion as v on v.id_vocacion = p.id_vocacion
	where r.valor_respuesta = 1 and e.id_alumno = idAlumno
	group by p.id_vocacion;
END$$
DELIMITER $$

create view v_reportes
as
	select 
	concat(MONTHNAME(e.fecha_encuesta),'-',YEAR(e.fecha_encuesta)) as 'mes',
	nombre_colegio as 'colegio',count(a.id_alumno) as 'alumnos',
	count( case when a.genero_alumno = 1 then 1 end) as  m,
	count( case when a.genero_alumno = 0 then 1 end) as  f
	from t_alumno as a
	inner join panel_admin_tcolegio as c on c.id_colegio=a.id_colegio
	inner join t_encuesta as e on e.id_alumno=a.id_alumno
	group by concat(MONTHNAME(e.fecha_encuesta),'-',YEAR(e.fecha_encuesta)),c.id_colegio
	order by e.fecha_encuesta desc;

create view v_reportes_por_sexo
as
select 
	concat(MONTHNAME(e.fecha_encuesta),'-',YEAR(e.fecha_encuesta)) as 'mes',
	count(a.id_alumno) as 'alumnos',
	count( case when a.genero_alumno = 1 then 1 end) as  m,
	count( case when a.genero_alumno = 0 then 1 end) as  f
	from t_alumno as a
	inner join panel_admin_tcolegio as c on c.id_colegio=a.id_colegio
	inner join t_encuesta as e on e.id_alumno=a.id_alumno
	group by concat(MONTHNAME(e.fecha_encuesta),'-',YEAR(e.fecha_encuesta))
	order by e.fecha_encuesta desc;
