from api.extensions import db
from datetime import datetime
from zoneinfo import ZoneInfo
from pytz import timezone

class Materia(db.Model):
    __tablename__ = 'materias'
    id_materia = db.Column(db.String(50), primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)


class Curso(db.Model):
    __tablename__ = 'cursos'
    id_inscripcion = db.Column(db.Integer, primary_key=True)
    id_materia = db.Column(db.String(50), db.ForeignKey('materias.id_materia'), nullable=False)
    alumno = db.Column(db.String(100), nullable=False)
    identificacion = db.Column(db.String(100), nullable=False)
    legajo = db.Column(db.String(100), nullable=False)
    comision = db.Column(db.String(100), nullable=False)
    estado_ins = db.Column(db.String(50), nullable=False)
    instancia = db.Column(db.String(50), nullable=False)
    fecha_inscripcion = db.Column(db.DateTime, nullable=False)
    nro_transaccion = db.Column(db.String(100), nullable=False)

    materia = db.relationship('Materia', backref='cursos')


class Sesion(db.Model):
    __tablename__ = 'sesiones'
    id_sesion = db.Column(db.Integer, primary_key=True)
    id_materia = db.Column(db.String(10), nullable=False)
    comision = db.Column(db.String(10), nullable=False)
    fecha_hora = db.Column(db.DateTime, nullable=False)
    token_qr = db.Column(db.String(100), nullable=True)
    token_expiracion = db.Column(db.DateTime, nullable=True)


class AsistenciaResumen(db.Model):
    __tablename__ = 'asistencias_resumen'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_materia = db.Column(db.String(50), nullable=False)
    id_inscripcion = db.Column(db.Integer, nullable=False)
    alumno = db.Column(db.String(100), nullable=False)
    cuatrimestre = db.Column(db.String(10), nullable=False)  # Ej: "2025_1"
    asistencias = db.Column(db.Integer, default=0)

    __table_args__ = (
        db.UniqueConstraint('id_materia', 'id_inscripcion', 'cuatrimestre', name='unique_resumen'),
    )


class Asistencia(db.Model):
    __tablename__ = 'asistencias'
    id_asistencia = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_sesion = db.Column(db.Integer, db.ForeignKey('sesiones.id_sesion'), nullable=False)
    id_inscripcion = db.Column(db.Integer, db.ForeignKey('cursos.id_inscripcion'), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")))
    presente = db.Column(db.Boolean, default=True)

    sesion = db.relationship('Sesion', backref='asistencias')
    curso = db.relationship('Curso', backref='asistencias')
