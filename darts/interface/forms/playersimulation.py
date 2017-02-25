from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField
from wtforms.validators import InputRequired, NumberRange


class PlayerSimulationForm(FlaskForm):

    profile_id = SelectField('Profile', coerce=int)

    iterations = IntegerField(
        'Iterations',
        default=1000,
        validators=[NumberRange(100, 100000), InputRequired()],
    )
