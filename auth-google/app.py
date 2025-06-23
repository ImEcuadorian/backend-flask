import os, io, base64
from flask import Flask, request, jsonify, abort, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import pyotp, qrcode

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False



db = SQLAlchemy(app)

class User(db.Model):
    id      = db.Column(db.Integer, primary_key=True)
    secret  = db.Column(db.String(100), nullable=True)
    active  = db.Column(db.Boolean, default=False)
def create_tables():
    db.create_all()

with app.app_context():
    create_tables()

CORS(app, origins="*")



def get_user_or_404(user_id: str):
    user = User.query.get(user_id)
    if not user:
        abort(404, description="User not found")
    return user

@app.route("/register-2fa/<user_id>", methods=["POST"])
def register_2fa(user_id):
    user = User.query.get(user_id) or User(id=user_id)
    if not user.secret:
        user.secret = pyotp.random_base32()
    user.active = True
    db.session.add(user)
    db.session.commit()

    uri = pyotp.TOTP(user.secret).provisioning_uri(
        name=user_id,
        issuer_name="MyAwesomeService"
    )

    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    qr_b64 = base64.b64encode(buf.getvalue()).decode()
    buf.close()

    return jsonify({
        "provisioning_uri": uri,
        "qr_code_base64": qr_b64
    })

@app.route("/verify-2fa", methods=["POST"])
def verify_2fa():
    data    = request.get_json() or {}
    user_id = data.get("user_id")
    code    = data.get("code")
    if not user_id or not code:
        abort(400, description="user_id and code required")

    user = get_user_or_404(user_id)
    if not user.active or not user.secret:
        abort(400, description="2FA not configured")

    verified = pyotp.TOTP(user.secret).verify(code)
    return jsonify({"verified": verified})

@app.route("/qr-code/<user_id>")
def qr_code(user_id):
    user = get_user_or_404(user_id)
    if not user.active or not user.secret:
        abort(404, description="2FA not configured")

    uri = pyotp.TOTP(user.secret).provisioning_uri(
        name=user_id,
        issuer_name="MyAwesomeService"
    )
    qr  = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)
    img = qr.make_image()

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

@app.route("/2fa-status/<user_id>", methods=["GET"])
def status_2fa(user_id):
    user = get_user_or_404(user_id)
    return jsonify({"active": bool(user.active)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)
