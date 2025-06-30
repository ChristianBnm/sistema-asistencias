import os
import qrcode
from datetime import datetime
from zoneinfo import ZoneInfo
from api.main import create_app
from db.database import db
from api.models import Curso, Sesion
from utils.helpers import construir_nombre_qr

BASE_URL = "http://192.168.1.36:5000/registrar_asistencia"
QR_DIR = os.path.join("static", "qr")

app = create_app()

with app.app_context():
    os.makedirs(QR_DIR, exist_ok=True)

    from sqlalchemy import distinct

    comisiones = db.session.query(Curso.id_materia, Curso.comision).filter(Curso.comision != None).distinct().all()

    for id_materia, comision in comisiones:
        # Evitar duplicados si ya existe una sesión para esa combinación
        ya_existe = db.session.query(Sesion).filter_by(id_materia=id_materia, comision=comision).first()
        if ya_existe:
            continue

        sesion = Sesion(
            id_materia=id_materia,
            comision=comision,
            fecha_hora=datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))
        )
        db.session.add(sesion)
        db.session.commit()

        url_qr = f"{BASE_URL}?id_sesion={sesion.id_sesion}"
        img = qrcode.make(url_qr)

        filename = construir_nombre_qr(id_materia, comision, sesion.id_sesion)
        filepath = os.path.join(QR_DIR, filename)
        img.save(filepath)

        print(f"Sesión creada para {id_materia} - Comisión {comision}")
        print(f"Sesión ID: {sesion.id_sesion}")
        print(f"URL QR: {url_qr}")
        print(f"Imagen guardada en: {filepath}")
        print("-" * 75)
