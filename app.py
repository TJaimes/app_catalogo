from re import A
import re
from flask import Flask, render_template, request, redirect
from flask.helpers import make_response
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:watashiwa@localhost:5432/bd'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://igwqnzywudmduk:0196dc8376074e02625e47efc45351a818d9e6cc0bc9052e12a515a7b66206c2@ec2-34-203-182-172.compute-1.amazonaws.com:5432/dft03s8jsb38jn'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class Usuarios(db.Model):
    __tablename__ = "usuarios"
    idUsuario = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(80))
    password = db.Column(db.String(255))

    def __init__(self,email, password):
        self.email=email
        self.password=password

class Editorial(db.Model):
    __tablename__="editorial"
    id_editorial = db.Column(db.Integer, primary_key=True)
    nombre_editorial = db.Column(db.String(80))

    def __init__(self, nombre_editorial):
        self.nombre_editorial = nombre_editorial

class Libro(db.Model):
    __tablename__ = "libro"
    id_libro = db.Column(db.Integer, primary_key=True)
    titulo_libro = db.Column(db.String(80))
    fecha_publicacion = db.Column(db.Date)
    numero_paginas = db.Column(db.Integer)
    formato = db.Column(db.String(30))
    volumen = db.Column(db.Integer)

    id_editorial = db.Column(db.Integer, db.ForeignKey("editorial.id_editorial"))
    id_autor = db.Column(db.Integer, db.ForeignKey("autor.id_autor"))
    id_genero = db.Column(db.Integer, db.ForeignKey("genero.id_genero"))

    def __init__(self, titulo_libro, fecha_publicacion, numero_paginas, formato, volumen, id_editorial, id_autor, id_genero):
        self.titulo_libro = titulo_libro
        self.fecha_publicacion = fecha_publicacion
        self.numero_paginas = numero_paginas
        self.formato = formato
        self.volumen = volumen
        self.id_editorial = id_editorial
        self.id_autor = id_autor
        self.id_genero = id_genero

class Autor(db.Model):
    __tablename__="autor"
    id_autor = db.Column(db.Integer, primary_key=True)
    nombre_autor = db.Column(db.String(130))
    fecha_nac = db.Column(db.Date)
    nacionalidad = db.Column(db.String(30))

    def __init__(self,nombre_autor, fecha_nac, nacionalidad):
        self.nombre_autor = nombre_autor
        self.fecha_nac = fecha_nac
        self.nacionalidad = nacionalidad

class Genero(db.Model):
    __tablename__ = "genero"
    id_genero = db.Column(db.Integer, primary_key=True)
    nombre_genero = db.Column(db.String(30))

    def __init__(self, nombre_genero):
        self.nombre_genero = nombre_genero

class Misfavoritos(db.Model):
    __tablename__ = "misfavoritos"
    id_lista_favoritos = db.Column(db.Integer, primary_key=True)

    id_libro = db.Column(db.Integer, db.ForeignKey("libro.id_libro"))
    idUsuario = db.Column(db.Integer, db.ForeignKey("usuarios.idUsuario"))

    def __init__(self, id_libro, idUsuario):
        self.id_libro = id_libro
        self.idUsuario = idUsuario

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=['POST'])
def login():
    email = request.form["email"]
    password = request.form["password"]
    consultar_usuarios = Usuarios.query.filter_by(email=email).first()
    if consultar_usuarios == None:
        mensaje="Correo no existente"
        return render_template("index.html", mensaje=mensaje) 
    else:
        if bcrypt.check_password_hash(consultar_usuarios.password,password) == True:
            resp = make_response(render_template("menu.html"))
            resp.set_cookie("usuario", str(consultar_usuarios.idUsuario))
            return resp
        else:
            mensaje="Correo o contraseña incorrecto"
            return render_template("index.html", mensaje=mensaje)

@app.route("/registrar")
def registrar():
    return render_template("registrar.html")

@app.route("/registrar_usuario", methods=['POST'])
def registrar_usuario():
    email = request.form.get("email")
    password = request.form.get("password")
    password_cifrado = bcrypt.generate_password_hash(password).decode('utf-8')
    print(email)
    print(password)
    print(password_cifrado)

    usuario = Usuarios(email = email, password = password_cifrado)
    db.session.add(usuario)
    db.session.commit()

    return redirect("/iniciar")

@app.route("/iniciar")
def iniciar():
    return render_template("index.html")

@app.route("/menu")
def menu():
    return render_template("menu.html")

#REGISTRO DE EDITORIALES
@app.route("/formulario_editorial")
def formulario_editorial():
    return render_template("formEditorial.html")

@app.route("/registrar_editorial",methods=['POST'] )
def registrar_editorial():
    nombre_editorial = request.form["nombre_editorial"]
    editorial_nuevo = Editorial(nombre_editorial = nombre_editorial)
    db.session.add(editorial_nuevo)
    db.session.commit()
    message = "Editorial registrada!!"
    return redirect("/catalogo_editorial")

#REGISTRO DE LIBROS
@app.route("/formulario_libro")
def formulario_libro():
    consulta_editorial = Editorial.query.all()
    print(consulta_editorial)
    consulta_genero = Genero.query.all()
    print(consulta_genero)
    consulta_autor = Autor.query.all()
    print(consulta_autor)
    return render_template("formLibro.html", consulta_editorial=consulta_editorial, consulta_genero=consulta_genero, consulta_autor=consulta_autor)

@app.route("/registrar_libro", methods=['POST'])
def registrar_libro():
    titulo_libro = request.form["titulo_libro"]
    fecha_publicacion = request.form["fecha_publicacion"]
    numero_paginas = request.form["numero_paginas"]
    formato = request.form["formato"]
    volumen = request.form["volumen"]
    id_editorial=request.form["editorial"]
    id_autor = request.form["autor"]
    id_genero = request.form["genero"]
    numero_paginas_int = int(numero_paginas)

    libro_nuevo = Libro(titulo_libro=titulo_libro, fecha_publicacion=fecha_publicacion, numero_paginas=numero_paginas_int,formato=formato, volumen=volumen, id_editorial=id_editorial, id_genero=id_genero,id_autor=id_autor)
    db.session.add(libro_nuevo)
    db.session.commit()
    message = "Libro registrado!!"
    return redirect("/catalogo_libro")

#REGISTRO DE AUTORES
@app.route("/formulario_autor")
def formulario_autor():
    return render_template("formAutor.html")

@app.route("/registrar_autor", methods=['POST'])
def registrar_autor():
    nombre_autor = request.form["nombre_autor"]
    fecha_nac = request.form["fecha_nac"]
    nacionalidad = request.form["nacionalidad"]

    autor_nuevo = Autor(nombre_autor=nombre_autor, fecha_nac=fecha_nac, nacionalidad=nacionalidad)
    db.session.add(autor_nuevo)
    db.session.commit()
    message = "Autor registrado!!"
    return redirect("/catalogo_autor")

#REGISTRO DE GENEROS
@app.route("/formulario_genero")
def formulario_genero():
    return render_template("formGenero.html")

@app.route("/registrar_genero", methods=['POST'])
def registrar_genero():
    nombre_genero = request.form["nombre_genero"]

    genero_nuevo = Genero(nombre_genero = nombre_genero)
    db.session.add(genero_nuevo)
    db.session.commit()
    message = "Género registrado!!"
    return redirect("/catalogo_genero")

#CATÁLOGOS
@app.route("/catalogo_libro")
def catalogo_libro():
    Consulta = Libro.query.join(Genero, Libro.id_genero == Genero.id_genero).join(Autor, Libro.id_autor == Autor.id_autor).join(Editorial, Libro.id_editorial == Editorial.id_editorial).add_columns(Libro.titulo_libro, Autor.nombre_autor, Genero.nombre_genero, Editorial.nombre_editorial, Libro.numero_paginas, Libro.formato, Libro.volumen, Libro.fecha_publicacion, Libro.id_libro)
    return render_template("catalogoLibro.html", consulta_libros = Consulta)

@app.route("/mis_favoritos")
def mis_favoritos():
    Consulta = Misfavoritos.query.join(Libro, Misfavoritos.id_libro == Libro.id_libro).join(Genero, Libro.id_genero == Genero.id_genero).join(Autor, Libro.id_autor == Autor.id_autor).join(Editorial, Libro.id_editorial == Editorial.id_editorial).add_columns(Libro.titulo_libro, Autor.nombre_autor, Genero.nombre_genero, Editorial.nombre_editorial, Libro.numero_paginas, Libro.formato, Libro.volumen, Libro.fecha_publicacion, Libro.id_libro, Misfavoritos.id_lista_favoritos)
    return render_template("MisFavoritos.html", consulta_fav=Consulta)

@app.route("/catalogo_autor")
def catalogo_autor():
    consulta_autor = Autor.query.all()
    for autor in consulta_autor:
        nombre_autor = autor.nombre_autor
        fecha_nac = autor.fecha_nac
        nacionalidad = autor.nacionalidad
    return render_template("catalogoAutor.html", consulta_autor=consulta_autor)

@app.route("/catalogo_editorial")
def catalogo_editorial():
    consulta_editorial = Editorial.query.all()
    for editorial in consulta_editorial:
        nombre_editorial = editorial.nombre_editorial
    return render_template("catalogoEditorial.html", consulta_editorial = consulta_editorial)

@app.route("/catalogo_genero")
def catalogo_genero():
    consulta_genero = Genero.query.all()
    for genero in consulta_genero:
        nombre_genero = genero.nombre_genero
    return render_template("catalogoGenero.html", consulta_genero = consulta_genero)

#ACCIONES EN LIBRO
@app.route("/eliminarlibro/<id>")
def eliminarlibro(id):
    libro = Libro.query.filter_by(id_libro = int(id)).delete()
    db.session.commit()
    return redirect("/catalogo_libro")

@app.route("/editarlibro/<id>")
def editarlibro(id):
    libro = Libro.query.filter_by(id_libro=int(id)).first()
    consulta_editorial = Editorial.query.all()
    consulta_genero = Genero.query.all()
    consulta_autor = Autor.query.all()
    return render_template("modificarLibro.html", libro=libro, consulta_editorial=consulta_editorial, consulta_genero=consulta_genero, consulta_autor=consulta_autor)

@app.route("/modificarlibro", methods=['POST'])
def modificarlibro():
    id_libro = request.form['id_libro']
    nuevo_titulo = request.form['titulo_libro']
    nuevo_publicacion = request.form['fecha_publicacion']
    nuevo_paginas = request.form['numero_paginas']
    nuevo_formato = request.form['formato']
    nuevo_voumen = request.form['volumen']
    nuevo_id_editorial = request.form['editorial']
    nuevo_id_autor = request.form['autor']
    nuevo_id_genero = request.form['genero']
    nuevo_paginas_int = int(nuevo_paginas)

    libro = Libro.query.filter_by(id_libro=int(id_libro)).first()
    libro.titulo_libro = nuevo_titulo
    libro.fecha_publicación = nuevo_publicacion
    libro.numero_paginas = nuevo_paginas_int
    libro.formato = nuevo_formato
    libro.volumen = nuevo_voumen
    libro.id_editorial = nuevo_id_editorial
    libro.id_autor = nuevo_id_autor
    libro.id_genero = nuevo_id_genero
    db.session.commit()
    return redirect("/catalogo_libro")

#ACCIONES DE AUTOR
@app.route("/eliminarautor/<id>")
def eliminarautor(id):
    autor = Autor.query.filter_by(id_autor = int(id)).delete()
    db.session.commit()
    return redirect("/catalogo_autor")

@app.route("/editarautor/<id>")
def editarautor(id):
    autor = Autor.query.filter_by(id_autor=int(id)).first()
    return render_template("modificarAutor.html",autor=autor)

@app.route("/modificarautor", methods=['POST'])
def modificarautor():
    id_autor = request.form['id_autor']
    nuevo_nombre = request.form['nombre_autor']
    nueva_fecha = request.form['fecha_nac']
    nuevo_nacionalidad = request.form['nacionalidad']

    autor = Autor.query.filter_by(id_autor=int(id_autor)).first()
    autor.nombre_autor = nuevo_nombre
    autor.fecha_nac = nueva_fecha
    autor.nacionalidad = nuevo_nacionalidad
    db.session.commit()
    return redirect("/catalogo_autor")

#ACCIONES DE EDITORIAL
@app.route("/eliminareditorial/<id>")
def eliminareditorial(id):
    editorial = Editorial.query.filter_by(id_editorial = int(id)).delete()
    db.session.commit()
    return redirect("/catalogo_editorial")

@app.route("/editareditorial/<id>")
def editareditorial(id):
    editorial = Editorial.query.filter_by(id_editorial=int(id)).first()
    return render_template("modificarEditorial.html", editorial=editorial)

@app.route("/modificareditorial", methods=['POST'])
def modificareditorial():
    id_editorial = request.form['id_editorial']
    nuevo_nombre = request.form['nombre_editorial']

    editorial = Editorial.query.filter_by(id_editorial=int(id_editorial)).first()
    editorial.nombre_editorial = nuevo_nombre
    db.session.commit()
    return redirect("/catalogo_editorial")

#ACCIONES DE GÉNERO
@app.route("/eliminargenero/<id>")
def eliminargenero(id):
    genero = Genero.query.filter_by(id_genero=int(id)).delete()
    db.session.commit()
    return redirect("/catalogo_genero")

@app.route("/editargenero/<id>")
def editargenero(id):
    genero = Genero.query.filter_by(id_genero=int(id)).first()
    return render_template("modificarGenero.html", genero=genero)

@app.route("/modificargenero", methods=['POST'])
def modificargenero():
    id_genero = request.form['id_genero']
    nuevo_nombre = request.form['nombre_genero']

    genero = Genero.query.filter_by(id_genero=int(id_genero)).first()
    genero.nombre_genero = nuevo_nombre
    db.session.commit()
    return redirect("/catalogo_genero")

#ACCIÓN DE MIS FAVORITOS
@app.route("/añadirfav/<id>")
def añadirfav(id):
    idUsuario = request.cookies.get("idUsuario")
    print(idUsuario)

    misfav = Misfavoritos.query.filter_by(id_libro = int(id), idUsuario=idUsuario).first()
    if misfav == None:
        misfavoritos = Misfavoritos(id_libro=id, idUsuario=idUsuario)
        db.session.add(misfavoritos)
        db.session.commit()
    return redirect("/catalogo_libro")

@app.route("/eliminarfavoritos/<id>")
def eliminarfavoritos(id):
    misfavoritos = Misfavoritos.query.filter_by(id_lista_favoritos = int(id)).delete()
    print("eliminando:",id)
    db.session.commit()
    return redirect("/mis_favoritos")

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)