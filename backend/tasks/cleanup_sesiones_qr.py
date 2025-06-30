import os
import qrcode
from datetime import datetime
from zoneinfo import ZoneInfo

from api.main import create_app
from api.extensions import db
from api.models import Curso, Sesion, Materia  # Asegurate que Curso tenga comisiones cargadas

# URL base para registrar asistencia
BASE_URL = "http://192.168.1.36:5000/registrar_asistencia" # LA IP DEBE SER LA DEL SERVIDOR, ESTO ES PARA PROBAR (DEBERIA ESTAR EN .ENV)

# Carpeta donde se guardan los QR
QR_DIR = os.path.join("static", "qr")

# Crear app Flask
app = create_app()

with app.app_context():
    # Crear carpeta QR si no existe
    os.makedirs(QR_DIR, exist_ok=True)

    # Obtener todas las combinaciones únicas de materia + comisión
    comisiones = db.session.query(Curso.id_materia, Curso.comision).distinct().all()

    if not comisiones:
        print("No se encontraron materias con comisiones.")
        exit()

    for id_materia, comision in comisiones:
        # Crear nueva sesión
        sesion = Sesion(
            id_materia=id_materia,
            comision=comision,
            fecha_hora=datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))
        )
        db.session.add(sesion)
        db.session.commit()

        # Generar URL del QR
        url_qr = f"{BASE_URL}?id_sesion={sesion.id_sesion}"

        # Crear imagen QR
        img = qrcode.make(url_qr)

        # Nombre del archivo con id materia y comisión
        filename = f"qr_{id_materia}_{comision}_{sesion.id_sesion}.png"
        filepath = os.path.join(QR_DIR, filename)
        img.save(filepath)

        # Obtener nombre completo de la materia
        materia = Materia.query.filter_by(id_materia=id_materia).first()
        nombre_materia = materia.nombre if materia else "Materia desconocida"

        # Mostrar información
        print(f"Sesión creada para {nombre_materia} (ID: {id_materia}) - Comisión: {comision}")
        print(f"Sesión ID: {sesion.id_sesion}")
        print(f"URL QR: {url_qr}")
        print(f"Imagen guardada en: {filepath}")
        print("-" * 75)

