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
    app.logger.info(f"Datos recibidos para actualización: {data}")

    if 'CorreoElectronico' in data:
        app.logger.warning("El campo 'CorreoElectronico' está presente en los datos y será eliminado")
        data.pop('CorreoElectronico')

    data.pop('UsuarioID', None)
    data.pop('defaultBoardId', None)

    errors = usuario_schema.validate(data)
    if errors:
        app.logger.error(f"Errores de validación: {errors}")
        return jsonify(errors), 400

    result = call_procedure('ObtenerUsuarioPorID', [id])
    if not result:
        app.logger.error(f"Usuario no encontrado: ID {id}")
        return jsonify({'message': 'Usuario no encontrado'}), 404

    correo_electronico = result[0][3]  # Obtener el correo electrónico actual del usuario
    app.logger.info(f"Correo electrónico actual del usuario: {correo_electronico}")

    app.logger.info(f"Ejecutando procedimiento de actualización con datos: {data}")
    try:
        password_hash = data.get('PasswordHash')
        if password_hash:
            password_hash = generate_password_hash(password_hash)
        else:
            # Si no se está actualizando la contraseña, obtenemos la contraseña actual del usuario
            password_hash = result[0][6] 
        update_data = [
            id,
            data['Nombre'],
            data['Apellido'],
            data.get('Telefono', ''),
            data.get('ImagenPerfil', ''),
            password_hash
        ]
        app.logger.info(f"Datos enviados al procedimiento almacenado ActualizarUsuario: {update_data}")

        call_procedure('ActualizarUsuario', update_data)
        app.logger.info(f"Usuario actualizado exitosamente: ID {id}")
        return jsonify({'message': 'Usuario actualizado exitosamente'}), 200
    except Exception as e:
        app.logger.error(f"Error al actualizar usuario: {str(e)}")
        return jsonify({'message': 'Error al actualizar usuario'}), 500
      
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

    # Paso 1: Actualizar defaultBoardId a NULL
    try:
        call_procedure('ActualizarDefaultBoardId', [id])
        app.logger.info(f"defaultBoardId actualizado a NULL para el usuario ID {id}")
    except Exception as e:
        app.logger.error(f"Error al actualizar defaultBoardId: {str(e)}")
        return jsonify({'message': 'Error al actualizar defaultBoardId'}), 500

    # Paso 2: Eliminar filas dependientes en la tabla `proyectos`
    try:
        call_procedure('EliminarProyectosPorUsuarioID', [id])
        app.logger.info(f"Proyectos asociados con los boards del usuario ID {id} eliminados exitosamente")
    except Exception as e:
        app.logger.error(f"Error al eliminar proyectos: {str(e)}")
        return jsonify({'message': 'Error al eliminar proyectos asociados a los boards del usuario'}), 500

    # Paso 3: Eliminar filas dependientes en la tabla `boards`
    try:
        call_procedure('EliminarBoardsPorUsuarioID', [id])
        app.logger.info(f"Boards asociados con el usuario ID {id} eliminados exitosamente")
    except Exception as e:
        app.logger.error(f"Error al eliminar boards: {str(e)}")
        return jsonify({'message': 'Error al eliminar boards asociados al usuario'}), 500
    
    # Paso 4: Eliminar el usuario
    try:
        call_procedure('EliminarUsuario', [id])
        app.logger.info(f"Usuario ID {id} eliminado exitosamente")
        return '', 204
    except Exception as e:
        app.logger.error(f"Error al eliminar usuario: {str(e)}")
        return jsonify({'message': 'Error al eliminar usuario'}), 500



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

from werkzeug.security import generate_password_hash, check_password_hash

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
    app.logger.info(f"Usuario actualizando contraseña para usuario {id}: {current_user.UsuarioID}")
    data = request.get_json()

    if not data or not data.get('oldPassword') or not data.get('newPassword'):
        app.logger.error(f"Datos insuficientes: {data}")
        return jsonify({'message': 'Datos insuficientes para actualizar la contraseña.'}), 400

    old_password = data.get('oldPassword')
    new_password = data.get('newPassword')

    result = call_procedure('ObtenerUsuarioPorID', [id])
    if not result:
        app.logger.error(f"Usuario no encontrado: ID {id}")
        return jsonify({'message': 'Usuario no encontrado'}), 404

    usuario = result[0]
    stored_password_hash = usuario[6]  # Asume que el índice 6 es el campo PasswordHash

    app.logger.info(f"Hashed password from DB: {stored_password_hash}")
    app.logger.info(f"Old password provided: {old_password}")

    # Verificar la contraseña antigua
    if not check_password_hash(stored_password_hash, old_password):
        app.logger.error("La contraseña actual es incorrecta.")
        return jsonify({'message': 'La contraseña actual es incorrecta.'}), 400

    # Hashear la nueva contraseña usando pbkdf2
    new_password_hash = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=8)
    try:
        call_procedure('ActualizarPasswordUsuario', [id, new_password_hash])
        app.logger.info(f"Contraseña actualizada exitosamente para usuario ID {id}")
        return jsonify({'message': 'Contraseña actualizada exitosamente.'}), 200
    except Exception as e:
        app.logger.error(f"Error al actualizar contraseña: {str(e)}")
        return jsonify({'message': 'Error al actualizar contraseña.'}), 500


