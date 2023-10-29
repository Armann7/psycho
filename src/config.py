from pathlib import Path

from src._config_reader import env

ROOT_DIR = Path(__file__).parent.parent
ENV_PATH = Path().home() / '.secret/psycho.env'
DB_PATH = ROOT_DIR / '.db'
OPENAI_API_KEY = env(ENV_PATH)['OPENAI_API_KEY']
