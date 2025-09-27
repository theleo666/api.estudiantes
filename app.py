import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError 
from dotenv import load_dotenv 

# Cargar las variables de entorno (para uso local)
load_dotenv()

# Crear instancia de la aplicación Flask
app = Flask(__name__)

# Configuración de la base de datos PostgreSQL
# Utiliza la variable de entorno DATABASE_URL, que Render inyecta automáticamente.
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de la base de datos
class Estudiante(db.Model):
    __tablename__ = 'estudiantes'
    no_control = db.Column(db.String(20), primary_key=True) # Definir un tamaño para el String
    nombre = db.Column(db.String(100), nullable=False)
    ap_paterno = db.Column(db.String(100), nullable=False)
    ap_materno = db.Column(db.String(100))
    semestre = db.Column(db.Integer, nullable=False)

# =======================================================
# RUTAS DE SERVICIO
# =======================================================

# Ruta de Bienvenida (Soluciona el error 404 en la raíz '/')
@app.route('/', methods=['GET'])
def home():
    """Ruta principal."""
    return "<h1>API de Gestión de Estudiantes Activa</h1><p>Consulta /api/estudiantes o usa POST en /db/setup para inicializar.</p>"

# Ruta para Inicializar la Base de Datos (Crear las tablas)
@app.route('/db/setup', methods=['POST'])
def setup_db():
    """Crea todas las tablas de la base de datos."""
    try:
        # Crea las tablas definidas en db.Model
        with app.app_context():
            db.create_all()
        return jsonify({"mensaje": "Tablas creadas exitosamente."}), 200
    except Exception as e:
        return jsonify({"error": f"Error al crear tablas: {str(e)}"}), 500

# =======================================================
# ENDPOINTS CRUD (RUTAS CON PREFIJO /api)
# =======================================================

# endpoint para obtener todos los estudiantes
@app.route('/api/estudiantes', methods=['GET'])
def get_estudiantes():
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
    return jsonify(lista_estudiantes)

# Obtener un estudiante por no_control
@app.route('/api/estudiantes/<string:no_control>', methods=['GET'])
def get_estudiante(no_control):
    estudiante = Estudiante.query.get(no_control)
    if estudiante is None:
        return jsonify ({'msg':'Estudiante no encontrado'}), 404
    return jsonify({
        'no_control': estudiante.no_control.strip() if estudiante.no_control else None,
        'nombre': estudiante.nombre,
        'ap_paterno': estudiante.ap_paterno,
        'ap_materno': estudiante.ap_materno,
        'semestre': estudiante.semestre,
    })

# Eliminar un estudiante
@app.route('/api/estudiantes/<string:no_control>', methods=['DELETE'])
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
        
        # Validar campos requeridos
        required_fields = ['no_control', 'nombre', 'ap_paterno', 'semestre']
        for field in required_fields:
            if field not in data:
                return jsonify({'msg': f'Error: Falta el campo requerido "{field}"'}), 400
        
        # Primero verificar si el estudiante ya existe
        estudiante_existente = Estudiante.query.get(data['no_control'])
        if estudiante_existente:
            return jsonify({'msg': 'Error: El estudiante ya está inscrito'}), 400
        
        nuevo_estudiante = Estudiante(
            no_control = data['no_control'],
            nombre = data['nombre'],
            ap_paterno = data['ap_paterno'],
            ap_materno = data.get('ap_materno'), # Usa .get por si ap_materno es opcional
            semestre = data['semestre']
        )
        db.session.add(nuevo_estudiante)
        db.session.commit()
        return jsonify({'msg':'Estudiante agregado correctamente'}), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'msg': 'Error: El número de control ya está en uso'}), 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error inesperado: {str(e)}'}), 500
    
# Actualizar un estudiante
@app.route('/api/estudiantes/<string:no_control>', methods=['PATCH'])
def update_estudiante(no_control):
    estudiante = Estudiante.query.get(no_control)
    if estudiante is None:
        return jsonify ({'msg':'Estudiante no encontrado'}), 404
    data = request.get_json()

    if "nombre" in data:
        estudiante.nombre = data['nombre']
    if "ap_paterno" in data:
        estudiante.ap_paterno = data['ap_paterno']
    if "ap_materno" in data:
        estudiante.ap_materno = data['ap_materno']
    if "semestre" in data:
        try:
            estudiante.semestre = int(data['semestre'])
        except ValueError:
             return jsonify({'msg': 'Error: Semestre debe ser un número entero'}), 400

    db.session.commit()
    
    return jsonify({'msg':'Estudiante actualizado correctamente'}), 200
    
if __name__ == '__main__':
    # Ejecuta el servidor solo si se llama directamente (para desarrollo local)
    # En Render, Gunicorn se encarga de la ejecución
    app.run(debug=True)