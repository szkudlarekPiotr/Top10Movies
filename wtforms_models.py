from wtforms import StringField, SubmitField, IntegerField, TextAreaField, DateField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm


class AddForm(FlaskForm):
    title = StringField("Movie title", validators=[DataRequired()])
    release_date = IntegerField("Release date", validators=[DataRequired()])
    rating = IntegerField("Rating out of 10", validators=[DataRequired()])
    comment = StringField("Review", validators=[DataRequired()])
    description = TextAreaField("Movie description", validators=[DataRequired()])
    submit = SubmitField("Submit")
