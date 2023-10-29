from pathlib import Path

from src._database import Database
from tests.data import personas


def test_db(tmp_path: Path):
    db_path = tmp_path / '.db'
    db_path.mkdir(exist_ok=True)
    db = Database(db_path)
    db.append(personas)
    db.save()
    db2 = Database(db_path)
    db2.load()
    assert db.items() == db2.items()
