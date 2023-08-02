from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired, NumberRange
from flask_wtf import FlaskForm


class AddForm(FlaskForm):
    title = StringField("Movie title", validators=[DataRequired()])
    submit = SubmitField("Submit")


class RatingForm(FlaskForm):
    rating = FloatField(
        "Movie rating out of 10",
        validators=[DataRequired(), NumberRange(0, 10, "Please insert 1-10 number")],
    )
    comment = StringField("Review", validators=[DataRequired()])
    submit = SubmitField("Submit")
