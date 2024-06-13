from . import db

USUARIO_ID = 'Usuarios.UsuarioID'
TAREA_ID = 'Tareas.TareaID'

class Usuario(db.Model):
    __tablename__ = 'Usuarios'
    UsuarioID = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(50), nullable=False)
    Apellido = db.Column(db.String(50), nullable=False)
    CorreoElectronico = db.Column(db.String(100), unique=True, nullable=False)
    Telefono = db.Column(db.String(15))
    ImagenPerfil = db.Column(db.String(255))
    PasswordHash = db.Column(db.String(64), nullable=False)

class PerfilUsuario(db.Model):
    __tablename__ = 'PerfilesUsuario'
    PerfilID = db.Column(db.Integer, primary_key=True)
    UsuarioID = db.Column(db.Integer, db.ForeignKey(USUARIO_ID), nullable=False)
    Editable = db.Column(db.Boolean, default=True)
    Biografia = db.Column(db.Text)
    Intereses = db.Column(db.Text)
    Ocupacion = db.Column(db.String(100))

class Invitacion(db.Model):
    __tablename__ = 'Invitaciones'
    InvitacionID = db.Column(db.Integer, primary_key=True)
    UsuarioOrigenID = db.Column(db.Integer, db.ForeignKey(USUARIO_ID), nullable=False)
    UsuarioDestinoID = db.Column(db.Integer, db.ForeignKey(USUARIO_ID), nullable=False)
    Estado = db.Column(db.Enum('pendiente', 'aceptada', 'rechazada'), default='pendiente')
    FechaEnvio = db.Column(db.DateTime, default=db.func.current_timestamp())
    FechaAceptacion = db.Column(db.DateTime)

class Board(db.Model):
    __tablename__ = 'Boards'
    BoardID = db.Column(db.Integer, primary_key=True)
    UsuarioPropietarioID = db.Column(db.Integer, db.ForeignKey(USUARIO_ID), nullable=False)
    Titulo = db.Column(db.String(100), nullable=False)

class Proyecto(db.Model):
    __tablename__ = 'Proyectos'
    ProyectoID = db.Column(db.Integer, primary_key=True)
    BoardID = db.Column(db.Integer, db.ForeignKey('Boards.BoardID'), nullable=False)
    Titulo = db.Column(db.String(100), nullable=False)

class Tarea(db.Model):
    __tablename__ = 'Tareas'
    TareaID = db.Column(db.Integer, primary_key=True)
    ProyectoID = db.Column(db.Integer, db.ForeignKey('Proyectos.ProyectoID'), nullable=False)
    Titulo = db.Column(db.String(100), nullable=False)
    Descripcion = db.Column(db.Text)
    Importancia = db.Column(db.Integer)
    Estado = db.Column(db.Enum('pendiente', 'en_proceso', 'completada'), default='pendiente')
    FechaVencimiento = db.Column(db.Date)
    FechaCreacion = db.Column(db.DateTime, default=db.func.current_timestamp())
    UltimaActualizacion = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class Columna(db.Model):
    __tablename__ = 'Columnas'
    ColumnaID = db.Column(db.Integer, primary_key=True)
    ColumnaNombre = db.Column(db.String(100), nullable=False)
    ProyectoID = db.Column(db.Integer, db.ForeignKey('Proyectos.ProyectoID'), nullable=False)

class TareaColumna(db.Model):
    __tablename__ = 'Tareas_Columnas'
    TareaID = db.Column(db.Integer, db.ForeignKey(TAREA_ID), primary_key=True)
    ColumnaID = db.Column(db.Integer, db.ForeignKey('Columnas.ColumnaID'), primary_key=True)
    Posicion = db.Column(db.Integer, nullable=False)

class AsignacionTarea(db.Model):
    __tablename__ = 'AsignacionesTareas'
    AsignacionID = db.Column(db.Integer, primary_key=True)
    TareaID = db.Column(db.Integer, db.ForeignKey(TAREA_ID), nullable=False)
    UsuarioID = db.Column(db.Integer, db.ForeignKey(USUARIO_ID), nullable=False)

class AuditLog(db.Model):
    __tablename__ = 'AuditLogs'
    LogID = db.Column(db.Integer, primary_key=True)
    UsuarioID = db.Column(db.Integer, db.ForeignKey(USUARIO_ID))
    Accion = db.Column(db.String(100), nullable=False)
    Detalles = db.Column(db.Text)
    Fecha = db.Column(db.DateTime, default=db.func.current_timestamp())

class Notificacion(db.Model):
    __tablename__ = 'Notificaciones'
    NotificacionID = db.Column(db.Integer, primary_key=True)
    UsuarioID = db.Column(db.Integer, db.ForeignKey(USUARIO_ID))
    Mensaje = db.Column(db.String(255), nullable=False)
    Fecha = db.Column(db.DateTime, default=db.func.current_timestamp())
    Leida = db.Column(db.Boolean, default=False)

class Comentario(db.Model):
    __tablename__ = 'Comentarios'
    ComentarioID = db.Column(db.Integer, primary_key=True)
    TareaID = db.Column(db.Integer, db.ForeignKey(TAREA_ID))
    UsuarioID = db.Column(db.Integer, db.ForeignKey(USUARIO_ID))
    Texto = db.Column(db.Text, nullable=False)
    Fecha = db.Column(db.DateTime, default=db.func.current_timestamp())

class Etiqueta(db.Model):
    __tablename__ = 'Etiquetas'
    EtiquetaID = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(50), nullable=False)

class TareaEtiqueta(db.Model):
    __tablename__ = 'Tareas_Etiquetas'
    TareaID = db.Column(db.Integer, db.ForeignKey(TAREA_ID), primary_key=True)
    EtiquetaID = db.Column(db.Integer, db.ForeignKey('Etiquetas.EtiquetaID'), primary_key=True)

class Adjunto(db.Model):
    __tablename__ = 'Adjuntos'
    AdjuntoID = db.Column(db.Integer, primary_key=True)
    TareaID = db.Column(db.Integer, db.ForeignKey(TAREA_ID))
    Archivo = db.Column(db.String(255), nullable=False)
    Fecha = db.Column(db.DateTime, default=db.func.current_timestamp())
