from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    rating = db.Column(db.Float)
    comment = db.Column(db.String)
    description = db.Column(db.String)
    release_date = db.Column(db.Integer)
    img_url = db.Column(db.String)
