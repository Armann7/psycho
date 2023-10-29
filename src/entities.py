from dataclasses import dataclass
from dataclasses import field
from datetime import date


@dataclass
class Persona:
    name: str
    url: str
    title: str = None
    born: date = None
    died: date = None
    publications: list['Publication'] = field(default_factory=list)

    def merge(self, other: 'Persona'):
        if not self.url:
            self.url = other.url
        if not self.title:
            self.title = other.title
        if not self.born:
            self.born = other.born
        if not self.died:
            self.died = other.died
        for pub_other in other.publications:
            for pub in self.publications:
                if _is_equal_str(pub_other.title, pub.title):
                    break
            else:
                self.publications.append(pub_other)

    @classmethod
    def from_dict(cls, data: dict) -> 'Persona':
        publications = []
        for pub in data.get('publications', []):
            publications.append(Publication(title=pub['title'], year=pub.get('year', '')))

        born = data.get('born')
        try:
            born = date.fromisoformat(born) if born else None
        except ValueError:
            born = None
        died = data.get('died')
        try:
            died = date.fromisoformat(died) if died else None
        except ValueError:
            died = None
        return cls(
            name=data.get('name'),
            url=data.get('url'),
            title=data.get('title'),
            born=born,
            died=died,
            publications=publications,
            )

    def is_exhaustively(self) -> bool:
        if self.title is None or self.born is None or self.died is None or not self.publications:
            return False
        else:
            return True


@dataclass
class Publication:
    title: str
    year: str


def _is_equal_str(s1: str, s2: str) -> bool:
    spec_chars = r''',./?'";:][{}!@#$%^&*()+=`~'''
    table = str.maketrans(spec_chars, ' ' * len(spec_chars))
    return s1.translate(table).replace(' ', '').lower() == s2.translate(table).replace(' ', '').lower()


def test_data():
    p1 = Persona('Binet, Alfred', 'https://www.britannica.com/biography/Alfred-Binet', 'French psychologist')
    p2 = Persona('Binet, Alfred', 'https://www.britannica.com/biography/Alfred-Binet', 'French psychologist')
    assert p1 == p2
