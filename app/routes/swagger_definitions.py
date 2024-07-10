from flasgger import SwaggerView, Schema, fields

class UsuarioSchema(Schema):
    class Meta:
        type_ = 'object'
        properties = {
            'UsuarioID': fields.Int(dump_only=True),
            'Nombre': fields.Str(required=True),
            'Apellido': fields.Str(required=True),
            'CorreoElectronico': fields.Str(required=True),
            'Telefono': fields.Str(),
            'ImagenPerfil': fields.Str(),
            'PasswordHash': fields.Str(load_only=True, required=True)
        }
