from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, Form, FormField, TextField, SelectMultipleField, SelectField, MultipleFileField, widgets
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from src import tabla_usuarios, tabla_validacion
from flask import session


class RegistroForm(FlaskForm):
    cedula = IntegerField('Cedula', validators=[DataRequired(message='Ingrese un numero de cedula porfavor')])
    nombre = StringField('Nombre', validators=[DataRequired(message='Ingrese sus nombres porfavor')])
    apellido = StringField('Apellido', validators=[DataRequired(message='Ingrese sus apellidos porfavor')])
    habilidades = TextAreaField('Habilidades')
    experiencia = TextAreaField('Experiencia')
    educacion = TextAreaField('Educacion')
    archivo = MultipleFileField('Ingrese las fotos de su cedula de cada lado', validators = [DataRequired(message='Debes ingresar las fotos de tu cedula'),FileAllowed(['.jpg', '.jpeg', '.png', '.pdf'])])
    username = StringField('Usuario', validators=[
                           DataRequired(message='Ingrese un usuario porfavor'), Length(min=6, max=20, message='El usuario debe tener minimo 6 caracteres')])
    email = StringField('Email', validators=[DataRequired(
        message='Ingrese un email porfavor'), Email(message='No es un correo valido ')])
    password = PasswordField('Contraseña', validators=[
                             DataRequired(message='Ingrese una contraseña porfavor')])
    confirm_password = PasswordField('Confirme Contraseña', validators=[
                                     DataRequired(message='Confirme su contraseña porfavor'), EqualTo('password', message='Las contraseñas ingresadas no son las mismas')])
    submit = SubmitField('Ingrese')

    def validate_username(self, username):
        user = tabla_usuarios.find_one({'usuario': username.data})
        user2 = tabla_validacion.find_one({'usuario': username.data})
        if user or user2:
            raise ValidationError(
                'Este usuario no esta disponibles. Porfavor ingrese otro.')

    def validate_email(self, email):
        email = tabla_usuarios.find_one({'email': email.data})
        if email:
            raise ValidationError(
                'Este email ya esta registrado. Porfavor inicie sesion o recupere su contraseña')

    def validate_cedula(self, cedula):
        user = tabla_usuarios.find_one({'cedula': cedula.data})
        user2 = tabla_validacion.find_one({'cedula': cedula.data})
        if user or user2:
            raise ValidationError(
                'Este usuario no esta disponibles. Porfavor ingrese otro.')
                
class InicioSesionForm(FlaskForm):
    username = StringField('Usuario', validators=[
                           DataRequired(), Length(min=6, max=20)])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember = BooleanField('  Recordar mi usuario')
    submit = SubmitField('Inicia Sesion')


class ActualizarPerfilForm(FlaskForm):
    username = StringField('Usuario', validators=[
                           DataRequired(), Length(min=6, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    cedula = IntegerField('Cedula', validators=[DataRequired(message='Ingrese un numero de cedula porfavor')])
    nombre = StringField('Nombre', validators=[DataRequired(message='Ingrese sus nombres porfavor')])
    apellido = StringField('Apellido', validators=[DataRequired(message='Ingrese sus apellidos porfavor')])
    habilidades = TextAreaField('Habilidades')
    experiencia = TextAreaField('Experiencia')
    educacion = TextAreaField('Educacion')
    picture = FileField('Actualizar la foto',
                        validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Actualizar')

    def validate_username(self, username):
        if session['user'] != username.data:
            user = tabla_usuarios.find_one({'usuario': username.data})
            if user:
                raise ValidationError(
                    'Este usuario no esta disponibles. Porfavor ingrese otro.')

    def validate_email(self, email):
        if session['email'] != email.data:
            email = tabla_usuarios.find_one({'email': email.data})
            if email:
                raise ValidationError(
                    'Este email ya esta registrado. Porfavor inicie sesion o recupere su contraseña')


class PublicacionForm(FlaskForm):
    titulo = StringField('Titulo', validators=[DataRequired(message = 'Porfavor agregale un titulo a tu publicacion')])
    archivo = MultipleFileField('Sube una foto de lo que estas haciendo', validators = [FileAllowed(['.jpg', '.jpeg', '.png'])])
    contenido = TextAreaField('Compartenos que haces', validators=[DataRequired(message = 'Porfavor agregale contenido a tu publicacion')])
    categoria = SelectField('Categorias', choices=[('hola', 'hola')])
    submit = SubmitField('Agregar')
class ServicioForm(FlaskForm):
    pass