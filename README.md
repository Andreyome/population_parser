# Country Population Scraper

## Technologies Used
| Backend        | Database               | Infrastructure |
|----------------|:-----------------------|----------------|
| Python 3.12    | PostgreSQL 16 (Alpine) | Docker         |
| SQLAlchemy     |                        |                |
| requests       |                        |                |
| BeautifulSoup4 |                        |                |

## How to run:

```bash
git clone https://github.com/Andreyome/population_parser.git
docker-compose up get_data 
docker-compose up print_data
```
## To stop and remove containers:

```bash
docker compose down
```