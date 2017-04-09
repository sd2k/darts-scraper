from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, SelectField
from wtforms.validators import InputRequired, NumberRange, ValidationError


class MatchSimulationForm(FlaskForm):

    match_type = SelectField(
        'MatchType',
        choices=[
            ('match_play', 'Match Play'),
            ('set_play', 'Set Play'),
            ('premier_league', 'Premier League'),
        ],
    )

    profile_a_id = SelectField('Player 1 profile', coerce=int)
    profile_b_id = SelectField('Player 2 profile', coerce=int)

    total_legs = IntegerField(
        'Match Play only - number of legs per match',
        default=None,
    )
    total_sets = IntegerField(
        'Set play only - number of sets required to win match',
        default=5,
    )

    a_first = BooleanField('Player 1 throws first', default=True)

    iterations = IntegerField(
        'Iterations',
        default=1000,
        validators=[NumberRange(100, 5000), InputRequired()],
    )

    a_handicap = IntegerField(
        'Player 1 handicap',
        default=0,
        validators=[NumberRange(-10, 10), InputRequired()],
    )
    b_handicap = IntegerField(
        'Player 2 handicap',
        default=0,
        validators=[NumberRange(-10, 10), InputRequired()],
    )

    def validate_profile_b_id(form, field):
        profile_a_id = form.data['profile_a_id']
        profile_b_id = field.data

        if profile_a_id == profile_b_id:
            raise ValidationError("Can't simulate two identical profiles")
