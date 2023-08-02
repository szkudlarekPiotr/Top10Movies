from flask import Flask, render_template, redirect, url_for, request, abort
from flask_bootstrap import Bootstrap5
from wtforms_models import AddForm, RatingForm
from database_models import Movie, db
from sqlalchemy import exc
import requests
from requests.exceptions import RequestException, HTTPError
import ast
import os

SECRET_KEY = os.urandom(32)
OMDB_ENDPOINT = "http://www.omdbapi.com/"
OMDB_KEY = os.environ["OMDB_KEY"]

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DB_URI"]
app.config["SECRET_KEY"] = SECRET_KEY
Bootstrap5(app)
db.init_app(app)


def get_request(params):
    params = params
    try:
        response = requests.get(url=OMDB_ENDPOINT, params=params)
        response.raise_for_status()
        return response.json()
    except (RequestException, HTTPError) as e:
        print(f"Error: {e.args}")
        abort(404)


@app.route("/")
def home():
    movies = list(db.session.execute(db.select(Movie).order_by(Movie.rating)).scalars())
    return render_template("index.j2", movies=movies)


@app.route("/add", methods=["GET", "POST"])
def add():
    add_form = AddForm()
    movie = request.args.get("movie", False)
    imdb_id = request.args.get("imdb_id", False)
    if not movie or not imdb_id:
        if request.method != "POST" or not add_form.validate_on_submit():
            return render_template("add.j2", form=add_form)
        else:
            data_params = {"apikey": OMDB_KEY, "s": add_form.title.data}
            results = get_request(data_params)
            return render_template("select.j2", movies=results)
    else:
        movie_dict = ast.literal_eval(movie)
        params = {"apikey": OMDB_KEY, "i": imdb_id}
        plot = get_request(params)
        new_movie = Movie(
            title=movie_dict["Title"],
            release_date=int(movie_dict["Year"]),
            img_url=movie_dict["Poster"],
            description=plot["Plot"],
        )
        db.session.add(new_movie)
        try:
            db.session.commit()
            id = db.session.execute(
                db.Select(Movie.id).where(Movie.title == new_movie.title)
            ).scalar()
        except exc.SQLAlchemyError as e:
            print(f"Error: {e.args}")
            abort(404)
        return redirect(url_for("update", id=id))


@app.route("/update", methods=["GET", "POST"])
def update():
    form = RatingForm()
    id = request.args["id"]
    movie = db.get_or_404(Movie, id)
    if not form.validate_on_submit():
        return render_template("edit.j2", form=form, id=id, title=movie.title)
    else:
        movie.rating = form.rating.data
        movie.comment = form.comment.data
        try:
            db.session.commit()
        except exc.SQLAlchemyError as e:
            print(f"Error {e.args}")
            abort(404)
        return redirect(url_for("home"))


@app.route("/delete")
def delete():
    id = request.args["id"]
    movie = db.get_or_404(Movie, id)
    db.session.delete(movie)
    try:
        db.session.commit()
    except exc.SQLAlchemyError as e:
        print(f"Error {e.args}")
        abort(404)
    return redirect(url_for("home"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
