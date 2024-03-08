from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_wtf import FlaskForm
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user, login_manager, logout_user
from wtforms import StringField, PasswordField, SubmitField,  SelectField, FileField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bootstrap import Bootstrap
from flask_bcrypt import Bcrypt
from datetime import datetime
from sqlalchemy import func, extract
import base64
#aca importamos de los otros archivos.py
from app import app
from models.tablas import Usuario, Data, Reserva, Estados, Tipos, GraficoGuardado
from utils.db import db

# iniciamos la instancia Bycript para encriptar contraseña
encriptador = Bcrypt(app)
#iniciamos bootstrap
Bootstrap(app)
# configuramos el adminisitrador de inicio de sesion de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# metodo que se llama cuando se carga un usuario desde la sesion
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# formularios
class RegisterForm(FlaskForm):
    nombre_usuario = StringField(validators=[InputRequired(), Length(min=4, max=80)], render_kw={"placeholder": "Usuario"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=80)], render_kw={"placeholder": "Contraseña"})
    correo = StringField(validators=[InputRequired(), Length(min=4, max=200)], render_kw={"placeholder": "Correo"})
    nombre_completo = StringField(validators=[InputRequired(), Length(min=7, max=120)], render_kw={"placeholder": "Nombre completo"})
    run = StringField(validators=[InputRequired(), Length(min=6, max=11)], render_kw={"placeholder": "Rut"})
    area = SelectField('Área', choices=[('Administración', 'Administración'), ('Agroindustria y Medioambiente', 'Agroindustria y Medioambiente'), ('Automatización y Robotica', 'Automatización y Robotica'), ('Construcción', 'Construcción'), ('Diseño & Comunicacíón', 'Diseño & Comunicacíón'), ('Electricidad y Electrónica - Telecomunicaciones', 'Electricidad y Electrónica - Telecomunicaciones'), ('Energías Renovables y Eficiencia Energetica', 'Energías Renovables y Eficiencia Energetica'), ('Hoteleria, Turismo y Gastronomía', 'Hoteleria, Turismo y Gastronomía'), ('Logística', 'Logística'), ('Mecánica', 'Mecánica'), ('Mineria y Metalurgia', 'Mineria y Metalurgia'), ('Salud', 'Salud'), ('Tecnologías de Información y Ciberseguridad', 'Tecnologías de Información y Ciberseguridad')])
    submit = SubmitField('Registrarse')
    # ver si ya existe el usuario
    def user_existing(self, nombre_usuario):
        Usuario_usuario = Usuario.query.filter_by(nombre_usuario=nombre_usuario.data).first()
        if Usuario_usuario:
            raise ValidationError('Este usuario ya esta registrado')

class LoginForm(FlaskForm):
    nombre_usuario = StringField(validators=[InputRequired(), Length(min=4, max=80)], render_kw={"placeholder": "Usuario"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=80)], render_kw={"placeholder": "Contraseña"})
    submit = SubmitField('Iniciar Sesion')

class PerfilForm(FlaskForm):
    foto = FileField()
    submit = SubmitField('Actualizar')


class ReservaForm(FlaskForm):
    data_id = data_id = SelectField('Data', choices=[], coerce=int)
    title = StringField(validators=[InputRequired(), Length(min=5, max=50)], render_kw={"placeholder": "Sala 110"})
    area = SelectField('Área', choices=[('Administración', 'Administración'), ('Agroindustria y Medioambiente', 'Agroindustria y Medioambiente'), ('Automatización y Robotica', 'Automatización y Robotica'), ('Construcción', 'Construcción'), ('Diseño & Comunicacíón', 'Diseño & Comunicacíón'), ('Electricidad y Electrónica - Telecomunicaciones', 'Electricidad y Electrónica - Telecomunicaciones'), ('Energías Renovables y Eficiencia Energetica', 'Energías Renovables y Eficiencia Energetica'), ('Hoteleria, Turismo y Gastronomía', 'Hoteleria, Turismo y Gastronomía'), ('Logística', 'Logística'), ('Mecánica', 'Mecánica'), ('Mineria y Metalurgia', 'Mineria y Metalurgia'), ('Salud', 'Salud'), ('Tecnologías de Información y Ciberseguridad', 'Tecnologías de Información y Ciberseguridad')])
    submit = SubmitField('Enviar Reserva')  
# formulario para ingresar los datas al sistema
class DatasForm(FlaskForm):
    marca = StringField(validators=[InputRequired(), Length(min=1, max=50)], render_kw={"placeholder": "Marca"})
    tipo_id = SelectField('Tipos', choices=[], coerce=int)
    estado_id = SelectField('Estados', choices=[], coerce=int)
    submit = SubmitField('Registrar Data')

# formulario para los graficos:
class GraficoForm(FlaskForm):
    titulo = StringField('Título del gráfico:')
    etiquetas = StringField('Etiquetas (separadas por comas):')
    valores = StringField('Valores (separadas por comas):')
    submit = SubmitField('Crear gráfico')

meses = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre"
}
# ruta inicial
@app.route('/')
def home():
    return render_template('home.html')

# ruta para el login, valida los datos y te inicia sesion
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(nombre_usuario=form.nombre_usuario.data).first()
        if usuario:
            if encriptador.check_password_hash(usuario.password, form.password.data):
                login_user(usuario)
                flash('Iniciaste sesión correctamente')
                return redirect(url_for('dashboard'))
        
    return render_template('login.html', form=form)

# ruta para enviar los datos del registro y guardarlos en la base de datos 
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # guardamos el encriptador en una variable 'hased_password' para que luego escripte la contraseña del nuevo usuario
        hashed_password = encriptador.generate_password_hash(form.password.data)
        # guardamos los datos en una variable 'nuevo_ususario' con el encriptador en password
        with open('static/minilogo.png', 'rb') as f:
            foto = f.read()
        foto = foto
        perfil = 'docente'
        nuevo_usuario = Usuario(nombre_usuario=form.nombre_usuario.data, password=hashed_password, nombre_completo=form.nombre_completo.data, area=form.area.data, run=form.run.data, correo=form.correo.data ,perfil=perfil, foto=foto)
        #agregamos el usuario
        db.session.add(nuevo_usuario)
        #lo enviamos a la base de datos
        db.session.commit()
        # nos redirigimmos al login
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# ruta cerrar sesion
@app.route('/logout', methods=['GET', 'POST'])
@login_required # solo permite usar esta funcion si estas logeado
def logout():
    logout_user()
    return redirect(url_for('login'))


# ruta de dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required # solo permite que los usuarios logeados entren a esta funcion 
def dashboard():
    usuario_actual = Usuario.query.filter_by(id=current_user.id).first()
    foto_base64 = base64.b64encode(usuario_actual.foto).decode('utf-8')
    if usuario_actual.perfil == 'docente' or usuario_actual.perfil == 'administrador' or usuario_actual.perfil == 'gestor de reportes':
        # para la opcion de ver el calendario // esta en jinja html igual
        events = Reserva.query.order_by(Reserva.id).all()
        
        # grafico mixto de datas disponibles y reservados por data
        grafico = db.session.query(Data.marca, func.count(Data.marca)).filter(Data.estado_id == 1).group_by(Data.marca).all()
        titulo = 'Datas disponibles'
        etiquetas = [i[0] for i in grafico]
        valores = [i[1] for i in grafico]
        grafico2 = db.session.query(Data.marca, func.count(Data.marca)).filter(Data.estado_id == 2).group_by(Data.marca).all()
        titulo2 = 'Datas Reservados'
        valores2 = [i[1] for i in grafico2]

        # grafico de cantidad de datas por area
        grafico3 = db.session.query(Reserva.area, func.count(Reserva.area)).group_by(Reserva.area).all()
        titulo3 = 'Datas usados por area'
        etiquetas3 = [i[0] for i in grafico3]
        valores3 = [i[1] for i in grafico3]

        # grafico de cantidad de reservas por fecha
        grafico4 = db.session.query(extract('month', Reserva.start_event), func.count(Reserva.id)).group_by(extract('month', Reserva.start_event)).all()
        titulo4 = 'Datas usados por area'
        etiquetas4 = [meses[i[0]] for i in grafico4]
        valores4 = [i[1] for i in grafico4]
    return render_template('dashboard.html',foto=foto_base64 ,calendar=events, usuario_actual=usuario_actual, valores=valores, titulo=titulo, etiquetas=etiquetas, valores2=valores2, titulo2=titulo2, titulo3=titulo3, valores3=valores3, etiquetas3=etiquetas3, titulo4=titulo4, etiquetas4=etiquetas4, valores4=valores4)


# ruta de perfil (actualizar datos y completar datos)
@app.route('/perfil', methods=["GET", "POST"])
@login_required
def updatePerfil():
    form = PerfilForm()
    usuario_actual = Usuario.query.filter_by(id=current_user.id).first()
    foto_base64 = base64.b64encode(usuario_actual.foto).decode('utf-8')
    if usuario_actual.perfil == 'docente' or usuario_actual.perfil == 'administrador' or usuario_actual.perfil == 'gestor de reportes':
        if form.validate_on_submit():
            # Obtener el archivo y guardarlo en el servidor
            foto = request.files['foto']
            # Crear una nueva instancia del modelo Phot
            usuario_actual.foto = foto.read()
            db.session.commit()
            return redirect(url_for('dashboard'))
    return render_template('perfil.html', form=form, usuario_actual=usuario_actual, foto=foto_base64)


# ruta para reservar 
@app.route('/reserva', methods=['GET', 'POST'])
@login_required
def reserva():
    form = ReservaForm()
    form.data_id.choices = [(data.id, f"id: {data.id} - Marca: {data.marca} - {data.tipo.title}") for data in Data.query.join(Tipos).filter(Data.estado_id == 1).all()]
    usuario_actual = Usuario.query.filter_by(id=current_user.id).first()
    if usuario_actual.perfil == 'docente' or usuario_actual.perfil == 'administrador':
        if request.method == "POST":
            start = request.form['start_event']
            end = request.form['end_event']
            start_event = datetime.strptime(start, '%Y-%m-%dT%H:%M')
            end_event = datetime.strptime(end, '%Y-%m-%dT%H:%M')
            nueva_reserva = Reserva(data_id=form.data_id.data, nombre_completo=current_user.nombre_completo, title=form.title.data, start_event=start_event, end_event=end_event, area=form.area.data)
            db.session.add(nueva_reserva)
            data = Data.query.filter_by(id=form.data_id.data).first()
            data.estado_id = 2
            db.session.commit()
            return redirect(url_for('dashboard'))
    return render_template('reserva.html', form=form, usuario_actual=usuario_actual)

# panel para crear un reporte
@app.route('/grafico', methods=['GET', 'POST'])
@login_required
def grafico():
    usuario_actual = Usuario.query.filter_by(id=current_user.id).first()
    form = GraficoForm()
    foto_base64 = base64.b64encode(usuario_actual.foto).decode('utf-8')
    if usuario_actual.perfil == 'administrador' or usuario_actual.perfil == 'gestor de reportes':
        reservas = Reserva.query.all()
        if form.validate_on_submit():
            titulo = form.titulo.data
            etiquetas = form.etiquetas.data.split(',')
            valores = form.valores.data.split(',')
            etiquetas_str = ','.join(etiquetas)
            valores_str = ','.join(valores)
            
            grafico1 = GraficoGuardado(titulo=titulo, etiquetas=etiquetas_str, valores=valores_str)
            db.session.add(grafico1)
            db.session.commit()
            
            return render_template('crearGrafico.html', foto=foto_base64, form=form, titulo=titulo, etiquetas=etiquetas, valores=valores, usuario_actual=usuario_actual, reservas=reservas)
    return render_template('crearGrafico.html', form=form, usuario_actual=usuario_actual, reservas=reservas, foto=foto_base64)

# panel para agregar data
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    form = DatasForm()
    usuario_actual = Usuario.query.filter_by(id=current_user.id).first()
    form.tipo_id.choices = [(tipos.id, tipos.title) for tipos in Tipos.query.all()]
    form.estado_id.choices = [(estados.id, estados.title) for estados in Estados.query.all()]
    if usuario_actual.perfil == 'administrador':
        if form.validate_on_submit():
            # guardamos el nuevo data en nuevo_data
            nuevo_data = Data(marca=form.marca.data, tipo_id=form.tipo_id.data, estado_id=form.estado_id.data)
            #agregamos el data
            db.session.add(nuevo_data)
            #lo enviamos a la base de datos
            db.session.commit()
            # nos redirigimmos al login
            return redirect(url_for('admin'))
    return render_template('admin.html', form=form, usuario_actual=usuario_actual)
# entrar al calendario
@app.route('/calendar')
@login_required
def calendar():
    usuario_actual = Usuario.query.filter_by(id=current_user.id).first()
    foto_base64 = base64.b64encode(usuario_actual.foto).decode('utf-8')
    if usuario_actual.perfil == 'administrador':
        events = Reserva.query.order_by(Reserva.id).all()
        return render_template('calendar.html', calendar=events, usuario_actual=usuario_actual, foto=foto_base64)


# insertar evento
@app.route('/insert', methods=["GET", "POST"])
@login_required
def insert():
    # para ver si el usuairo actual es administrador
    usuario_actual = Usuario.query.filter_by(id=current_user.id).first()
    if usuario_actual.perfil == 'administrador':
        if request.method == "POST":
            title = request.form['title']
            nombre = request.form['nombre']
            proyector = request.form['proyector']
            area = request.form['area']
            start = request.form['start']
            end = request.form['end']
            
            start_event = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
            end_event = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
            
            # agrega los datos registrador a la tabla Reserva
            events = Reserva(data_id=proyector, nombre_completo=nombre, title=title, area=area, start_event=start_event, end_event=end_event)
            # actualiza el parametro "estado_id" de la tabla Datas para ponerlo en "reservado" 
            data = Data.query.filter_by(id=proyector).first()
            data.estado_id = 2
            db.session.add(events)

            db.session.commit()

            msg = "success"
            return jsonify(msg)
        return redirect(url_for('calendar'))
    else:
        flash('error')


# actualizar evento
@app.route('/update',methods=["GET", "POST"])
@login_required
def update():
    # para ver si el usuario actual es administrador
    usuario_actual = Usuario.query.filter_by(id=current_user.id).first()
    if usuario_actual.perfil == 'administrador':
        if request.method == 'POST':
            title = request.form['title']
            start = request.form['start']
            end = request.form['end']
            nombre = request.form['nombre']
            area = request.form['area']
            proyector = request.form['proyector']
            id = request.form['id']

            start_event = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
            end_event = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
            event = Reserva.query.get(id)
            event.title = title
            event.start_event = start_event
            event.end_event = end_event
            event.nombre_completo = nombre
            event.area = area
            event.data_id = proyector
            db.session.commit()
    
            msg = 'success'
            return jsonify(msg)
        return redirect(url_for('calendar'))


# eliminar evento
@app.route('/ajax_delete', methods=['GET', 'POST'])
@login_required
def delete():
    # para ver si el usuario actual es administrador
    usuario_actual = Usuario.query.filter_by(id=current_user.id).first()
    if usuario_actual.perfil == 'administrador':
        if request.method == 'POST':
            getid = request.form['id']
            proyector = request.form['proyector']
            Reserva.data_id = proyector
            db.session.query(Reserva).filter_by(id=getid).delete()
            data = Data.query.filter_by(id=proyector).first()
            data.estado_id = 1
            db.session.commit()
            return redirect(url_for('calendar'))
