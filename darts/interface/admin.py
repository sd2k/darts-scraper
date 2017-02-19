from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy_session import current_session

from darts import models


class MatchView(ModelView):

    can_view_details = True

    column_list = [
        'name',
        'date',
        'event',
    ]
    column_filters = [
        'date',
        'event',
        'match_results'
    ]


class MatchResultView(ModelView):

    can_view_details = True
    column_filters = [
        'player',
        'score',
        'average',
        'oneeighties',
        'high_checkout',
        'checkout_percent',
        'checkout_chances',
    ]


admin = Admin(
    name='Darts Simulator',
    template_mode='bootstrap3',
    index_view=AdminIndexView(),
)

admin.add_view(ModelView(
    models.Profile,
    current_session,
    name='Profiles',
    endpoint='profiles',
))
admin.add_view(ModelView(
    models.Player,
    current_session,
    name='Players',
    endpoint='players',
))
admin.add_view(MatchView(
    models.Match,
    current_session,
    name='Matches',
    endpoint='matches',
))
admin.add_view(MatchResultView(
    models.MatchResult,
    current_session,
    name='Match Results',
    endpoint='matchresults',
))
admin.add_view(ModelView(
    models.Event,
    current_session,
    name='Events',
    endpoint='events',
))
admin.add_view(ModelView(
    models.Tournament,
    current_session,
    name='Tournaments',
    endpoint='tournaments',
))
