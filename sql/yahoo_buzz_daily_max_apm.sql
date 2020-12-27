WITH max_adds_per_player AS (
	SELECT
		player,
		DATE(time_fetched) AS date,
		MAX(adds_per_minute) AS daily_max_adds_per_minute
	FROM yahoo_buzz_adds
	GROUP BY
		player,
		date
	ORDER BY daily_max_adds_per_minute DESC
),
rank_tbl AS (
	SELECT
		player,
		daily_max_adds_per_minute,
		date,
		RANK() OVER (
			PARTITION BY date
			ORDER BY(daily_max_adds_per_minute) DESC
			) AS daily_rank
	FROM max_adds_per_player
)
SELECT
	rt.*,
	yba.time_fetched
FROM rank_tbl AS rt
JOIN yahoo_buzz_adds AS yba ON rt.player = yba.player
AND rt.daily_max_adds_per_minute = yba.adds_per_minute
WHERE daily_rank <= 10
ORDER BY daily_max_adds_per_minute DESC