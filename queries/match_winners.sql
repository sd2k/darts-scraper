SELECT p.name AS player_name,
    e.name AS event_name,
    m.date,
    m.id,
    CASE WHEN score >= MAX(score) OVER (PARTITION BY match_id) THEN 'won' ELSE 'lost' END AS won, 
    score, 
    average, 
    oneeighties, 
    high_checkout, 
    checkout_percent,
    checkout_chances
FROM players p
JOIN match_results mr ON p.id = mr.player_id
JOIN matches m ON mr.match_id = m.id
JOIN events e ON m.event_id = e.id 
ORDER BY date, match_id, won DESC;

