from functools import lru_cache
from pathlib import Path


@lru_cache
def env(env_path: Path) -> dict[str, str]:
    lines = [line for line in env_path.read_text().split('\n') if line.strip() != '']
    variables = {}
    for line in lines:
        [key, value] = line.split('=', maxsplit=2)
        variables[key.strip()] = value.strip()
    return variables
