SELECT player_name,
    SUM(oneeighties) AS oneeighties,
    SUM(legs) AS legs,
    CAST(SUM(oneeighties) AS FLOAT) / CAST(SUM(legs) AS FLOAT) AS oneeighties_per_leg
FROM (
    SELECT
        t.id AS tournament_id,
        t.name AS tournament_name,
        e.name AS event_name,
        p.name AS player_name,
        m.date,
        mr.oneeighties,
        legs,
        CAST(mr.oneeighties AS FLOAT) / CAST(legs AS FLOAT) AS oneeighties_per_leg
    FROM match_results mr
    JOIN players p ON mr.player_id = p.id
    JOIN (
        SELECT m.id, m.event_id, m.date, SUM(mr.score) AS legs
        FROM matches m
        JOIN match_results mr ON m.id = mr.match_id
        GROUP BY m.id
    ) AS m ON mr.match_id = m.id
    JOIN events e ON m.event_id = e.id
    JOIN tournaments t ON e.tournament_id = t.id
    WHERE m.date > '2015-01-01'
        AND t.id NOT IN (
        11, -- PDC World Championship (sets not legs)
        14  -- World Grand Prix (must start on double)
    )
) recent
GROUP BY player_name;
