from darts import models, sim
from darts.db import Session


s = Session()


def run_one_player_sim(
        sim_id,
        profile,
        score_shot_types,
        score_points,
        **kwargs
        ):

    sim_results = sim.oneplayer.simulate_profile(
        profile,
        score_shot_types,
        score_points,
        )

    simulation = (
        s.query(models.PlayerSimulation)
        .filter(models.PlayerSimulation.id == sim_id)
        .one()
    )

    simulation.results = [
        leg.as_dict()
        for leg in sim_results
    ]
    simulation.stats = simulation.create_stats(simulation.results)
    s.add(simulation)
    s.commit()


def run_two_player_sim(sim_id, **kwargs):

    sim_results = sim.twoplayer.simulate_match(**kwargs)

    simulation = (
        s.query(models.MatchSimulation)
        .filter(models.MatchSimulation.id == sim_id)
        .one()
    )

    simulation.results = [match.as_dict() for match in sim_results]
    simulation.stats = simulation.create_stats(simulation.results)

    s.add(simulation)
    s.commit()
