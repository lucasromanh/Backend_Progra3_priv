# Backend Integrador

Este es el backend para una aplicación de gestión de trabajo colaborativo similar a Trello, realizada pro Alumnos de la Tecnicatura de Desarrollo de Software de UPATECO.
El equipo formado por Coccocia, Nahuel, Juarez, Raul, Roman, Lucas y Vargas Ariel, llamados "JINJArdigans", para el desarrollo trabajamos con Python, Flask, SQLAlchemy y Flask-SocketIO. El backend proporciona una API REST para manejar usuarios, perfiles, tareas, comentarios, notificaciones, etiquetas y adjuntos.

## Requisitos

- Python 3.7+
- MySQL
- virtualenv

## Instalación

1. Clonar el repositorio:

    ```bash
    git clone https://github.com/lucasromanh/Board
    cd Board
    ```

2. Crear y activar un entorno virtual:

    ```bash
    virtualenv venv
    source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
    ```

3. Instalar las dependencias:

    ```bash
    pip install -r requirements.txt
    ```

4. Configurar la base de datos:

    Crear una base de datos en MySQL. Luego, configura la URI de la base de datos en `config.py`:

    ```python
    class Config:
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://username:password@localhost/GestionColaborativa'
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        SECRET_KEY = 'your_secret_key'
    ```

5. Inicializar la base de datos:

    ```bash
    flask db init
    flask db migrate
    flask db upgrade
    ```

6. Ejecutar la aplicación:

    ```bash
    flask run
    ```

## Rutas de la API

### Usuarios

- `GET /api/usuarios`: Obtener todos los usuarios.
- `GET /api/usuarios/<int:id>`: Obtener un usuario por ID.
- `POST /api/usuarios`: Crear un nuevo usuario.
- `PUT /api/usuarios/<int:id>`: Actualizar un usuario por ID.
- `DELETE /api/usuarios/<int:id>`: Eliminar un usuario por ID.

### Perfiles

- `GET /api/perfiles`: Obtener todos los perfiles.
- `GET /api/perfiles/<int:id>`: Obtener un perfil por ID.
- `POST /api/perfiles`: Crear un nuevo perfil.
- `PUT /api/perfiles/<int:id>`: Actualizar un perfil por ID.
- `DELETE /api/perfiles/<int:id>`: Eliminar un perfil por ID.

### Tareas

- `GET /api/tareas`: Obtener todas las tareas.
- `GET /api/tareas/<int:id>`: Obtener una tarea por ID.
- `POST /api/tareas`: Crear una nueva tarea.
- `PUT /api/tareas/<int:id>`: Actualizar una tarea por ID.
- `DELETE /api/tareas/<int:id>`: Eliminar una tarea por ID.

### Comentarios

- `GET /api/comentarios`: Obtener todos los comentarios.
- `GET /api/comentarios/<int:id>`: Obtener un comentario por ID.
- `POST /api/comentarios`: Crear un nuevo comentario.
- `PUT /api/comentarios/<int:id>`: Actualizar un comentario por ID.
- `DELETE /api/comentarios/<int:id>`: Eliminar un comentario por ID.

### Notificaciones

- `GET /api/notificaciones`: Obtener todas las notificaciones.
- `GET /api/notificaciones/<int:id>`: Obtener una notificación por ID.
- `POST /api/notificaciones`: Crear una nueva notificación.
- `PUT /api/notificaciones/<int:id>`: Actualizar una notificación por ID.
- `DELETE /api/notificaciones/<int:id>`: Eliminar una notificación por ID.

### Etiquetas

- `GET /api/etiquetas`: Obtener todas las etiquetas.
- `GET /api/etiquetas/<int:id>`: Obtener una etiqueta por ID.
- `POST /api/etiquetas`: Crear una nueva etiqueta.
- `PUT /api/etiquetas/<int:id>`: Actualizar una etiqueta por ID.
- `DELETE /api/etiquetas/<int:id>`: Eliminar una etiqueta por ID.
- `POST /api/tareas/<int:tarea_id>/etiquetas`: Añadir una etiqueta a una tarea.
- `DELETE /api/tareas/<int:tarea_id>/etiquetas/<int:etiqueta_id>`: Eliminar una etiqueta de una tarea.

### Adjuntos

- `POST /api/tareas/<int:tarea_id>/adjuntos`: Subir un adjunto a una tarea.
- `GET /api/adjuntos/<int:id>`: Obtener un adjunto por ID.
- `DELETE /api/adjuntos/<int:id>`: Eliminar un adjunto por ID.

## Documentación de la API

La documentación interactiva de la API está disponible en la ruta `/apidocs`. Se ha implementado usando Flasgger.

## Auditoría y Logs de Actividad

La aplicación incluye auditoría y logs de actividad para mantener un registro de cambios y actividades. Estos registros se almacenan en la tabla `AuditLogs`.

## WebSockets para Actualizaciones en Tiempo Real

La aplicación utiliza Flask-SocketIO para permitir actualizaciones en tiempo real en la interfaz de usuario.

## Notificaciones

El sistema de notificaciones alerta a los usuarios sobre eventos importantes. Las notificaciones se almacenan en la tabla `Notificaciones`.

## Comentarios en Tareas

Los usuarios pueden agregar comentarios a las tareas. Los comentarios se gestionan a través de la tabla `Comentarios`.

## Etiquetas y Categorías para Tareas

Las tareas pueden organizarse con etiquetas y categorías para facilitar su gestión. Las etiquetas se gestionan a través de las tablas `Etiquetas` y `Tareas_Etiquetas`.

## Adjuntos en Tareas

Los usuarios pueden adjuntar archivos a las tareas. Los adjuntos se gestionan a través de la tabla `Adjuntos`.

## Pruebas Unitarias y de Integración

Se recomienda implementar pruebas automáticas para asegurar la calidad del código. Las pruebas se pueden realizar utilizando `pytest` o cualquier otro framework de pruebas compatible con Flask.

## Contribuciones

Las contribuciones son bienvenidas. Si deseas contribuir, por favor sigue los siguientes pasos:

1. Haz un fork del repositorio.
2. Crea una nueva rama (`git checkout -b feature/nueva-funcionalidad`).
3. Realiza los cambios y haz commit (`git commit -am 'Añadir nueva funcionalidad'`).
4. Haz push a la rama (`git push origin feature/nueva-funcionalidad`).
5. Abre un Pull Request.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.
