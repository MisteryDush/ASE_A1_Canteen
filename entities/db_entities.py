from flask_sqlalchemy import SQLAlchemy



class Stall(db.Model):
    __tablename__ = 'stalls'
    stall_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=30))

    def __init__(self, name):
        self.name = name
