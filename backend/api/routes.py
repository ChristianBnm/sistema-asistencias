import os
import qrcode
import secrets
from flask import Blueprint, request, jsonify
from api.extensions import db
from api.models import Curso, Materia, Sesion, Asistencia, AsistenciaResumen
from datetime import datetime, timedelta
from utils.helpers import obtener_cuatrimestre, serializar_cursos, construir_nombre_qr
from collections import defaultdict
from zoneinfo import ZoneInfo
from pytz import timezone
from utils.helpers import construir_nombre_qr, obtener_detalle_asistencias_sesion, limpiar_qrs_static  
from flask import send_from_directory, current_app


api_bp = Blueprint('api', __name__)

# ------------------------------------------------------------------------------------

# Mostrar toda la lista del excel como JSON
@api_bp.route('/cursos', methods=['GET'])
def get_cursos():
    results = db.session.query(Curso, Materia.nombre).join(Materia).order_by(Materia.nombre, Curso.alumno).all()

    agrupadas = defaultdict(list)
    for curso, nombre in results:
        agrupadas[nombre].append({
            'id_inscripcion': curso.id_inscripcion,
            'id_materia': curso.id_materia,
            'alumno': curso.alumno,
            'identificacion': curso.identificacion,
            'legajo': curso.legajo,
            'comision': curso.comision,
            'estado_ins': curso.estado_ins,
            'instancia': curso.instancia,
            'fecha_inscripcion': curso.fecha_inscripcion.strftime('%d/%m/%Y %H:%M'),
            'nro_transaccion': curso.nro_transaccion
        })

    response = [{'nombre_materia': materia, 'alumnos': alumnos} for materia, alumnos in agrupadas.items()]
    return jsonify(response)

# ------------------------------------------------------------------------------------

# Mostrar todos los estudiantes de una materia en todas las comisiones (posiblemente este se borre a futuro)
@api_bp.route('/cursos/<id_materia>', methods=['GET'])
def get_curso(id_materia):
    results = db.session.query(Curso, Materia.nombre).join(Materia).filter(Curso.id_materia == id_materia).all()
    if not results:
        return jsonify({'error': 'Inscripciones no encontradas'}), 404

    return jsonify(serializar_cursos(results))

# ------------------------------------------------------------------------------------

# Mostrar estudiantes de una materia y comision especificas 
@api_bp.route('/cursos/por_comision', methods=['GET'])
def get_cursos_por_comision():
    id_materia = request.args.get('id_materia')
    comision = request.args.get('comision')

    if not id_materia or not comision:
        return jsonify({'error': 'Se requieren los par谩metros id_materia y comision'}), 400

    results = (
        db.session.query(Curso, Materia.nombre)
        .join(Materia)
        .filter(Curso.id_materia == id_materia)
        .filter(Curso.comision == comision)
        .order_by(Curso.alumno.asc())
        .all()
    )

    if not results:
        return jsonify({'message': 'No se encontraron inscripciones para esos filtros'}), 404

    return jsonify(serializar_cursos(results))


from collections import defaultdict
from flask import jsonify

# ------------------------------------------------------------------------------------

# Listar todas las materias 
@api_bp.route('/materias', methods=['GET'])
def get_materias_y_comisiones():
    results = db.session.query(Curso.id_materia, Materia.nombre, Curso.comision)\
        .join(Materia, Curso.id_materia == Materia.id_materia).distinct().all()

    materias_dict = {}
    for id_materia, nombre, comision in results:
        if id_materia not in materias_dict:
            materias_dict[id_materia] = {
                'id_materia': id_materia,
                'nombre': nombre,
                'comisiones': []
            }
        if comision not in materias_dict[id_materia]['comisiones']:
            materias_dict[id_materia]['comisiones'].append(comision)

    return jsonify(list(materias_dict.values()))

# ------------------------------------------------------------------------------------

# Mostrar nobmre de la materia y comision mediante su ID 
@api_bp.route('/sesiones/<int:id_sesion>/datos_materia', methods=['GET'])
def datos_materia_sesion(id_sesion):
    sesion = Sesion.query.get_or_404(id_sesion)
    materia = Materia.query.get_or_404(sesion.id_materia)

    return jsonify({
        'id_materia': sesion.id_materia,
        'nombre_materia': materia.nombre,
        'comision': sesion.comision
    })

# ------------------------------------------------------------------------------------

# Crear curso (posiblemente no se use y tambien se tenga que borrar este endpoint)
@api_bp.route('/cursos', methods=['POST'])
def add_curso():
    data = request.get_json()
    required_fields = [
        'id_materia', 'alumno', 'identificacion', 'legajo',
        'comision', 'estado_ins', 'instancia', 'fecha_inscripcion',
        'nro_transaccion'
    ]
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Todos los campos son requeridos'}), 400

    curso = Curso(
        id_materia=data['id_materia'],
        alumno=data['alumno'],
        identificacion=data['identificacion'],
        legajo=data['legajo'],
        comision=data['comision'],
        estado_ins=data['estado_ins'],
        instancia=data['instancia'],
        fecha_inscripcion=datetime.fromisoformat(data['fecha_inscripcion']),
        nro_transaccion=data['nro_transaccion']
    )

    db.session.add(curso)
    db.session.commit()

    return jsonify({'message': 'Inscripci贸n registrada', 'id_inscripcion': curso.id_inscripcion}), 201

# ------------------------------------------------------------------------------------

# Crear sesion 
@api_bp.route('/sesiones', methods=['POST'])
def crear_sesion():
    data = request.get_json()
    if not data or 'id_materia' not in data or 'comision' not in data:
        return jsonify({'error': 'Faltan los campos "id_materia" y/o "comision"'}), 400

    ahora = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).date()

    # 馃Ч Verificar si ya hay una sesi贸n con esa materia y comisi贸n HOY y eliminarla
    sesion_existente = Sesion.query.filter_by(
        id_materia=data['id_materia'],
        comision=data['comision']
    ).filter(Sesion.fecha_hora >= datetime.combine(ahora, datetime.min.time()))
    sesion_existente = sesion_existente.first()

    if sesion_existente:
        # Borrar asistencias relacionadas
        Asistencia.query.filter_by(id_sesion=sesion_existente.id_sesion).delete()

        # Eliminar QR anterior si existe
        nombre_archivo = construir_nombre_qr(sesion_existente.id_materia, sesion_existente.comision, sesion_existente.id_sesion)
        ruta_qr = os.path.join('static', 'qr', nombre_archivo)
        if os.path.exists(ruta_qr):
            os.remove(ruta_qr)

        db.session.delete(sesion_existente)
        db.session.commit()

    # Crear nueva sesi贸n
    nueva_sesion = Sesion(
        id_materia=data['id_materia'],
        comision=data['comision'],
        fecha_hora=datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))
    )

    # Token
    token_qr = secrets.token_urlsafe(16)
    token_expiracion = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")) + timedelta(seconds=45)

    nueva_sesion.token_qr = token_qr
    nueva_sesion.token_expiracion = token_expiracion

    db.session.add(nueva_sesion)
    db.session.commit()

    # Generar nombre de archivo QR
    nombre_archivo = construir_nombre_qr(nueva_sesion.id_materia, nueva_sesion.comision, nueva_sesion.id_sesion)
    ruta_qr = os.path.join('static', 'qr', nombre_archivo)

    frontend_host = os.getenv("FRONTEND_URL", "http://localhost:3000")
    contenido_qr = f"{frontend_host}/registro-qr?id_sesion={nueva_sesion.id_sesion}&token={token_qr}"

    # Crear QR y guardar
    qr_img = qrcode.make(contenido_qr)
    os.makedirs(os.path.dirname(ruta_qr), exist_ok=True)
    qr_img.save(ruta_qr)

    return jsonify({
    'message': 'Sesi贸n creada y QR generado',
    'id_sesion': nueva_sesion.id_sesion,
    'url_qr': contenido_qr  # Devuelve la URL completa del QR
}), 201


# ------------------------------------------------------------------------------------

# Registrar una asistencia mediante el id_inscripcion del estudiante 
@api_bp.route('/asistencias', methods=['POST'])
def registrar_asistencia():
    data = request.get_json()
    required = ['id_sesion', 'id_inscripcion', 'token']

    if not all(k in data for k in required):
        return jsonify({'error': 'Faltan campos obligatorios'}), 400

    sesion = Sesion.query.get(data['id_sesion'])
    if not sesion:
        return jsonify({'error': 'Sesi贸n no encontrada'}), 404

    # 馃敀 Validar token del QR
    if data['token'] != sesion.token_qr:
        return jsonify({'error': 'Token inv谩lido'}), 403

    zona_arg = ZoneInfo("America/Argentina/Buenos_Aires")
    ahora = datetime.now(zona_arg)

    # Corregir token_expiracion para que tenga zona horaria
    if sesion.token_expiracion.tzinfo is None:
        sesion.token_expiracion = sesion.token_expiracion.replace(tzinfo=zona_arg)

    if ahora > sesion.token_expiracion:
        return jsonify({'error': 'Token expirado'}), 403

    curso = Curso.query.get(data['id_inscripcion'])
    if not curso:
        return jsonify({'error': 'Inscripci贸n (curso) no encontrada'}), 404

    # Validar que la inscripci贸n pertenezca a la misma materia y comisi贸n que la sesi贸n
    if curso.id_materia != sesion.id_materia or curso.comision != sesion.comision:
        return jsonify({'error': 'La inscripci贸n no corresponde a la materia o comisi贸n de la sesi贸n'}), 400

    # Verificar si ya existe la asistencia para esta sesi贸n y alumno
    existe = Asistencia.query.filter_by(
        id_sesion=data['id_sesion'],
        id_inscripcion=data['id_inscripcion']
    ).first()

    if existe:
        return jsonify({'error': 'Asistencia ya registrada para esta sesi贸n'}), 400

    # Crear la asistencia
    asistencia = Asistencia(
        id_sesion=data['id_sesion'],
        id_inscripcion=data['id_inscripcion'],
        presente=True
    )
    db.session.add(asistencia)

    # Obtener cuatrimestre y actualizar resumen
    cuatrimestre = obtener_cuatrimestre()

    resumen = AsistenciaResumen.query.filter_by(
        id_materia = curso.id_materia,
        id_inscripcion = curso.id_inscripcion,
        cuatrimestre = cuatrimestre
    ).first()

    if resumen:
        resumen.asistencias += 1
    else:
        resumen = AsistenciaResumen(
            id_materia = curso.id_materia,
            id_inscripcion = curso.id_inscripcion,
            alumno = curso.alumno,
            cuatrimestre = cuatrimestre,
            asistencias = 1
        )
        db.session.add(resumen)

    sesion.token_expiracion = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))  # Bloquear el token si la registracion fue exitosa. 
    db.session.commit()

    return jsonify({'message': 'Asistencia registrada correctamente'}), 201


# ------------------------------------------------------------------------------------

# Obtener las asistencias de una sesion mediante su ID
@api_bp.route('/asistencias/sesion/<int:id_sesion>', methods=['GET'])
def get_asistencias_sesion(id_sesion):
    asistencias = Asistencia.query.filter_by(id_sesion=id_sesion).all()
    zona_arg = ZoneInfo("America/Argentina/Buenos_Aires")

    return jsonify([{
        'id_asistencia': a.id_asistencia,
        'id_inscripcion': a.id_inscripcion,
        'alumno': a.curso.alumno,
        'presente': a.presente,
        'timestamp': a.timestamp.astimezone(zona_arg).strftime('%d/%m/%Y %H:%M')
    } for a in asistencias])


# ------------------------------------------------------------------------------------

# Endpoint para obtener la direccion del QR
@api_bp.route('/qr/<path:filename>')
def servir_qr(filename):
    qr_folder = os.path.join(os.path.dirname(__file__), '..', 'static', 'qr')
    return send_from_directory(qr_folder, filename)

# ------------------------------------------------------------------------------------

# Borrar una sesion mediante su id
@api_bp.route('/sesiones/<int:id_sesion>', methods=['DELETE'])
def eliminar_sesion(id_sesion):
    sesion = Sesion.query.get(id_sesion)
    if not sesion:
        return jsonify({'error': 'Sesi贸n no encontrada'}), 404

    Asistencia.query.filter_by(id_sesion=id_sesion).delete()

    nombre_archivo = construir_nombre_qr(sesion.id_materia, sesion.comision, sesion.id_sesion)
    ruta_qr = os.path.join('static', 'qr', nombre_archivo)
    if os.path.exists(ruta_qr):
        os.remove(ruta_qr)

    db.session.delete(sesion)
    db.session.commit()
    return jsonify({'message': f'Sesi贸n {id_sesion} y QR eliminado'}), 200

# ------------------------------------------------------------------------------------

# Borrar todas las sesiones activas (desarrollo, esto a futuro deberia ser automatico)
@api_bp.route('/dev/limpiar_sesiones', methods=['DELETE'])
def dev_limpiar_sesiones():
    try:
        sesiones = Sesion.query.all()
        eliminadas = 0

        for sesion in sesiones:
            Asistencia.query.filter_by(id_sesion=sesion.id_sesion).delete()

            nombre_archivo = construir_nombre_qr(sesion.id_materia, sesion.comision, sesion.id_sesion)
            ruta_qr = os.path.join("static", "qr", nombre_archivo)
            if os.path.exists(ruta_qr):
                os.remove(ruta_qr)

            db.session.delete(sesion)
            eliminadas += 1

        db.session.commit()
        limpiar_qrs_static() 

        return jsonify({
            'message': f'{eliminadas} sesiones eliminadas',
            'status': 'ok'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ------------------------------------------------------------------------------------

# Lista las sesiones existentes 
@api_bp.route('/sesiones/listar', methods=['GET'])
def listar_sesiones():
    sesiones = (
    db.session.query(Sesion, Materia.nombre)
    .join(Materia, Sesion.id_materia == Materia.id_materia)
    .order_by(Sesion.fecha_hora.desc())
    .all()
)

    return jsonify([
    {
        'id_sesion': sesion.id_sesion,
        'id_materia': sesion.id_materia,
        'nombre_materia': nombre,
        'comision': sesion.comision,
        'fecha_hora': sesion.fecha_hora.isoformat()
    } for sesion, nombre in sesiones
])

# ------------------------------------------------------------------------------------

# regenerar token y QR
@api_bp.route('/sesiones/<int:id_sesion>/regenerar_qr', methods=['PUT'])
def regenerar_qr(id_sesion):
    sesion = Sesion.query.get(id_sesion)
    if not sesion:
        return jsonify({'error': 'Sesi贸n no encontrada'}), 404

    # Generar nuevo token y expiraci贸n
    token_qr = secrets.token_urlsafe(16)
    token_expiracion = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")) + timedelta(seconds=45)

    sesion.token_qr = token_qr
    sesion.token_expiracion = token_expiracion
    db.session.commit()

    # Generar nombre de archivo para QR
    nombre_archivo = construir_nombre_qr(sesion.id_materia, sesion.comision, sesion.id_sesion)
    ruta_qr = os.path.join('static', 'qr', nombre_archivo)

    # Usar la IP del frontend desde variable de entorno
    frontend_host = os.getenv("FRONTEND_URL", "http://localhost:3000")
    url_qr = f"{frontend_host}/registro-qr?id_sesion={sesion.id_sesion}&token={token_qr}"

    # Crear el c贸digo QR
    qr_img = qrcode.make(url_qr)
    os.makedirs(os.path.dirname(ruta_qr), exist_ok=True)
    qr_img.save(ruta_qr)

    return jsonify({
        'message': 'QR regenerado correctamente',
        'token': token_qr,
        'url_qr': url_qr,
        'token_expiracion': token_expiracion.isoformat()
    }), 200


# -------------------------------------------------------------------------------------------------

@api_bp.route('/sesiones/<int:id_sesion>/detalle_asistencias', methods=['GET'])
def detalle_asistencias_sesion(id_sesion):
    sesion = Sesion.query.get(id_sesion)
    if not sesion:
        return jsonify({'error': 'Sesi贸n no encontrada'}), 404

    data = obtener_detalle_asistencias_sesion(sesion)
    return jsonify(data)
