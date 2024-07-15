from flask import Blueprint, request, jsonify, current_app as app
from flask_cors import CORS
from werkzeug.security import generate_password_hash
from app.models import db, Usuario
from ..utils import call_procedure
from app.routes.auth import token_required
from ..schemas import UsuarioSchema
from ..constants import USER_NOT_FOUND
import jwt
import datetime
import os

usuarios_bp = Blueprint('usuarios', __name__)
CORS(usuarios_bp)  

usuario_schema = UsuarioSchema()
usuarios_schema = UsuarioSchema(many=True)

@usuarios_bp.route('/usuarios', methods=['GET'])
@token_required
def get_usuarios(current_user):
    """
    Obtener todos los usuarios.
    ---
    tags:
      - usuarios
    responses:
      200:
        description: Devuelve un listado de todos los usuarios.
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/Usuario'
    """
    app.logger.info(f"Usuario accediendo a todos los usuarios: {current_user.UsuarioID}")
    result = call_procedure('ObtenerUsuarios', [])
    return jsonify({'usuarios': usuarios_schema.dump(result)}), 200

@usuarios_bp.route('/usuarios/<int:id>', methods=['GET'])
@token_required
def get_usuario(current_user, id):
    """
    Obtener detalles de un usuario específico por su ID.
    ---
    tags:
      - usuarios
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: El ID del usuario a obtener.
    responses:
      200:
        description: Devuelve el usuario especificado.
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Usuario'
      404:
        description: Usuario no encontrado.
    """
    app.logger.info(f"Usuario accediendo a usuario {id}: {current_user.UsuarioID}")
    result = call_procedure('ObtenerUsuarioPorID', [id])
    
    if result:
        app.logger.info(f"Resultado del procedimiento almacenado: {result}")
        usuario = {
            'UsuarioID': result[0][0],
            'Nombre': result[0][1],
            'Apellido': result[0][2],
            'CorreoElectronico': result[0][3],
            'Telefono': result[0][4],
            'ImagenPerfil': result[0][5],
            'PasswordHash': result[0][6],
            'defaultBoardId': result[0][7],
        }
        app.logger.info(f"Datos del usuario: {usuario}")
        return jsonify({'usuario': usuario}), 200
    else:
        return jsonify({'message': USER_NOT_FOUND}), 404

@usuarios_bp.route('/usuarios', methods=['POST'])
def create_usuario():
    """
    Crear un nuevo usuario.
    ---
    tags:
      - usuarios
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              Nombre:
                type: string
                description: Nombre del usuario.
              Apellido:
                type: string
                description: Apellido del usuario.
              CorreoElectronico:
                type: string
                description: Correo electrónico del usuario.
              Password:
                type: string
                description: Contraseña del usuario.
    responses:
      201:
        description: Usuario creado exitosamente.
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                token:
                  type: string
      400:
        description: Entrada inválida.
    """
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No se proporcionaron datos'}), 400

    required_fields = ['Nombre', 'Apellido', 'CorreoElectronico', 'Password']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'{field} es requerido'}), 400

    errors = usuario_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    new_user = Usuario(
        Nombre=data['Nombre'],
        Apellido=data['Apellido'],
        CorreoElectronico=data['CorreoElectronico'],
        PasswordHash=generate_password_hash(data['Password'])
    )

    db.session.add(new_user)
    db.session.commit()

    token = jwt.encode({'UsuarioID': new_user.UsuarioID, 'exp': datetime.datetime.now() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'], algorithm="HS256")
    
    return jsonify({'message': 'Usuario creado exitosamente', 'token': token}), 201

@usuarios_bp.route('/usuarios/<int:id>', methods=['PUT'])
@token_required
def update_usuario(current_user, id):
    """
    Actualizar un usuario.
    ---
    tags:
      - usuarios
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: El ID del usuario a actualizar.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              Nombre:
                type: string
                description: Nombre del usuario.
              Apellido:
                type: string
                description: Apellido del usuario.
              CorreoElectronico:
                type: string
                description: Correo electrónico del usuario.
              Password:
                type: string
                description: Contraseña del usuario.
    responses:
      200:
        description: Usuario actualizado exitosamente.
      400:
        description: Entrada inválida.
      404:
        description: Usuario no encontrado.
    """
    app.logger.info(f"Usuario actualizando usuario {id}: {current_user.UsuarioID}")
    data = request.get_json()
    errors = usuario_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    result = call_procedure('ObtenerUsuarioPorID', [id])
    if not result:
        return jsonify({'message': 'Usuario no encontrado'}), 404
    call_procedure('ActualizarUsuario', [
        id,
        data['Nombre'],
        data['Apellido'],
        data['CorreoElectronico'],
        data.get('Telefono', ''),
        data.get('ImagenPerfil', ''),
        generate_password_hash(data['Password'])
    ])
    return jsonify({'message': 'Usuario actualizado exitosamente'}), 200

@usuarios_bp.route('/usuarios/<int:id>', methods=['DELETE'])
@token_required
def delete_usuario(current_user, id):
    """
    Eliminar un usuario.
    ---
    tags:
      - usuarios
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: El ID del usuario a eliminar.
    responses:
      204:
        description: Usuario eliminado exitosamente.
      404:
        description: Usuario no encontrado.
    """
    app.logger.info(f"Usuario eliminando usuario {id}: {current_user.UsuarioID}")
    result = call_procedure('ObtenerUsuarioPorID', [id])
    if not result:
        return jsonify({'message': 'Usuario no encontrado'}), 404
    call_procedure('EliminarUsuario', [id])
    return '', 204

@usuarios_bp.route('/usuarios/<int:id>/imagen', methods=['POST'])
@token_required
def upload_imagen_usuario(current_user, id):
    """
    Subir una imagen de perfil para un usuario.
    ---
    tags:
      - usuarios
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: El ID del usuario.
      - in: formData
        name: imagen
        type: file
        required: true
        description: El archivo de la imagen a subir.
    responses:
      200:
        description: Imagen de perfil actualizada exitosamente.
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
      400:
        description: Error en la solicitud.
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
    """
    if 'imagen' not in request.files:
        return jsonify({'message': 'No se encontró la imagen en la solicitud'}), 400
    imagen = request.files['imagen']
    if imagen.filename == '':
        return jsonify({'message': 'Nombre de archivo vacío'}), 400
    filename = f'{id}_{imagen.filename}'
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    imagen.save(filepath)
    call_procedure('ActualizarImagenUsuario', [id, filename])
    return jsonify({'message': 'Imagen de perfil actualizada exitosamente'}), 200

@usuarios_bp.route('/usuarios/<int:id>/password', methods=['PUT'])
@token_required
def change_password(current_user, id):
    """
    Cambiar la contraseña de un usuario.
    ---
    tags:
      - usuarios
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: El ID del usuario.
      - in: body
        name: body
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                oldPassword:
                  type: string
                  description: La contraseña actual del usuario.
                newPassword:
                  type: string
                  description: La nueva contraseña para el usuario.
    responses:
      200:
        description: Contraseña actualizada exitosamente.
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
      400:
        description: Error en la solicitud.
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
      404:
        description: Usuario no encontrado.
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
    """
    data = request.get_json()
    old_password = data.get('oldPassword')
    new_password = data.get('newPassword')

    result = call_procedure('ObtenerUsuarioPorID', [id])
    if not result:
        return jsonify({'message': 'Usuario no encontrado'}), 404

    usuario = result[0]
    if not generate_password_hash.check_password_hash(usuario['PasswordHash'], old_password):
        return jsonify({'message': 'La contraseña actual es incorrecta'}), 400

    new_password_hash = generate_password_hash(new_password)
    call_procedure('ActualizarPasswordUsuario', [id, new_password_hash])
    return jsonify({'message': 'Contraseña actualizada exitosamente'}), 200
