from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField
from wtforms.validators import InputRequired, NumberRange, ValidationError


def validate_trebles(form, field):
    total = (
        form.treble_hit_pct.data +
        form.treble_miss_pct.data +
        form.treble_big_miss_pct.data
    )
    if total != 100:
        raise ValidationError('Treble percentages must sum to 100%')


def validate_bullseyes(form, field):
    total = (
        form.bullseye_hit_pct.data +
        form.bullseye_miss_pct.data
    )
    if total != 100:
        raise ValidationError('Bullseye percentages must sum to 100%')


def validate_outer_bulls(form, field):
    total = (
        form.outer_bull_hit_pct.data +
        form.outer_bull_miss_pct.data
    )
    if total != 100:
        raise ValidationError('Outer bull percentages must sum to 100%')


def validate_doubles(form, field):
    total = (
        form.double_hit_pct.data +
        form.double_miss_inside_pct.data +
        form.double_miss_outside_pct.data
    )
    if total != 100:
        raise ValidationError('Treble percentages must sum to 100%')


class ProfileForm(FlaskForm):

    name = StringField('Name', validators=[InputRequired()])

    treble_hit_pct = DecimalField(
        'Treble Hit Percentage',
        validators=[NumberRange(0, 100), InputRequired(), validate_trebles],
    )
    treble_miss_pct = DecimalField(
        'Treble Miss Percentage',
        validators=[NumberRange(0, 100), InputRequired(), validate_trebles],
    )
    treble_big_miss_pct = DecimalField(
        'Treble Big Miss Percentage',
        validators=[NumberRange(0, 100), InputRequired(), validate_trebles],
    )

    bullseye_hit_pct = DecimalField(
        'Bullseye Hit Percentage',
        validators=[NumberRange(0, 100), InputRequired(), validate_bullseyes],
    )
    bullseye_miss_pct = DecimalField(
        'Bullseye Miss Percentage',
        validators=[NumberRange(0, 100), InputRequired(), validate_bullseyes],
    )

    outer_bull_hit_pct = DecimalField(
        'Outer Bull Hit Percentage',
        validators=[NumberRange(0, 100), InputRequired(), validate_outer_bulls],  # noqa
    )
    outer_bull_miss_pct = DecimalField(
        'Outer Bull Miss Percentage',
        validators=[NumberRange(0, 100), InputRequired(), validate_outer_bulls],  # noqa
    )

    double_hit_pct = DecimalField(
        'Double Hit Percentage',
        validators=[NumberRange(0, 100), InputRequired(), validate_doubles],
    )
    double_miss_inside_pct = DecimalField(
        'Double Miss Inside Percentage',
        validators=[NumberRange(0, 100), InputRequired(), validate_doubles],
    )
    double_miss_outside_pct = DecimalField(
        'Double Miss Outside Percentage',
        validators=[NumberRange(0, 100), InputRequired(), validate_doubles],
    )
