from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text
from . import db

def verify_password(hash, password):
    return check_password_hash(hash, password)


def call_procedure(procedure_name, params):
    conn = db.engine.raw_connection()
    try:
        cursor = conn.cursor()
        cursor.callproc(procedure_name, params)
        result = cursor.fetchall()
        cursor.close()
        conn.commit()
        return result
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()