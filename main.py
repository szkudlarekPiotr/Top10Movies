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
OMDB_ENDPOINT = os.environ["OMDB_ENDPOINT"]
OMDB_KEY = os.environ["OMDB_KEY"]

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DB_URI"]
app.config["SECRET_KEY"] = SECRET_KEY
Bootstrap5(app)
db.init_app(app)


@app.route("/")
def home():
    movies = list(db.session.execute(db.select(Movie).order_by(Movie.rating)).scalars())
    return render_template("index.j2", movies=movies)


@app.route("/add", methods=["GET", "POST"])
def add():
    add_form = AddForm()
    if request.args.get("movie", False) and request.args.get("imdb_id", False):
        movie = request.args["movie"]
        imdb_id = request.args["imdb_id"]
        try:
            plot_response = requests.get(
                url=OMDB_ENDPOINT, params={"apikey": OMDB_KEY, "i": imdb_id}
            )
            plot_response.raise_for_status()
        except (RequestException, HTTPError) as e:
            print(f"Error: {e.args}")
            abort(404)
        plot = plot_response.json()
        movie_dict = ast.literal_eval(movie)
        temp_movie = Movie(
            title=movie_dict["Title"],
            release_date=int(movie_dict["Year"]),
            img_url=movie_dict["Poster"],
            description=plot["Plot"],
        )
        db.session.add(temp_movie)
        try:
            db.session.commit()
        except exc.SQLAlchemyError as e:
            print(f"Error: {e.args}")
            abort(404)
        id = db.session.execute(
            db.Select(Movie.id).where(Movie.title == temp_movie.title)
        ).scalar()
        return redirect(url_for("update", id=id))
    else:
        if request.method == "POST":
            if add_form.validate_on_submit():
                data_params = {"apikey": OMDB_KEY, "s": add_form.title.data}
                try:
                    data_response = requests.get(url=OMDB_ENDPOINT, params=data_params)
                    data_response.raise_for_status()
                except (RequestException, HTTPError) as e:
                    print(f"Error: {e.args}")
                    abort(404)
                results = data_response.json()
                return render_template("select.j2", movies=results)
            else:
                return render_template("add.j2", form=add_form)
        else:
            return render_template("add.j2", form=add_form)


@app.route("/update", methods=["GET", "POST"])
def update():
    form = RatingForm()
    id = request.args["id"]
    movie = db.get_or_404(Movie, id)
    if request.method == "POST":
        if form.validate_on_submit():
            movie.rating = form.rating.data
            movie.comment = form.comment.data
            try:
                db.session.commit()
            except exc.SQLAlchemyError as e:
                print(f"Error {e.args}")
                abort(404)
            return redirect(url_for("home"))
        else:
            return render_template("edit.j2", form=form, id=id, title=movie.title)
    else:
        return render_template("edit.j2", form=form, id=id, title=movie.title)


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
