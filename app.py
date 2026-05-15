from flask import Flask, render_template, request, redirect, url_for, session, url_for
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import bcrypt

load_dotenv()

app = Flask(__name__)
app.secret_key = "mi_clave_super_secreta_123"

# Conexion MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client["flask_login"]
usuarios = db["usuarios"]

# Carpeta uploads
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# HOME
@app.route("/")
def home():
    if "usuario" not in session:
        return redirect(url_for("login"))
    return render_template("home.html", usuario=session["usuario"])

# REGISTRO
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nombre = request.form["nombre"]
        apellido1 = request.form["apellido1"]
        apellido2 = request.form["apellido2"]
        correo = request.form["correo"]
        username = request.form["username"]
        password = request.form["password"]
        foto = request.files["foto"]

        usuario_existente = usuarios.find_one({"username": username})
        if usuario_existente:
            return "El usuario ya existe"

        if foto:
            foto_path = os.path.join(app.config["UPLOAD_FOLDER"], foto.filename)
            foto.save(foto_path)

        # encriptar password
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        # guardar usuario
        usuarios.insert_one({
            "nombre": nombre,
            "apellido1": apellido1,
            "apellido2": apellido2,
            "correo": correo,
            "username": username,
            "foto": foto.filename,
            "password": password_hash
        })
        return render_template("login.html")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        usuario = usuarios.find_one({"username": username})

        if not usuario:
            return redirect(url_for("register"))

        if bcrypt.checkpw(password.encode("utf-8"), usuario["password"]):

            session["usuario"] = {
                "nombre": usuario["nombre"],
                "username": usuario["username"],
                "foto": usuario["foto"]
            }

            return redirect(url_for("home"))

        else:
            return "Contraseña incorrecta"

    return render_template("login.html")

# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
