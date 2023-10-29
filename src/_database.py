import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any
from typing import Iterable
from typing import Mapping
from typing import Optional
from typing import Union

from src.entities import Persona
from src.entities import Publication


class Database:
    def __init__(self, db_path: Path):
        self._path = db_path
        self._data: dict[str, Persona] = {}

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, key: Union[str, Persona]) -> Optional[Persona]:
        if isinstance(key, Persona):
            return self._data.get(_gen_key(key))
        elif isinstance(key, str):
            return self._data.get(key)
        raise TypeError(f'Unsupported type {type(key)}')

    def items(self):
        return self._data.values()

    def load(self):
        personas = []
        for file in self._path.glob('*.json'):
            pers = _load_from_dict(json.loads(file.read_text(encoding='utf8')))
            personas.append(pers)
        self._data.update({_gen_key(pers): pers for pers in personas})

    def save(self):
        for file in self._path.glob('*.json'):
            file.unlink()
        for key, pers in self._data.items():
            file = self._path / f'{key}.json'
            file.write_text(
                json.dumps(asdict(pers), ensure_ascii=False, default=_convert_non_serializable, indent=4),
                encoding='utf8',
            )

    def append(self, data: Iterable[Union[Persona, Mapping]]):
        personas = []
        for pers in data:
            if isinstance(pers, dict):
                pers = _load_from_dict(pers)
            personas.append(pers)
        self._data.update({_gen_key(pers): pers for pers in personas})


def _gen_key(persona: Persona) -> str:
    illegal_symbols = r''',./?'";:][{}!@#$%^&*()+=`~'''
    trans_table = str.maketrans(illegal_symbols, ' ' * len(illegal_symbols))
    key = persona.name.translate(trans_table).replace(' ', '').lower()
    return key


def _load_from_dict(data: Mapping[str, Any]) -> Persona:
    data = dict(data)
    if isinstance(data['born'], str):
        data['born'] = _decode_date(data['born']) if data['born'] else None
    if isinstance(data['died'], str):
        data['died'] = _decode_date(data['died']) if data['died'] else None
    publications = []
    for pub in data.get('publications', []):
        publications.append(Publication(**pub))
    return Persona(
        name=data['name'],
        url=data['url'],
        title=data['title'],
        born=data['born'],
        died=data['died'],
        publications=publications,
    )


def _convert_non_serializable(data: Any) -> str:
    if isinstance(data, datetime):
        return data.isoformat()
    else:
        return str(data)


def _decode_date(date_str: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        return None
