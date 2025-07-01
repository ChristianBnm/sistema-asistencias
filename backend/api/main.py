import os
import time
import sqlalchemy.exc
from flask import Flask
from sqlalchemy import text
from api.extensions import db, migrate
from scripts.importar_datos_excel import importar_datos_desde_df
from api.models import Materia, Curso
from dotenv import load_dotenv
load_dotenv()

def create_app():
    app = Flask(__name__)

    # Configuración de base de datos
    db_url = os.getenv('DATABASE_URL', 'mysql+pymysql://Undav:123456788@db/Undav')
    print(f"DEBUG: DATABASE_URL = {db_url}")
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializamos extensiones
    db.init_app(app)
    migrate.init_app(app, db)

    # Registro de rutas
    from api.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Migraciones solo si no existe la carpeta
    with app.app_context():
        migrations_dir = os.path.join(os.getcwd(), 'migrations')
        if not os.path.exists(migrations_dir):
            try:
                from flask_migrate import init as migrate_init
                migrate_init()
                print("Carpeta 'migrations/' inicializada.")
            except Exception as e:
                print("Error inicializando migraciones:", e)

    # Esperamos a la DB
    with app.app_context():
        max_retries = 20
        retry_delay = 5

        for attempt in range(1, max_retries + 1):
            try:
                db.session.execute(text('SELECT 1'))
                db.create_all()
                print("Conexión a la base de datos exitosa y tablas creadas.")

                materias_vacias = not Materia.query.first()
                cursos_vacios = not Curso.query.first()

                if materias_vacias or cursos_vacios:
                    print("Base de datos incompleta. Importando datos desde Excel...")
                    importar_datos_desde_df(db)
                    print("Importación finalizada.")
                else:
                    print("Datos ya cargados, se omite la importación.")
                    print("Importación finalizada.")
                break
            except sqlalchemy.exc.OperationalError as e:
                print(f"Intento {attempt}/{max_retries}: MySQL no listo aún ({e}). Reintentando en {retry_delay}s...")
                time.sleep(retry_delay)
        else:
            print("No se pudo conectar a la base de datos tras varios intentos.")
            raise RuntimeError("Conexión fallida a la base de datos.")

    return app
