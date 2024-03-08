from utils.db import db
from routes.inacap import UserMixin
# 1 usuarios para iniciar sesion

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(100))
    nombre_usuario = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    area = db.Column(db.String(120)) # carreras de inacap
    run = db.Column(db.String(20), unique=True)
    correo = db.Column(db.String(120), unique=True)
    foto =  db.Column(db.LargeBinary)
    perfil = db.Column(db.String(100)) # administrador, docente, gestor de reportes

    def __init__(self, nombre_completo, nombre_usuario, password, perfil, area, correo, run, foto): 
        self.nombre_completo = nombre_completo
        self.nombre_usuario = nombre_usuario
        self.password = password
        self.perfil = perfil
        self.area = area
        self.correo = correo
        self.run = run
        self.foto = foto

        
class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    marca = db.Column(db.String(30))
    tipo_id = db.Column(db.Integer, db.ForeignKey('tipos.id'))
    tipo = db.relationship('Tipos', back_populates='data')
    estado_id = db.Column(db.Integer, db.ForeignKey('estados.id'))
    estado = db.relationship('Estados', back_populates='data')
    reserva = db.relationship('Reserva', back_populates='data')
    
    def __init__(self, marca, estado_id, tipo_id):
        self.marca = marca
        self.estado_id = estado_id
        self.tipo_id = tipo_id
        
class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_id = db.Column(db.Integer, db.ForeignKey('data.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    data = db.relationship('Data', back_populates='reserva')
    nombre_completo = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    start_event = db.Column(db.TIMESTAMP, nullable=False)
    end_event = db.Column(db.TIMESTAMP, nullable=False)
    area = db.Column(db.String)

    def __init__(self, data_id, nombre_completo, title, start_event, end_event, area):
        self.data_id = data_id
        self.nombre_completo = nombre_completo
        self.title = title
        self.start_event = start_event
        self.end_event = end_event
        self.area = area

class Tipos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    data = db.relationship('Data', lazy='dynamic', back_populates='tipo')

    def __init__(self, title, data):
        self.title = title
        self.data = data

class Estados(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    data = db.relationship('Data', lazy='dynamic', back_populates='estado')

    def __init__(self, title, data):
        self.title = title
        self.data = data

class GraficoGuardado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String)
    etiquetas = db.Column(db.String)
    valores = db.Column(db.String)
    
    def __init__(self, titulo, etiquetas, valores):
        self.titulo = titulo
        self.etiquetas = etiquetas
        self.valores = valores
