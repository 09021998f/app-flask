from __main__ import app #importando la instancia de la aplicación Flask (app) desde el módulo principal (__main__).
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)
"""
Aquí se crea una instancia de SQLAlchemy llamada db y se le pasa la instancia de la aplicación 
Flask (app) como argumento. Esto vincula la instancia de SQLAlchemy (db) con la configuración 
de la aplicación Flask (app), permitiendo que SQLAlchemy acceda y gestione la base de datos que 
especificas en la configuración de Flask.
"""
class Sucursal(db.Model):
    __tablename__ = 'sucursal'
    id = db.Column(db.Integer, primary_key = True)
    numero = db.Column(db.Integer, nullable = False)
    provincia = db.Column(db.String(100), nullable = False)
    localidad = db.Column(db.String(100), nullable = False)
    direccion = db.Column(db.String(100), nullable = False)
    paquete = db.relationship('Paquete', backref = 'sucursal', cascade = 'all, delete-orphan')
    transporte = db.relationship('Transporte', backref = 'sucursal', cascade= 'all, delete-orphan')
    repartidor = db.relationship('Repartidor', backref = 'sucursal', cascade = 'all, delete-orphan')

class Transporte(db.Model):
    __tablename__ = 'transporte'
    id = db.Column(db.Integer, primary_key = True)
    numerotransporte = db.Column(db.Integer, nullable = False)
    fechahorasalida = db.Column(db.DateTime)
    fechahorallegada = db.Column(db.DateTime)
    idsucursal = db.Column(db.Integer, db.ForeignKey('sucursal.id'))

class Repartidor(db.Model):
    __tablename__ ='repartidor'
    id = db.Column(db.Integer, primary_key = True)
    numero = db.Column(db.Integer, nullable = False)
    nombre = db.Column(db.String(60), nullable = False)
    dni = db.Column(db.String(8), nullable = False)
    idsucursal = db.Column(db.Integer, db.ForeignKey('sucursal.id'))

class Paquete(db.Model):
    __tablename__ = 'paquete'
    id = db.Column(db.Integer, primary_key = True)
    numeroenvio = db.Column(db.Integer, nullable = False)
    peso = db.Column(db.Integer, nullable = False)
    nomdestinatario = db.Column(db.String(60), nullable = False)
    dirdestinatario = db.Column(db.String(100), nullable = False)
    entregado = db.Column(db.Boolean, default = False)
    observaciones = db.Column(db.Text)
    idsucursal = db.Column(db.Integer, db.ForeignKey('sucursal.id'))
    idtransporte = db.Column(db.Integer, db.ForeignKey('transporte.id'))
    idrepartidor = db.Column(db.Integer, db.ForeignKey('repartidor.id'))