from PIL import Image
import os
import time
import secrets
from flask import render_template, flash, redirect, url_for, session, request
from src.forms import RegistroForm, InicioSesionForm, ActualizarPerfilForm, PublicacionForm, ServicioForm
from src import app, tabla_publicaciones, tabla_usuarios, tabla_empleados, bcrypt, tabla_validacion
from bson import ObjectId

@app.route('/')
def inicio():
    return render_template('inicio.html', titulo= 'Inicio')
    
@app.route('/sobre_nosotros')
def sobre_nosotros():
    return render_template('sobre_nosotros.html', titulo = 'Sobre Nosotros')

@app.route('/iniciar_sesion', methods=['GET', 'POST'])
def iniciar_sesion():
    form = InicioSesionForm()
    if form.validate_on_submit():
        user = tabla_usuarios.find_one({'usuario': form.username.data})
        if user and bcrypt.check_password_hash(user['password'], form.password.data):
            # login_user(user, remember=login.remember.data)
            flash('Inicio de sesion completado satisfactoriamente', 'success')
            session['user'] = user['usuario']
            session['email'] = user['email']
            if user['image'] != None:
                session['image'] = user['image']
            else:
                session['image'] = 'default.jpg'
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('No se pudo iniciar sesion, porfavor revise el usuario y contraseña', 'danger')
    return render_template('inicio_sesion.html', titulo = 'Inicio De Sesion', form = form)

def save_picture(form_picture, categoria):
    if categoria == 'cedula':
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(form_picture.filename)
        picture_fn = random_hex + f_ext
        picture_path = os.path.join(app.root_path, 'static/cedula-pic', picture_fn)
        form_picture.save(picture_path)
        return picture_fn
    elif categoria == 'publicacion':
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(form_picture.filename)
        picture_fn = random_hex + f_ext
        picture_path = os.path.join(app.root_path, 'static/publicacion-pic', picture_fn)
        form_picture.save(picture_path)
        return picture_fn
    elif categoria == 'perfil':
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(form_picture.filename)
        picture_fn = random_hex + f_ext
        picture_path = os.path.join(app.root_path, 'static/perfil-pic', picture_fn)
        form_picture.save(picture_path)
        return picture_fn

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    form = RegistroForm()
    if form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        cedula_foto = []
        for e in form.archivo.data:
            print(e)
            nombre = save_picture(e, 'cedula')
            cedula_foto.append(nombre)
        usuario = {'usuario': form.username.data,
                   'password': hashed_pass, 
                   'email': form.email.data, 
                   'image': 'default.jpg',
                   'cedula': form.cedula.data,
                   'nombre': form.nombre.data,
                   'apellido': form.apellido.data,
                   'habilidades': form.habilidades.data,
                   'experiencia': form.experiencia.data,
                   'educacion': form.educacion.data, 
                   'cedula-foto': cedula_foto}
                   
        tabla_validacion.insert_one(usuario)
        flash(f'Se envio correctamente la solicitud, en unas horas te mandaremos un correo a {form.email.data} para que puedas hacer uso de tu cuenta', 'success')
        return redirect(url_for('iniciar_sesion'))
    return render_template('registro.html', titulo = 'Registro', form = form)

@app.route('/index', methods = ['GET', 'POST'])
def index():
    form = PublicacionForm()
    if form.validate_on_submit():
        archivos = []
        for e in form.archivo.data:
            archivo = save_picture(e, 'publicacion')
            archivos.append(archivo)
        publicacion = {
            'creador': session['user'],
            'fecha': time.strftime("%d-%m-%Y"),
            'categoria': form.categoria.data,
            'titulo': form.titulo.data,
            'archivos': archivos,
            'contenido': form.contenido.data,
        }
        tabla_publicaciones.insert_one(publicacion)
        return redirect(url_for('index'))
    if request.method == 'GET':
        publicaciones = tabla_publicaciones.find().sort('_id', -1)
        validacion = tabla_publicaciones.find_one()
        if validacion:
            vacio_publicaciones = False
        else: 
            vacio_publicaciones = True
        return render_template('index.html', titulo= 'Index', form = form, publicaciones= publicaciones, cc= True, vacio_publicaciones = vacio_publicaciones)
    return render_template('index.html', titulo= 'Index', form = form, publicaciones= publicaciones, cc= True, vacio_publicaciones = vacio_publicaciones)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('inicio'))

@app.route('/admin')
def admin():
    usuarios_no_validados = tabla_validacion.find({})
    if usuarios_no_validados:
        vacio_usuarios = False
    else: 
        vacio_usuarios = True
    return render_template('admin.html', titulo = 'Administrador', usuarios_no_validados = usuarios_no_validados, vacio_usuarios = vacio_usuarios)

@app.route('/aceptar_usuario/<id>')
def aceptar_usuario(id):
    usuario = tabla_validacion.find_one({'_id': ObjectId(id)})
    print(usuario)
    tabla_validacion.delete_one({'_id': ObjectId(id)})
    usuario = {
        'usuario': usuario['usuario'],
        'password': usuario['password'], 
        'email': usuario['email'], 
        'image': 'default.jpg',
        'cedula': usuario['cedula'],
        'nombre': usuario['nombre'],
        'apellido': usuario['apellido'],
        'habilidades': usuario['habilidades'],
        'experiencia': usuario['experiencia'],
        'educacion': usuario['educacion'], 
        'cedula-foto': usuario['cedula-foto']
    }
    tabla_usuarios.insert_one(usuario)
    flash('Se agrego usuario correctamente')
    return redirect(url_for('admin'))

@app.route('/borrar_usuario/<id>', methods = ['GET', 'POST'])
def borrar_usuario(id):
    tabla_validacion.delete_one({'_id': id})

    return redirect(url_for('admin'))

@app.route('/perfil/<id>', methods = ['GET', 'POST'])
def perfil(id):
    if 'user' in session:
        form = ActualizarPerfilForm()
        usuario = tabla_usuarios.find_one({'usuario': id})
        if request.method == 'POST':
            print('hola')
            if form.picture.data:
                filename = save_picture(form.picture.data, 'perfil')
            else: 
                filename = 'default.jpg'
            cambios = {
                'usuario': form.username.data,
                'email': form.email.data, 
                'image': filename,
                'cedula': form.cedula.data,
                'nombre': form.nombre.data,
                'apellido': form.apellido.data,
                'habilidades': form.habilidades.data,
                'experiencia': form.experiencia.data,
                'educacion': form.educacion.data, 
            }
            tabla_publicaciones.update_many({'creador':id}, {'$set': {'creador': form.username.data}})
            tabla_usuarios.update_one({'usuario': id}, {'$set': cambios})
            session['user'] = form.username.data
            session['email'] = form.email.data
            session['image'] = filename
            flash('Tus cambios se realizaron satisfactoriamente', 'success')
        if request.method == 'GET':
            print('hoa 1')
            form.apellido.data = usuario['apellido']
            form.username.data = usuario['usuario']
            form.email.data = usuario['email']
            form.nombre.data = usuario['nombre']
            form.habilidades.data = usuario['habilidades']
            form.experiencia.data = usuario['experiencia']
            form.educacion.data = usuario['educacion']
        return render_template('perfil.html', titulo = 'Perfil', form = form, cc = True)
    else:
        return render_template(url_for('inicio_sesion'))
    return render_template('perfil.html', titulo = 'Perfil')
@app.route('/estadisticas')
def estadisticas():
    return render_template('estadisticas.html', titulo = 'Estadisticas', cc = True)


@app.route('/notificaciones')
def notificaciones():
    return render_template('notificaciones.html', titulo = 'Notificaciones', cc = True)

@app.route('/servicios')
def servicios():
    return render_template('servicios.html', titulo='Servicios')