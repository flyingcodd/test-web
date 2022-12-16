# test-web
Pasos para que puedean ejecutar la app en desarrollo
1. Descargar Xamapp (apache y mysql) e iniciar
2. descargar git (agregar a PATH)
3. Iniciar session en gitHub desde una consola o visual
4. Clonar el proyecto con el sig comando (git clone https://github.com/flyingcodd/test-web.git)
5. EJecutar el script.sql en mysql
6. Ejecutar las migraciones en Django
  6.1 python manage.py makemigrations
  6.2 python manage.py migrate
7. Para correr la app es "py .\manage.py runserver"
