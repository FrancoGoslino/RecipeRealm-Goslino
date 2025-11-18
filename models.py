from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()

class Alumno(db.Model):
    __tablename__='alumnos'
    id=db.Column(db.Integer, primary_key=True)
    nombre=db.Column(db.String(80),nullable=False)
    apellido=db.Column(db.String(80), nullable=False)
    email=db.Column(db.String(80), nullable=False)


    def __repr__(self):
        return f'ALumno {self.nombre} {self.apellido}'
    
    