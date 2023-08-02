from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm


class AddForm(FlaskForm):
    title = StringField("Movie title", validators=[DataRequired()])
    submit = SubmitField("Submit")


class RatingForm(FlaskForm):
    rating = FloatField("Movie rating out of 10", validators=[DataRequired()])
    comment = StringField("Review", validators=[DataRequired()])
    submit = SubmitField("Submit")
