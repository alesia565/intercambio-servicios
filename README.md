Backend Intercambio de Servicios

API RESTful desarrollada con Flask para una plataforma de intercambio de servicios entre usuarios. Permite registrar usuarios, autenticar sesiones, publicar servicios, hacer ofertas de intercambio, gestionar perfiles y más.

Tecnologías utilizadas
	•	Backend: Flask
	•	Base de datos: PostgreSQL
	•	ORM: SQLAlchemy
	•	Sesiones: Redis + Flask-Session
	•	Autenticación: Basada en sesiones
	•	Subida de imágenes: werkzeug + rutas protegidas
	•	API REST: JSON

Características principales
	•	Registro e inicio de sesión de usuarios
	•	Gestión de sesiones con Redis
	•	Publicación, edición y eliminación de servicios
	•	Ofertas de intercambio entre usuarios
	•	Perfil de usuario editable con imagen, nombre y descripción
	•	Sistema básico de notificaciones por oferta aceptada

Instalación
	1.	Clona el repositorio:
 ```bash
git clone https://github.com/alesia565/intercambio-servicio-backend.git
cd intercambio-servicio-backend
```
2.	Crea y activa un entorno virtual (opcional pero recomendado):
```bash
python3 -m venv venv
source venv/bin/activate
```
3.	Instala dependencias:
   ```bash
pip install -r requirements.txt
```
4.	Asegúrate de tener PostgreSQL y Redis en funcionamiento.
5.	Ejecuta la app:
   ```bash
flask run
```

Variables de entorno sugeridas

Asegúrate de configurar las siguientes variables:
	•	DATABASE_URL
	•	SECRET_KEY
	•	REDIS_URL o SESSION_REDIS

Estado del proyecto

En desarrollo activo. Próximas funcionalidades previstas:
	•	Notificaciones en tiempo real
	•	Sistema de calificaciones y comentarios
	•	Búsqueda y filtrado de servicios
	•	Moderación de contenido

Autora

Alicia (alesia565) – GitHub
