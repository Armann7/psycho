import json
import logging
from json import JSONDecodeError
from typing import Mapping
from urllib.parse import urlparse

import aiohttp
from bs4 import BeautifulSoup
from openai import OpenAI

from src._database import Database
from src.entities import Persona


class Scraper:
    def __init__(self, openai_key: str):
        self._openai = OpenAI(api_key=openai_key)

    async def get_people_info(self, db: Database):
        personas = []
        # Scrape from britannica
        for page in range(1, 99):
            url = f'https://www.britannica.com/browse/Psychology-Mental-Health/{page}'
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 404:
                        break
                    if resp.status < 200 or resp.status >= 300:
                        _logger.error(f'Failed to get {url}')
                        continue
                    html_page = await resp.content.read()
            soup = BeautifulSoup(html_page, "lxml")
            elements = soup.find_all('invertedtitle')
            url_parts = urlparse(url)
            for e in elements:
                if e.string and e.string[0].isupper() and ',' in e.string:
                    name_parts = [word.strip() for word in e.string.split(',')]
                    name = ' '.join(name_parts[::-1])
                    person = Persona(name=name, url=f'{url_parts.scheme}://{url_parts.netloc}{e.parent.attrs["href"]}')
                    personas.append(person)
                else:
                    _logger.warning(f'{e.string!r} seems is not a name')
        # Select exhaustively existing ones
        to_update = []
        for person in personas:
            exist_person = db[person]
            if exist_person:
                person.merge(exist_person)
            else:
                db.append([person])
            if not person.is_exhaustively():
                to_update.append(person)
        # Enrich with ChatGPT
        names = []
        enriched_data = []
        for p in to_update:
            names.append(p.name)
            if len(names) >= 10:
                enriched_data.extend(self._ask_chatgpt(names))
                names = []
        else:
            enriched_data.extend(self._ask_chatgpt(names))
        for scientist in enriched_data:
            p = Persona.from_dict(scientist)
            exist_person = db[p]
            if exist_person is None:
                _logger.warning(f'ChatGPT get data for {p.name}, but it does not exist in the Database')
                continue
            exist_person.merge(p)

    def _ask_chatgpt(self, names: list[str]) -> Mapping:
        names = [f' - {n}' for n in names]
        parts = [
            "Write an information about these scientists:",
            *names,
            "Prepare the information as an json file with fields below.",
            "The main array in json should be named 'scientists'.",
            "Fields:",
            "- 'name' - name and surname",
            "- 'title' - specialization",
            "- 'born' - date of birth in ISO format",
            "- 'died' - date of death in ISO format",
            "- 'publications' - list of publications, every with fields:",
            "    - 'title' - title",
            "    - 'year' - year of release",
        ]
        prompt = "\n".join(parts)
        response = self._openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
        )
        left_bracket = response.choices[0].message.content.find('{')
        right_bracket = response.choices[0].message.content.rfind('}')
        try:
            content = json.loads(response.choices[0].message.content[left_bracket:right_bracket + 1])
        except JSONDecodeError:
            _logger.error('Failed to parse ChatGPT response:\n%s', response.choices[0].message.content)
            raise
        _logger.debug('ChatGPT response:\n%r', json.dumps(content, indent=4))
        return content['scientists']


_logger = logging.getLogger(__name__)
