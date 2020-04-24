from flask import Flask
from pymongo import MongoClient
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'c81dac792846c247acb200f1b0a7eab4'
client = MongoClient(
    "mongodb+srv://jatobrun:jatobrun@cluster0-hx8rh.mongodb.net/test?retryWrites=true&w=majority")
#client = MongoClient("mongodb://localhost:2717")
db = client['CraigList']
tabla_usuarios = db['Usuarios']
tabla_validacion = db['Validacion']
tabla_publicaciones = db['Publicaciones']
tabla_empleados = db['Empleados']
bcrypt = Bcrypt(app)
from src import routes