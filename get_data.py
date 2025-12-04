import os

import requests
from bs4 import BeautifulSoup
from sqlalchemy.dialects.postgresql import insert

from database import SessionLocal, init_db
from models import Country
from wait_for_db import wait_for_db


class CountryScraper:
    URL = os.environ.get("TARGET_URL")

    def fetch(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
        }
        response = requests.get(self.URL, headers=headers)
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
    def __init__(self):
        init_db()
        self.scraper = CountryScraper()

    def run(self):
        html = self.scraper.fetch()
        data = self.scraper.parse(html)

        session = SessionLocal()
        try:
            for item in data:
                query = insert(Country).values(
                    name=item["name"],
                    region=item["region"],
                    population=item["population"]
                )
                query = query.on_conflict_do_update(
                    index_elements=["name"],
                    set_={
                        "population": query.excluded.population
                    }
                )
                session.execute(query)
            session.commit()
            print("Data imported successfully.")
        finally:
            session.close()


if __name__ == "__main__":
    wait_for_db()
    GetDataService().run()
