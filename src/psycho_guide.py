import csv
from dataclasses import asdict
from typing import TextIO

from src import config
from src._database import Database
from src._scraper import Scraper
from src.entities import Persona


class PsychoGuide:
    def __init__(self):
        self._db = Database(config.DB_PATH)
        self._db.load()
        self._scraper = Scraper(openai_key=config.OPENAI_API_KEY)

    async def scrape(self):
        await self._scraper.get_people_info(self._db)
        self._db.save()

    def write_csv(self, stream: TextIO):
        fieldnames = list(Persona.__dict__['__dataclass_fields__'].keys())
        writer = csv.DictWriter(stream, delimiter='\t', fieldnames=fieldnames)
        writer.writeheader()
        for persona in self._db.items():
            row = asdict(persona)
            publications = [f'{p.title},{p.year}' for p in persona.publications]
            row['publications'] = ';'.join(publications)
            writer.writerow(row)

    def get_statistics(self):
        return {'Count personas': len(self._db)}
