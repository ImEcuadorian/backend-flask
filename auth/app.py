from flask import Flask, request, jsonify
from flask_cors import CORS

from models import db, User
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

CORS(app, origins="*")

with app.app_context():
    db.create_all()

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    pwd   = data.get('password')

    if not email or not pwd:
        return jsonify({'error': 'Email y contraseña son requeridos'}), 400

    user = User.query.filter_by(email=email).first()

    if not user or user.password != pwd:
        return jsonify({'error': 'Credenciales inválidas'}), 401

    return jsonify({
        'message': 'Inicio de sesión exitoso',
        'rol':     user.rol,
        'id':      user.id
    }), 200



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
