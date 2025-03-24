from flask import Flask, request, jsonify, session, send_from_directory
from flask_session import Session
from redis import Redis
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# Configuración general
app.config["SECRET_KEY"] = "supersecretkey"
app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_COOKIE_NAME"] = "my_session"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False
app.config["SESSION_REDIS"] = Redis(host="localhost", port=6379, decode_responses=False)

# Base de datos
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres@localhost/intercambio_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicialización
Session(app)
db = SQLAlchemy(app)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:3000"}})

# Subida de imágenes
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Modelos
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100))
    exchange_terms = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

# Crear tablas
with app.app_context():
    db.create_all()

# Registro
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "Usuario ya registrado"}), 400

    password_hash = generate_password_hash(data["password"])
    new_user = User(name=data["name"], email=data["email"], password_hash=password_hash)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Usuario registrado con éxito"}), 201

# Login
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data["email"]).first()

    if user and check_password_hash(user.password_hash, data["password"]):
        session["user_id"] = user.id
        return jsonify({
            "message": "Login exitoso",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email
            }
        }), 200

    return jsonify({"message": "Credenciales incorrectas"}), 401

# Perfil
@app.route("/profile/<int:user_id>", methods=["GET"])
def get_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "Usuario no encontrado"}), 404

    return jsonify({"id": user.id, "name": user.name, "email": user.email}), 200

# Verificar sesión
@app.route("/check-session", methods=["GET"])
def check_session():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"authenticated": False}), 401

    return jsonify({"authenticated": True, "user_id": user_id}), 200

# Publicar servicio
@app.route("/api/services", methods=["POST"])
def publicar_servicio():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"message": "No autorizado"}), 401

    title = request.form.get("title")
    description = request.form.get("description")
    category = request.form.get("category")
    location = request.form.get("location")
    exchange_terms = request.form.get("exchangeTerms")

    # Imagen
    image_file = request.files.get("image")
    image_filename = None

    if image_file:
        if allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

            try:
                image_file.save(image_path)
                image_filename = filename
            except Exception as e:
                print("Error al guardar la imagen:", e)
                return jsonify({"message": "Error al guardar la imagen"}), 500
        else:
            return jsonify({"message": "Formato de imagen no permitido"}), 400

    nuevo_servicio = Service(
        title=title,
        description=description,
        category=category,
        location=location,
        exchange_terms=exchange_terms,
        image=image_filename,
        user_id=user_id
    )

    db.session.add(nuevo_servicio)
    db.session.commit()

    return jsonify({"message": "Servicio publicado con éxito"}), 201

# Obtener servicios
@app.route("/api/services", methods=["GET"])
def obtener_servicios():
    servicios = Service.query.all()
    resultado = []
    for servicio in servicios:
        resultado.append({
            "id": servicio.id,
            "title": servicio.title,
            "description": servicio.description,
            "category": servicio.category,
            "location": servicio.location,
            "exchange_terms": servicio.exchange_terms,
            "image": servicio.image,
            "user_id": servicio.user_id
        })
    return jsonify(resultado), 200

# Editar servicio (con soporte para OPTIONS)
@app.route("/api/services/<int:service_id>", methods=["PUT", "OPTIONS"])
def editar_servicio(service_id):
    if request.method == "OPTIONS":
        return '', 200

    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"message": "No autorizado"}), 401

    servicio = Service.query.get(service_id)
    if not servicio or servicio.user_id != user_id:
        return jsonify({"message": "Servicio no encontrado o sin permisos"}), 404

    data = request.get_json()
    servicio.title = data.get("title", servicio.title)
    servicio.description = data.get("description", servicio.description)
    servicio.category = data.get("category", servicio.category)
    servicio.location = data.get("location", servicio.location)
    servicio.exchange_terms = data.get("exchangeTerms", servicio.exchange_terms)

    db.session.commit()
    return jsonify({"message": "Servicio actualizado con éxito"}), 200

# Eliminar servicio
@app.route("/api/services/<int:service_id>", methods=["DELETE"])
def eliminar_servicio(service_id):
    user_id = session.get("user_id")
    servicio = Service.query.get(service_id)

    if not servicio or servicio.user_id != user_id:
        return jsonify({"message": "No autorizado"}), 403

    db.session.delete(servicio)
    db.session.commit()
    return jsonify({"message": "Servicio eliminado"}), 200

# Servir imágenes
@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Ejecutar servidor
if __name__ == "__main__":
    app.run(debug=True)