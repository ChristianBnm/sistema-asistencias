import os
from datetime import datetime
from zoneinfo import ZoneInfo
from api.extensions import db, migrate
from api.models import Sesion, Curso, Asistencia, AsistenciaResumen

def obtener_cuatrimestre():
    now = datetime.now()
    año = now.year
    mes = now.month
    nro_cuatrimestre = 1 if mes <= 6 else 2
    return f"{año}_{nro_cuatrimestre}"

# ----------------------------------------------------------------------------------------

def serializar_cursos(results):
    return [{
        'id_inscripcion': curso.id_inscripcion,
        'id_materia': curso.id_materia,
        'nombre_materia': nombre,
        'alumno': curso.alumno,
        'identificacion': curso.identificacion,
        'legajo': curso.legajo,
        'comision': curso.comision,
        'estado_ins': curso.estado_ins,
        'instancia': curso.instancia,
        'fecha_inscripcion': curso.fecha_inscripcion.strftime('%d/%m/%Y %H:%M'),
        'nro_transaccion': curso.nro_transaccion
    } for curso, nombre in results]

# ----------------------------------------------------------------------------------------

def limpiar_sesiones_pasadas():
    hoy = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).date()
    sesiones = Sesion.query.all()
    eliminadas = 0

    for sesion in sesiones:
        if sesion.fecha_hora.date() < hoy:
            # Borrar asistencias
            Asistencia.query.filter_by(id_sesion=sesion.id_sesion).delete()

            # Borrar QR
            nombre_archivo = f"qr_{sesion.id_materia}_{sesion.id_sesion}.png"
            ruta_qr = os.path.join('static', 'qr', nombre_archivo)
            if os.path.exists(ruta_qr):
                os.remove(ruta_qr)

            db.session.delete(sesion)
            eliminadas += 1

    db.session.commit()
    print(f"Limpieza automática: {eliminadas} sesiones antiguas eliminadas.")

# ----------------------------------------------------------------------------------------

def construir_nombre_qr(id_materia, comision, id_sesion):
    safe_comision = comision.replace("/", "-") if comision else "X"
    return f"qr_{id_materia}_{safe_comision}_{id_sesion}.png"

# ----------------------------------------------------------------------------------------

def obtener_detalle_asistencias_sesion(sesion):
    cuatrimestre = obtener_cuatrimestre()

    cursos = Curso.query.filter_by(
        id_materia=sesion.id_materia,
        comision=sesion.comision
    ).all()

    resultado = []
    for curso in cursos:
        tiene_asistencia = Asistencia.query.filter_by(
            id_sesion = sesion.id_sesion,
            id_inscripcion = curso.id_inscripcion
        ).first() is not None

        resumen = AsistenciaResumen.query.filter_by(
            id_materia=curso.id_materia,
            id_inscripcion=curso.id_inscripcion,
            cuatrimestre=cuatrimestre
        ).first()

        total_asistencias = resumen.asistencias if resumen else 0

        resultado.append({
            'alumno': curso.alumno,
            'id_inscripcion': curso.id_inscripcion,
            'tiene_asistencia': tiene_asistencia,
            'total_asistencias': total_asistencias
        })

    return resultado

# ----------------------------------------------------------------------------------------


def limpiar_qrs_static():
    carpeta_qr = os.path.join('static', 'qr')
    if os.path.exists(carpeta_qr):
        for archivo in os.listdir(carpeta_qr):
            if archivo.startswith('qr_') and archivo.endswith('.png'):
                os.remove(os.path.join(carpeta_qr, archivo))
