WITH previous AS (
	SELECT
		player,
		time_fetched,
		adds,
	    buzz_index,
		LAG(adds) OVER (
			PARTITION BY player
			ORDER BY time_fetched) AS prev_adds,
		LAG(time_fetched) OVER (
		    PARTITION BY player
		    ORDER BY time_fetched) AS prev_time_fetched
	FROM yahoo_buzz
),
diff AS (
	SELECT
		player,
	    buzz_index,
		adds,
		prev_adds,
		adds - prev_adds AS adds_since_last_fetch,
		ROUND((adds - prev_adds) / adds * 100, 2) AS pct_change_from_prev,
		prev_time_fetched,
		TIMESTAMPDIFF(SECOND, prev_time_fetched, time_fetched) AS seconds_since_last_fetch,
		ROUND(TIMESTAMPDIFF(SECOND, prev_time_fetched, time_fetched) / 60, 2) AS minutes_since_last_fetch,
		time_fetched
	FROM previous AS p
)
SELECT
	player,
    buzz_index,
	adds,
	prev_adds,
	adds_since_last_fetch,
	pct_change_from_prev,
	ROUND(adds_since_last_fetch / minutes_since_last_fetch, 2) AS adds_per_minute,
	prev_time_fetched,
	seconds_since_last_fetch,
	minutes_since_last_fetch,
	time_fetched
FROM diff