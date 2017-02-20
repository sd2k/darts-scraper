import flask
import flask.views
from flask_paginate import Pagination
from flask_sqlalchemy_session import current_session

from darts import models, settings, sim
from .extensions import nav
from .forms import ProfileForm


interface = flask.Blueprint('interface', __name__)


@interface.before_request
def add_navigation():
    nav.Bar('top_left', [
        nav.Item('Home', 'interface.index'),
        nav.Item('Simulations', 'interface.list_simulations'),
        nav.Item('Profiles', 'interface.list_profiles')
    ])

    nav.Bar('top_right', [
        nav.Item('Admin', 'admin.index'),
    ])


@interface.route('/')
def index():
    return flask.render_template('index.html')


class SimulationView(flask.views.MethodView):

    def get(self):

        page = flask.request.args.get('page', type=int, default=1)

        query = current_session.query(models.Simulation)

        simulations = (
            query.offset(settings.SIMULATIONS_PER_PAGE * (page - 1))
            .limit(settings.SIMULATIONS_PER_PAGE)
        )

        pagination = Pagination(
            page=page,
            per_page=settings.SIMULATIONS_PER_PAGE,
            total=query.count(),
            record_name='simulations',
            css_framework='bootstrap3',
        )

        return flask.render_template(
            'list_simulations.html',
            pagination=pagination,
            simulations=simulations,
        )

    def post(self):
        sim_details = flask.request.form.as_dict()
        profile = (
            current_session.query(models.Profile)
            .filter(models.Profiles.id == sim_details['profile_id'])
            .one()
        )
        lookups = sim.load_lookups(current_session)
        simulation = models.Simulation(
            profile=profile,
            iterations=sim_details['iterations'],
        )
        simulation.results = sim.simulate_profile(profile, *lookups)
        current_session.add(simulation)
        current_session.commit()

        return flask.redirect(
            flask.url_for('.view_simulation', id=simulation.id)
        )


interface.add_url_rule(
    '/simulations/',
    view_func=SimulationView.as_view('list_simulations'),
)


@interface.route('/simulations/<int:id>/')
def view_simulation(id):
    return flask.render_template('view_simulation.html')


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
        show_modal=flask.request.method == "POST",
    ), 200 if flask.request.method == "GET" else 400


@interface.route('/profiles/<int:id>/')
def view_profile(id):
    profile = (
        current_session.query(models.Profile)
        .filter(models.Profile.id == id)
        .one()
    )
    return flask.render_template('view_profile.html', profile=profile)
