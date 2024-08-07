from marshmallow import Schema, fields, validate, post_load, validates, ValidationError
from .models import Tarea


class UsuarioSchema(Schema):
    UsuarioID = fields.Int(dump_only=True)
    Nombre = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    Apellido = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    CorreoElectronico = fields.Email(validate=validate.Length(max=100), allow_none=True)
    Telefono = fields.Str(validate=validate.Length(max=15), allow_none=True)
    ImagenPerfil = fields.Str(validate=validate.Length(max=255), allow_none=True)
    PasswordHash = fields.Str(load_only=True, validate=validate.Length(min=6), allow_none=True)
    defaultBoardId = fields.Int(dump_only=True)
    
class PerfilUsuarioSchema(Schema):
    PerfilID = fields.Int(dump_only=True)
    UsuarioID = fields.Int(required=True)
    Editable = fields.Bool()
    Biografia = fields.Str()
    Intereses = fields.Str()
    Ocupacion = fields.Str(validate=validate.Length(max=100))

class InvitacionSchema(Schema):
    InvitacionID = fields.Int(dump_only=True)
    UsuarioOrigenID = fields.Int(required=True)
    UsuarioDestinoID = fields.Int(required=True)
    Estado = fields.Str(required=True, validate=validate.OneOf(['pendiente', 'aceptada', 'rechazada']))
    FechaEnvio = fields.DateTime(dump_only=True)
    FechaAceptacion = fields.DateTime(dump_only=True)

class BoardSchema(Schema):
    BoardID = fields.Int(dump_only=True)
    UsuarioPropietarioID = fields.Int(required=True)
    Titulo = fields.Str(required=True, validate=validate.Length(min=1, max=100))

class ProyectoSchema(Schema):
    ProyectoID = fields.Int(dump_only=True)
    BoardID = fields.Int(required=True)
    Titulo = fields.Str(required=True, validate=validate.Length(min=1, max=100))

class TareaSchema(Schema):
    id = fields.Int(dump_only=True)
    ProyectoID = fields.Int(required=True)
    Titulo = fields.Str(required=True, validate=validate.Length(min=1))
    Descripcion = fields.Str()
    Importancia = fields.Int()
    Estado = fields.Str(validate=validate.OneOf(['pendiente', 'en_proceso', 'completada']))
    FechaVencimiento = fields.Date(allow_none=True)
    labels = fields.List(fields.Str(), missing=[])
    members = fields.List(fields.Str(), missing=[])
    checklists = fields.List(fields.Dict(), missing=[])

    @validates('ProyectoID')
    def validate_proyecto_id(self, value):
        if not isinstance(value, int):
            raise ValidationError('ProyectoID tiene que tener un valor.')

    @post_load
    def create_tarea(self, data, **kwargs):
        return Tarea(**data)

class MiembroSchema(Schema):
    UsuarioID = fields.Int(required=True)

class EtiquetaSchema(Schema):
    Nombre = fields.Str(required=True)

class ChecklistSchema(Schema):
    Titulo = fields.Str(required=True)

class FechaSchema(Schema):
    FechaVencimiento = fields.Date(required=True)

class AdjuntoSchema(Schema):
    Archivo = fields.Str(required=True)

class PortadaSchema(Schema):
    PortadaID = fields.Int(required=True)

class ColumnaSchema(Schema):
    ColumnaID = fields.Int(dump_only=True)
    ProyectoID = fields.Int(required=True)
    ColumnaNombre = fields.Str(required=True, validate=validate.Length(min=1, max=100))

class AsignacionTareaSchema(Schema):
    AsignacionID = fields.Int(dump_only=True)
    TareaID = fields.Int(required=True)
    UsuarioID = fields.Int(required=True)

class AuditLogSchema(Schema):
    LogID = fields.Int(dump_only=True)
    UsuarioID = fields.Int(required=True)
    Accion = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    Detalles = fields.Str()
    Fecha = fields.DateTime(dump_only=True)

class NotificacionSchema(Schema):
    NotificacionID = fields.Int(dump_only=True)
    UsuarioID = fields.Int(required=True)
    Mensaje = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    Fecha = fields.DateTime(dump_only=True)
    Leida = fields.Bool()

class ComentarioSchema(Schema):
    ComentarioID = fields.Int(dump_only=True)
    TareaID = fields.Int(required=True)
    UsuarioID = fields.Int(required=True)
    Texto = fields.Str(required=True, validate=validate.Length(min=1))
    Fecha = fields.DateTime(dump_only=True)

class EtiquetaSchema(Schema):
    EtiquetaID = fields.Int(dump_only=True)
    Nombre = fields.Str(required=True, validate=validate.Length(min=1, max=50))

class TareaEtiquetaSchema(Schema):
    TareaID = fields.Int(required=True)
    EtiquetaID = fields.Int(required=True)

class AdjuntoSchema(Schema):
    AdjuntoID = fields.Int(dump_only=True)
    TareaID = fields.Int(required=True)
    Archivo = fields.Str(required=True, validate=validate.Length(max=255))
    Fecha = fields.DateTime(dump_only=True)

# Nuevos esquemas
class MiembroSchema(Schema):
    UsuarioID = fields.Int(required=True)
    TareaID = fields.Int(required=True)

class ChecklistSchema(Schema):
    id = fields.Int(dump_only=True)
    Titulo = fields.Str(required=True, validate=validate.Length(min=1, max=100))

class FechaSchema(Schema):
    id = fields.Int(dump_only=True)
    FechaVencimiento = fields.Date(required=True)

class PortadaSchema(Schema):
    id = fields.Int(dump_only=True)
    TareaID = fields.Int(required=True)
    PortadaID = fields.Int(required=True)
