import os
from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError 
from dotenv import load_dotenv

# Cargar las variables de entorno (para uso local)
load_dotenv()

# Crear instancia de la aplicación Flask
app = Flask(__name__)

# Configuración de la base de datos PostgreSQL
# IMPORTANTE: Usamos os.getenv('DATABASE_URL') para Render.
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de la base de datos
class Estudiante(db.Model):
    __tablename__ = 'estudiantes'
    # Definir un tamaño para el String
    no_control = db.Column(db.String(20), primary_key=True) 
    nombre = db.Column(db.String(100))
    ap_paterno = db.Column(db.String(100))
    ap_materno = db.Column(db.String(100))
    semestre = db.Column(db.Integer)

# =======================================================
# RUTA PRINCIPAL (VISUALIZACIÓN JSON)
# =======================================================

@app.route('/', methods=['GET'])
def get_all_estudiantes_json():
    """
    Ruta principal. Devuelve todos los estudiantes en formato JSON.
    Esta ruta reemplaza la visualización HTML.
    """
    try:
        estudiantes = Estudiante.query.all()
        lista_estudiantes = []
        for estudiante in estudiantes:
            lista_estudiantes.append({
                'no_control': estudiante.no_control.strip() if estudiante.no_control else None,
                'nombre': estudiante.nombre,
                'ap_paterno': estudiante.ap_paterno,
                'ap_materno': estudiante.ap_materno,
                'semestre': estudiante.semestre
            })
        
        # Devuelve el listado JSON
        return jsonify(lista_estudiantes) 
        
    except Exception as e:
        # Esto ocurre si la tabla aún no se ha creado
        return jsonify({
            "error": "Error de conexión a la base de datos o tablas no inicializadas.",
            "detalle": str(e),
            "instruccion": "Realiza una petición POST a la ruta /db/setup para crear las tablas."
        }), 500


# Ruta para Inicializar la Base de Datos (Crear las tablas)
@app.route('/db/setup', methods=['POST'])
def setup_db():
    """Crea todas las tablas de la base de datos."""
    try:
        with app.app_context():
            db.create_all()
        return jsonify({"mensaje": "Tablas creadas exitosamente."}), 200
    except Exception as e:
        return jsonify({"error": f"Error al crear tablas: {str(e)}"}), 500

# =======================================================
# ENDPOINTS CRUD (Rutas JSON con prefijo /api)
# =======================================================

# Endpoint para obtener todos los estudiantes (JSON) - Endpoint duplicado para seguir la convención /api
@app.route('/api/estudiantes', methods=['GET'])
def get_estudiantes():
    return get_all_estudiantes_json()


@app.route('/api/estudiantes/<no_control>', methods=['GET'])
def get_estudiante(no_control):
    estudiante = Estudiante.query.get(no_control)
    if estudiante is None:
        return jsonify ({'msg':'Estudiante no encontrado'}), 404
    return jsonify({
        'no_control': estudiante.no_control,
        'nombre': estudiante.nombre,
        'ap_paterno': estudiante.ap_paterno,
        'ap_materno': estudiante.ap_materno,
        'semestre': estudiante.semestre,
    })

# Eliminar un estudiante
@app.route('/api/estudiantes/<no_control>', methods=['DELETE'])
def delete_estudiante(no_control):
    estudiante = Estudiante.query.get(no_control)
    
    if estudiante is None:
        return jsonify ({'msg':'Estudiante no encontrado'}), 404
    db.session.delete(estudiante)
    db.session.commit()
    return jsonify({'msg':'Estudiante eliminado correctamente'}), 200

# Agregar nuevo estudiante
@app.route('/api/estudiantes', methods=['POST'])
def insert_estudiante():
    try:
        data = request.get_json()
        
        # Primero verificar si el estudiante ya existe
        estudiante_existente = Estudiante.query.get(data['no_control'])
        if estudiante_existente:
            return jsonify({'msg': 'Error: El estudiante ya está inscrito'}), 400
        
        nuevo_estudiante = Estudiante(
            no_control = data['no_control'],
            nombre = data['nombre'],
            ap_paterno = data['ap_paterno'],
            ap_materno = data.get('ap_materno'), 
            semestre = data['semestre'])
        
        db.session.add(nuevo_estudiante)
        db.session.commit()
        
        return jsonify({'msg':'Estudiante agregado correctamente'}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'msg': 'Error: El estudiante ya está inscrito (Integrity)'}), 400
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error inesperado o falta de campo: {str(e)}'}), 500

# Actualizar un estudiante
@app.route('/api/estudiantes/<no_control>', methods=['PATCH'])
def update_estudiante(no_control):
    estudiante = Estudiante.query.get(no_control)
    if estudiante is None:
        return jsonify ({'msg':'Estudiante no encontrado'}), 404
    
    data = request.get_json()
    
    # Lógica de actualización
    if "nombre" in data:
        estudiante.nombre = data['nombre']
    if "ap_paterno" in data:
        estudiante.ap_paterno = data['ap_paterno']
    if "ap_materno" in data:
        estudiante.ap_materno = data['ap_materno']
    if "semestre" in data:
        estudiante.semestre = data['semestre']
        
    db.session.commit()
    
    return jsonify({'msg':'Estudiante actualizado correctamente'}), 200

if __name__ == '__main__':
    app.run(debug=True)