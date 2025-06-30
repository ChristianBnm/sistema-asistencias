from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


""" Este archivo contiene la única instancia de SQLAlchemy que se usara en toda la app"""
db = SQLAlchemy()
migrate = Migrate()