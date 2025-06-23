from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    secret = db.Column(db.String(200), nullable=False)
    active = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<User {self.username}>'
