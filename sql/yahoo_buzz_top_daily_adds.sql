WITH max_adds_per_player AS (
	SELECT
		player,
		DATE(time_fetched) AS date,
		MAX(adds) AS max_adds
	FROM yahoo_buzz
	GROUP BY
		player,
		date
	ORDER BY max_adds DESC
),
rank_tbl AS (
	SELECT
		player,
		max_adds,
		date,
		RANK() OVER (
			PARTITION BY date
			ORDER BY(max_adds) DESC
			) AS daily_rank
	FROM max_adds_per_player
)
SELECT *
FROM rank_tbl
WHERE daily_rank <= 10
ORDER BY date DESC