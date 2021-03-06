from flask_admin import Admin, AdminIndexView
from flask_admin.base import MenuLink
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy_session import current_session

from darts import models


class NonEditableModelView(ModelView):

    can_export = True
    can_view_details = True

    can_create = False
    can_delete = False
    can_edit = False


class PlayerView(NonEditableModelView):

    column_default_sort = 'pdc_ranking'

    column_labels = dict(
        name='Name',
        pdc_ranking='PDC Ranking',
        ddb_ranking='DDB Ranking',
        career_earnings='Career Earnings',
        career_9_darters='Career 9 darters',
        red_dragon_ranking='Red Dragon Ranking',
        ddb_popularity='DDB Popularity',
    )
    column_list = [
        'name',
        'pdc_ranking',
        'ddb_ranking',
        'career_9_darters',
        'career_earnings',
        'red_dragon_ranking',
        'ddb_popularity',
    ]
    column_filters = [
        'name',
        'pdc_ranking',
        'ddb_ranking',
        'career_earnings',
        'career_9_darters',
        'match_results',
    ]


class ScoreLookupView(ModelView):

    column_list = [
        'score',
        'dart',
        'shot_type',
        'hit_points',
        'miss_points',
        'big_miss_points',
    ]


class MatchView(NonEditableModelView):

    can_view_details = True
    can_edit = False

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


class MatchResultView(NonEditableModelView):

    can_view_details = True
    can_edit = False

    column_filters = [
        'player',
        'match',
        'score',
        'average',
        'oneeighties',
        'high_checkout',
        'checkout_percent',
        'checkout_chances',
    ]


admin = Admin(
    name='Darts Simulator - Admin',
    template_mode='bootstrap3',
    index_view=AdminIndexView(),
)

admin.add_view(ModelView(
    models.Profile,
    current_session,
    name='Profiles',
    endpoint='profiles',
))
admin.add_view(ScoreLookupView(
    models.ScoreLookup,
    current_session,
    name='Score Lookup',
    endpoint='scorelookups',
))
admin.add_view(PlayerView(
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
admin.add_view(NonEditableModelView(
    models.Event,
    current_session,
    name='Events',
    endpoint='events',
))
admin.add_view(NonEditableModelView(
    models.Tournament,
    current_session,
    name='Tournaments',
    endpoint='tournaments',
))

admin.add_link(MenuLink(name='Back To Simulator', endpoint='interface.index'))
