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
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    rol = user.rol

    if user and data['password'] == user.password:
        return jsonify({
            'message': 'Inicio de sesión exitoso',
            'rol': rol
        }), 200
    return jsonify({"error": "Credenciales inválidas"}), 401


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
