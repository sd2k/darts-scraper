SELECT *
FROM (
    SELECT p.name,
        p.id AS player_id,
        m.id AS match_id,
    	m.date AS date,
        p.pdc_ranking,
        e.prize_fund,
        mr.score,
        m.legs,
        mr.average,
        mr.oneeighties,
        mr.checkout_percent,
        mr.checkout_chances,
        row_number() OVER (PARTITION BY p.pdc_ranking ORDER BY m.date DESC)
    FROM match_results mr
    JOIN players p ON mr.player_id = p.id
    JOIN (
        SELECT m.id, m.event_id, m.date, SUM(mr.score) AS legs
        FROM matches m
        JOIN match_results mr ON mr.match_id = m.id
        GROUP BY m.id
    ) AS m ON mr.match_id = m.id
    JOIN events e ON m.event_id = e.id
    WHERE average IS NOT NULL
        AND high_checkout IS NOT NULL
) AS a
WHERE row_number <= 10
ORDER BY pdc_ranking, row_number;
