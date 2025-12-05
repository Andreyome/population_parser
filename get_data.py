import os

import httpx
from bs4 import BeautifulSoup
from sqlalchemy.dialects.postgresql import insert
import asyncio

from database import SessionLocal, init_db
from models import Country


class CountryScraper:
    URL = os.environ.get("TARGET_URL")

    async def fetch(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(self.URL, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
            })
            response.raise_for_status()
            return response.text

    def parse(self, html):
        soup = BeautifulSoup(html, "lxml")

        table = soup.find("table", {"class": "wikitable"})
        if table is None:
            table = soup.find("tbody")
        countries = []
        for row in table.find_all("tr")[2:]:
            columns = row.find_all("td")
            name = columns[0].get_text(strip=True)
            region = columns[-1].get_text(strip=True)
            population = columns[1].get_text(strip=True).replace(",", "")

            if not population.isdigit():
                continue

            countries.append({
                "name": name.split("[")[0].strip(),
                "region": region,
                "population": int(population)
            })

        return countries


class GetDataService:
    def __init__(self, scraper):
        self.scraper = scraper

    async def run(self):
        await init_db()
        html = await self.scraper.fetch()
        data = self.scraper.parse(html)

        async with (SessionLocal() as session):
            for item in data:
                query = insert(Country).values(
                    name=item["name"],
                    region=item["region"],
                    population=item["population"]
                )
                query = query.on_conflict_do_update(
                    index_elements=["name"],
                    set_={"region": query.excluded.region, "population": query.excluded.population}
                )
                await session.execute(query)
            await session.commit()
            print("Data imported successfully.")


if __name__ == "__main__":
    scraper = CountryScraper()
    service = GetDataService(scraper)
    asyncio.run(service.run())
