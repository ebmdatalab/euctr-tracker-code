from pathlib import Path
from .config import *
from .config import SCRAPY_SETTINGS


CACHE_SETTINGS = {
    'HTTPCACHE_POLICY': 'scrapy.extensions.httpcache.DummyPolicy',
    'HTTPCACHE_ENABLED': True,
    'HTTPCACHE_DIR': Path(__file__).parent.parent / 'tests/fixtures'
}
SCRAPY_SETTINGS.update(CACHE_SETTINGS)
