SELECT last_10.player_id,
    p.name,
    pdc_ranking, 
    AVG(average) AS average,
    AVG(CAST(high_checkout AS FLOAT)) AS high_checkout
FROM (
    SELECT *
    FROM (
        SELECT mr.*,
	    row_number() OVER (PARTITION BY pdc_ranking ORDER BY date DESC)
	FROM match_results mr
	JOIN players p ON mr.player_id = p.id
	JOIN matches m ON mr.match_id = m.id
	WHERE average IS NOT NULL
	    AND high_checkout IS NOT NULL
    ) AS a
    WHERE row_number <= 10
) as last_10
JOIN players p ON last_10.player_id = p.id
GROUP BY player_id, p.name, pdc_ranking
ORDER BY high_checkout DESC;
