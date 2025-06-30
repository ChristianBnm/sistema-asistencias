import pandas as pd
import re
from api.models import Materia, Curso
from datetime import datetime
from api.extensions import db

RUTA_ARCHIVO = "/app/Inscriptos_a_materias_SIU.xlsx"

def es_fila_materia(celda):
    return bool(re.match(r"\(?PT\d+|\(?TSC\d+|\(?TRL\d+", str(celda)))

def extraer_id_materia(nombre):
    coincidencia = re.search(r"(PT|TSC|TRL)(\d+)", nombre)
    return coincidencia.group(1) + coincidencia.group(2) if coincidencia else None

def limpiar_nombre_materia(nombre):
    nombre = re.sub(r"^\(?(?:PT|TSC|TRL)\d+\)?\s*", "", str(nombre))
    return nombre.strip()

def procesar_excel(ruta_archivo):
    df = pd.read_excel(ruta_archivo, header=None, dtype=str)
    materias = []
    cursos = []
    id_materia_actual = None
    nombre_materia_actual = None
    encabezados_actuales = None

    for _, fila in df.iterrows():
        primera_celda = str(fila[0]).strip()

        if es_fila_materia(primera_celda):
            if id_materia_actual and encabezados_actuales:
                materias.append((id_materia_actual, nombre_materia_actual))
            id_materia_actual = extraer_id_materia(primera_celda)
            nombre_materia_actual = limpiar_nombre_materia(primera_celda)
            encabezados_actuales = None

        elif id_materia_actual and encabezados_actuales is None:
            encabezados_actuales = fila.fillna("").tolist()

        elif id_materia_actual and encabezados_actuales is not None and fila.notna().sum() > 1:
            cursos.append([id_materia_actual] + fila.tolist())

    if id_materia_actual and nombre_materia_actual:
        materias.append((id_materia_actual, nombre_materia_actual))

    df_materias = pd.DataFrame(materias, columns=["id_materia", "nombre"])

    columnas_curso = ["id_materia"] + encabezados_actuales if encabezados_actuales else []
    df_cursos = pd.DataFrame(cursos, columns=columnas_curso)

    # Renombrar columnas para que coincidan con el código
    df_cursos.rename(columns={
        "Alumno": "alumno",
        "Identificación": "identificacion",
        "Legajo": "legajo",
        "Comisión": "comision",
        "Estado Insc.": "estado_ins",
        "Instancia": "instancia",
        "Fecha inscripción": "fecha_inscripcion",
        "Nro de Transacción": "nro_transaccion"
    }, inplace=True)

    # Filtrar cursos sin instancia válida
    if "instancia" in df_cursos.columns:
        df_cursos = df_cursos[df_cursos["instancia"].notna() & (df_cursos["instancia"].str.strip() != "")]

    return df_materias, df_cursos


def importar_datos_desde_df(db):
    print(f"Leyendo archivo Excel desde: {RUTA_ARCHIVO}")
    df_materias, df_cursos = procesar_excel(RUTA_ARCHIVO)

    print(f"Materias detectadas: {len(df_materias)}")
    print(f"Cursos detectados (previo a filtrar): {len(df_cursos)}")

    # Insertar materias
    for _, row in df_materias.iterrows():
        if not db.session.query(Materia).filter_by(id_materia=row['id_materia']).first():
            materia = Materia(
                id_materia=row['id_materia'],
                nombre=row['nombre']
            )
            db.session.add(materia)
    db.session.commit()

    # Insertar cursos
    insertados = 0
    for _, row in df_cursos.iterrows():
        if pd.isna(row.get('alumno')) or pd.isna(row.get('id_materia')) or row.get('alumno') == '':
            print(f"[!] Fila inválida omitida: {row.to_dict()}")
            continue

        with db.session.no_autoflush:
            existe = db.session.query(Curso).filter_by(
                id_materia=row['id_materia'],
                instancia=row.get('instancia')
            ).first()

        if not existe:
            fecha_inscripcion = None
            if row.get('fecha_inscripcion'):
                try:
                    fecha_inscripcion = pd.to_datetime(row['fecha_inscripcion'])
                except Exception as e:
                    print(f"[!] Error parseando fecha: {row['fecha_inscripcion']} - {e}")

            curso = Curso(
                id_materia=row['id_materia'],
                alumno=row['alumno'],
                identificacion=row.get('identificacion', ''),
                legajo=row.get('legajo', ''),
                comision=row.get('comision', ''),
                estado_ins=row.get('estado_ins', ''),
                instancia=row.get('instancia', ''),
                fecha_inscripcion=fecha_inscripcion,
                nro_transaccion=row.get('nro_transaccion', '')
            )
            db.session.add(curso)
            insertados += 1

    db.session.commit()
    print(f"Cursos insertados: {insertados}")
