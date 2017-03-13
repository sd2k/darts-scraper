import flask
import flask.views
from flask_paginate import Pagination
from flask_sqlalchemy_session import current_session

from darts import models, settings, sim
from .extensions import nav
from .forms import ProfileForm, PlayerSimulationForm


interface = flask.Blueprint('interface', __name__)


@interface.before_request
def add_navigation():
    nav.Bar('top_left', [
        nav.Item('Home', 'interface.index'),
        nav.Item('Player Simulations', 'interface.list_player_simulations'),
        nav.Item('Profiles', 'interface.list_profiles'),
        nav.Item('Players', 'interface.list_players')
    ])

    nav.Bar('top_right', [
        nav.Item('Admin', 'admin.index'),
    ])


@interface.route('/')
def index():
    return flask.render_template('index.html')


@interface.route('/playersimulations/', methods=['GET', 'POST'])
def list_player_simulations():

    page = flask.request.args.get('page', type=int, default=1)

    query = current_session.query(models.PlayerSimulation)

    simulations = (
        query.offset(settings.SIMULATIONS_PER_PAGE * (page - 1))
        .limit(settings.SIMULATIONS_PER_PAGE)
    )

    pagination = Pagination(
        page=page,
        per_page=settings.SIMULATIONS_PER_PAGE,
        total=query.count(),
        )

    form = PlayerSimulationForm()

    form.profile_id.choices = [
        (profile.id, str(profile))
        for profile in current_session.query(models.Profile)
    ]

    if form.validate_on_submit():
        form_data = form.data.copy()
        form_data.pop('csrf_token', None)
        profile = (
            current_session.query(models.Profile)
            .filter(models.Profile.id == form_data['profile_id'])
            .one()
        )
        lookups = sim.load_lookups(current_session)
        simulation = models.PlayerSimulation(
            profile=profile,
            iterations=form_data['iterations'],
        )
        sim_results = sim.simulate_profile(
            profile,
            *lookups,
            iterations=form_data['iterations']
        )
        simulation.results = [
            leg.as_dict()
            for leg in sim_results
        ]
        simulation.stats = simulation.create_stats(simulation.results)

        current_session.add(simulation)
        current_session.commit()
        return flask.redirect(
            flask.url_for('.view_player_simulation', id=simulation.id)
        )

    return flask.render_template(
        'list_player_simulations.html',
        form=form,
        pagination=pagination,
        simulations=simulations,
        show_modal=flask.request.method == 'POST',
    ), 200 if flask.request.method == 'GET' else 400


@interface.route('/playersimulations/<int:id>/')
def view_player_simulation(id):
    simulation = (
        current_session.query(models.PlayerSimulation)
        .filter(models.PlayerSimulation.id == id)
        .one()
    )
    return flask.render_template(
        'view_player_simulation.html',
        simulation=simulation,
    )



@interface.route('/profiles/', methods=['GET', 'POST'])
def list_profiles():

    page = flask.request.args.get('page', type=int, default=1)

    query = current_session.query(models.Profile)

    profiles = (
        query.offset(settings.PROFILES_PER_PAGE * (page - 1))
        .limit(settings.PROFILES_PER_PAGE)
    )

    pagination = Pagination(
        page=page,
        per_page=settings.PROFILES_PER_PAGE,
        total=query.count(),
        record_name='profiles',
        css_framework='bootstrap3',
    )

    form = ProfileForm()

    if form.validate_on_submit():
        data = form.data.copy()
        data.pop('csrf_token', None)
        profile = models.Profile(**data)
        current_session.add(profile)
        current_session.commit()
        return flask.redirect(flask.url_for('.view_profile', id=profile.id))

    return flask.render_template(
        'list_profiles.html',
        form=form,
        pagination=pagination,
        profiles=profiles,
        show_modal=flask.request.method == 'POST',
    ), 200 if flask.request.method == 'GET' else 400


@interface.route('/profiles/<int:id>/')
def view_profile(id):
    profile = (
        current_session.query(models.Profile)
        .filter(models.Profile.id == id)
        .one()
    )
    return flask.render_template('view_profile.html', profile=profile)


@interface.route('/players/')
def list_players():

    page = flask.request.args.get('page', type=int, default=1)
    query = (
        current_session.query(models.Player)
        .order_by(models.Player.pdc_ranking, models.Player.name)
    )
    players = (
        query.offset(settings.PROFILES_PER_PAGE * (page - 1))
        .limit(settings.PROFILES_PER_PAGE)
    )

    pagination = Pagination(
        page=page,
        per_page=settings.PROFILES_PER_PAGE,
        total=query.count(),
        record_name='players',
        css_framework='bootstrap3',
    )

    return flask.render_template(
        'list_players.html',
        pagination=pagination,
        players=players,
    )


@interface.route('/players/<int:id>/')
def view_player(id):
    player = (
        current_session.query(models.Player)
        .filter(models.Player.id == id)
        .one()
    )
    return flask.render_template('view_player.html', player=player)
