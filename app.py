import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError 
# Importar la excepción de integridad
from dotenv import load_dotenv

#Cargar las variables de entorno
load_dotenv()

#crear instancia
app =Flask(__name__)
# Configuración de la base de datos PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#Modelo de la base de datos

class Estudiante(db.Model):
    __tablename__ = 'estudiantes'
    no_control = db.Column(db.String, primary_key=True)
    nombre = db.Column(db.String)
    ap_paterno = db.Column(db.String)
    ap_materno = db.Column(db.String)
    semestre = db.Column(db.Integer)

#endpoint para obtener todos los estudiantes

@app.route('/estudiantes', methods=['GET'])
def get_estudiantes():
    estudiantes = Estudiante.query.all()
    lista_estudiantes = []
    for estudiante in estudiantes:
        lista_estudiantes.append({
            'no_control ': estudiante.no_control,
            'nombre ': estudiante.nombre,
            'ap_paterno ': estudiante.ap_paterno,
            'ap_materno ': estudiante.ap_materno,
            'semestre ': estudiante.semestre
            })
        
        return jsonify(lista_estudiantes)
    
@app.route('/estudiantes/<no_control>',methods=['GET'])
def get_estudiante(no_control):
    estudiante = Estudiante.query.get(no_control)
    if estudiante is None:
        
        return jsonify ({'msg':'Estudiante no encontrado'})
    return jsonify({
        'no_control':estudiante.no_control,
        'nombre':estudiante.nombre,
        'ap_paterno':estudiante.ap_paterno,
        'ap_materno':estudiante.ap_materno,
        'semestre':estudiante.semestre,
        })
#eliminar un estudiante
@app.route('/estudiantes/<no_control>',methods=['DELETE'])
def delete_estudiante(no_control):
    estudiante = Estudiante.query.get(no_control)
    
    if estudiante is None:
        return jsonify ({'msg':'Estudiante no encontrado'})
    db.session.delete(estudiante)
    db.session.commit()
    return jsonify({'msg':'Estudiante eliminado correctamente'
    })
#agregar nuevo estudiante

@app.route('/estudiantes',methods=['POST'])
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
            ap_materno = data['ap_materno'],
            semestre = data['semestre'])
        
        db.session.add(nuevo_estudiante)
        db.session.commit()
        
        return jsonify({'msg':'Estudiante agregado correctamente'}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'msg': 'Error: El estudiante ya está inscrito'}), 400
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error inesperado: {str(e)}'}), 500

#actualizar un estudiante

@app.route('/estudiantes/<no_control>',methods=['PATCH'])
def update_estudiante(no_control):
    estudiante = Estudiante.query.get(no_control)
    if estudiante is None:
        return jsonify ({'msg':'Estudiante no encontrado'})
    data = request.get_json()
    
    if "nombre" in data:
        estudiante.nombre = data['nombre']
        if "ap_paterno" in data:
            estudiante.ap_paterno = data['ap_paterno']
            if "ap_materno" in data:
                estudiante.ap_materno = data['ap_materno']
                if "semestre" in data:
                    estudiante.semestre = data['semestre']
                    db.session.commit()
                    return jsonify({'msg':'Estudiante actualizado correctamente'
})
if __name__ == '__main__':
    app.run(debug=True)