# Fantasy Basketball Scraper
This repo contains Python scripts to fetch Fantasy Basketball data from Yahoo and ESPN. 

An email alert is sent for these cases:
1. When a player is buzzing on [Yahoo Transaction Trends](https://basketball.fantasysports.yahoo.com/nba/buzzindex).
2. When a highly-owned player is a free agent in an [ESPN league](https://fantasy.espn.com/basketball/).

The scripts are scheduled using [Hickory](https://github.com/maxhumber/hickory).

## Tools & Libraries
- MySQL 8
- Firefox browser & [geckodriver](https://selenium-python.readthedocs.io/installation.html#drivers)

Python libraries
- gazpacho=1.1
- hickory=1.0
- pandas=1.1.3
- selenium=3.141.0
- sqlalchemy=1.3
- yagmail=0.14.245

## Meta
Author: Miguel Corral Jr.  
Email: corraljrmiguel@gmail.com  
LinkedIn: https://www.linkedin.com/in/miguelcorraljr/  
GitHub: https://github.com/corralm

Distributed under the MIT License. See [LICENSE](./LICENSE) for more information.
