from sqlalchemy import func
from sqlalchemy.orm import aliased
from database.database import SessionLocal, init_db
from models.models import Country
from utils.wait_for_db import wait_for_db


class PrintDataService:
    def __init__(self):
        init_db()

    def run(self):
        session = SessionLocal()
        try:
            pre_query = (
                session.query(
                    Country.region,
                    func.sum(Country.population).label("total_population"),
                    func.max(Country.population).label("max_population"),
                    func.min(Country.population).label("min_population")
                )
                .group_by(Country.region)
                .subquery()
            )

            largest_country = aliased(Country)
            smallest_country = aliased(Country)

            query = (
                session.query(
                    pre_query.columns.region,
                    pre_query.columns.total_population,
                    largest_country.name.label("largest_name"),
                    pre_query.columns.max_population,
                    smallest_country.name.label("smallest_name"),
                    pre_query.columns.min_population
                )
                .join(
                    largest_country,
                    (largest_country.region == pre_query.columns.region) &
                    (largest_country.population == pre_query.columns.max_population)
                )
                .join(
                    smallest_country,
                    (smallest_country.region == pre_query.columns.region) &
                    (smallest_country.population == pre_query.columns.min_population)
                )
                .order_by(pre_query.columns.region)
            )

            results = query.all()

            for row in results:
                print(f"Назва регіону: {row.region}")
                print(f"Загальне населення регіону: {row.total_population:,}")
                print(f"Назва найбільшої країни в регіоні (за населенням): {row.largest_name}")
                print(f"Населення найбільшої країни в регіоні: {row.max_population:,}")
                print(f"Назва найменшої країни в регіоні: {row.smallest_name}")
                print(f"Населення найменшої країни в регіоні: {row.min_population:,}")
                print("")

        finally:
            session.close()


if __name__ == "__main__":
    wait_for_db()
    PrintDataService().run()
