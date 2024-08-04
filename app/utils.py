from werkzeug.security import check_password_hash
from . import db
import mysql.connector
from mysql.connector import Error

def verify_password(hash, password):
    return check_password_hash(hash, password)

def call_procedure(procedure_name, params):
    conn = db.engine.raw_connection()
    try:
        cursor = conn.cursor()
        cursor.callproc(procedure_name, params)
        result = None
        if cursor.description:  
            result = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            result = [dict(zip(columns, row)) for row in result]
        cursor.close()
        conn.commit()
        return result
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def obtener_todas_las_tareas():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='gestioncolaborativa',
            user='root',
            password='micram123'
        )
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.callproc('ObtenerTareas')
            for result in cursor.stored_results():
                tasks = result.fetchall()
            cursor.close()
            connection.close()
            return tasks
    except Error as e:
        print("Error while connecting to MySQL", e)
        return []

def obtener_tarea_por_id(tarea_id):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='gestioncolaborativa',
            user='root',
            password='micram123'
        )
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.callproc('ObtenerTareaPorID', [tarea_id])
            for result in cursor.stored_results():
                task = result.fetchall()
            cursor.close()
            connection.close()
            return task
    except Error as e:
        print("Error while connecting to MySQL", e)
        return []
