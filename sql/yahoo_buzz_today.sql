WITH todays_buzz AS (
    SELECT
        player,
        buzz_index,
        adds,
        adds_per_minute,
        time_fetched
    FROM yahoo_buzz_adds
    WHERE
        buzz_index <= 10
        AND adds_per_minute >= 10
        AND DATE(time_fetched) = CURDATE()
)
SELECT
	player,
	MAX(buzz_index) AS max_buzz_index,
	MAX(adds) AS max_daily_adds,
	MAX(adds_per_minute) AS max_daily_apm
FROM todays_buzz
GROUP BY player
ORDER BY
	max_daily_adds DESC,
	max_daily_apm DESC