import asyncio

from sqlalchemy import func, select
from sqlalchemy.orm import aliased
from database import SessionLocal, init_db
from models import Country


class PrintDataService:
    async def run(self):
        await init_db()
        async with SessionLocal() as session:
            largest_country = aliased(Country)
            smallest_country = aliased(Country)
            pre_query = (
                select(
                    Country.region,
                    func.sum(Country.population).label("total_population"),
                    func.max(Country.population).label("max_population"),
                    func.min(Country.population).label("min_population")
                )
                .group_by(Country.region)
                .subquery()
            )

            query = (
                select(
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

            results = await session.execute(query)

            for row in results:
                print(f"Region name: {row.region}")
                print(f"Total region population: {row.total_population:,}")
                print(f"Biggest country: {row.largest_name}")
                print(f"Biggest country population: {row.max_population:,}")
                print(f"Smallest country: {row.smallest_name}")
                print(f"Smallest country: {row.min_population:,}")
                print("")


if __name__ == "__main__":
    service = PrintDataService()
    asyncio.run(service.run())
