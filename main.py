from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from wtforms_models import AddForm
from database_models import Movie, db
import requests
import os

SECRET_KEY = os.urandom(32)

app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://postgres:admin@localhost:5433/movies"
app.config["SECRET_KEY"] = SECRET_KEY
Bootstrap5(app)
db.init_app(app)


@app.route("/")
def home():
    movies = list(db.session.execute(db.select(Movie)).scalars())
    return render_template("index.j2", movies=movies)


@app.route("/add", methods=["GET", "POST"])
def add():
    form = AddForm()
    if request.method == "POST":
        if form.validate_on_submit():
            movie = Movie(
                title=form.title.data,
                release_date=form.release_date.data,
                rating=form.rating.data,
                comment=form.comment.data,
                description=form.description.data,
            )
            db.session.add(movie)
            db.session.commit()
            return redirect(url_for("home"))
        else:
            return render_template("add.j2", form=form)
    else:
        return render_template("add.j2", form=form)


@app.route("/update", methods=["GET", "POST"])
def update():
    id = request.args.get("id")
    movie = db.get_or_404(Movie, id)
    return render_template("edit.j2", movie=movie)


@app.route("/delete")
def delete():
    id = request.args.get("id")
    movie = db.get_or_404(Movie, id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for("home"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
